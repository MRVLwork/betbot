# -*- coding: utf-8 -*-
from aiohttp import web
import logging

from config import WEBHOOK_SECRET
from db import (
    activate_user_access,
    activate_vip_signals_access,
    grant_course_access,
    get_user,
    is_eligible_for_first_payment_promo,
    record_cryptobot_payment_once,
    subscribe_to_signal,
)
from services.cryptobot_service import parse_webhook_payload, verify_webhook_signature
from services.payment_service import USDT_PLANS
from handlers.admin_notify import notify_admin_activation_with_bot, notify_admin_course_purchase_with_bot


logger = logging.getLogger(__name__)
_bot = None


def _course_bundle(plan_type: str) -> str:
    return plan_type.replace("course_", "")


def _course_amount_label(plan_key: str) -> str:
    return {
        "course_solo": "$20",
        "course_tracker": "$21",
        "course_vip": "$25",
    }.get(plan_key, "")


def _course_success_text(plan_key: str) -> str:
    extra = ""
    if plan_key == "course_tracker":
        extra = "\nBasic активовано на 30 днів."
    elif plan_key == "course_vip":
        extra = "\nVIP активовано на 30 днів."
    return (
        "􀀀 Оплата пройшла! Доступ до курсу ColdMind відкрито назавжди.\n"
        "􀀀 Модуль 1 вже чекає: тисни Навчання в меню."
        f"{extra}"
    )


def set_bot(bot):
    global _bot
    _bot = bot


async def handle_cryptobot_webhook(request: web.Request):
    """
    Handle CryptoBot webhook on successful payment.
    URL: POST /webhook/cryptobot
    """
    try:
        body = await request.read()
        signature = request.headers.get("Crypto-Pay-API-Signature", "")

        if WEBHOOK_SECRET and request.headers.get("X-Webhook-Secret", "") not in ("", WEBHOOK_SECRET):
            logger.warning("Invalid webhook secret header")

        if not verify_webhook_signature(body, signature):
            logger.warning("Invalid webhook signature")
            return web.Response(status=401, text="Invalid signature")

        payload = parse_webhook_payload(body)
        if not payload.get("ok"):
            reason = payload.get("reason", "parse_error")
            if reason == "not_paid":
                return web.Response(status=200, text="OK")
            logger.error("Webhook parse error: %s", payload)
            return web.Response(status=400, text="Parse error")

        user_id = payload["user_id"]
        plan_key = payload["plan_key"]
        amount = payload["amount"]
        invoice_id = payload.get("invoice_id")

        plan_config = {
            "course_solo": {"plan_type": "course_solo", "duration_days": 0, "min_amount": 19.0},
            "course_tracker": {"plan_type": "course_tracker", "duration_days": 30, "min_amount": 20.0},
            "course_vip": {"plan_type": "course_vip", "duration_days": 30, "min_amount": 24.0},
            "tracker_1m_usd": {"plan_type": "tracker", "duration_days": 30, "min_amount": 6.9},
            "tracker_6m_usd": {"plan_type": "tracker", "duration_days": 180, "min_amount": 29.9},
            "usdt_signals_vip": {"plan_type": "signals_vip", "duration_days": 30, "min_amount": 19.0},
            "usdt_signals_elite": {"plan_type": "signals_elite", "duration_days": 30, "min_amount": 49.0},
            "usdt_basic_month": {"plan_type": "basic", "duration_days": 30, "min_amount": 6.9},
            "usdt_vip_month": {"plan_type": "vip", "duration_days": 30, "min_amount": 19.0},
            "usdt_basic_6m_promo": {"plan_type": "basic", "duration_days": 180, "min_amount": 29.9, "first_payment_only": True},
            "usdt_vip_3m_promo": {"plan_type": "vip", "duration_days": 90, "min_amount": 49.9, "first_payment_only": True},
            "usdt_vip_6m_promo": {"plan_type": "vip", "duration_days": 180, "min_amount": 89.0, "first_payment_only": True},
            "usdt_vip_signals_10d": {"plan_type": "vip_signals", "duration_days": 10, "min_amount": 4.9},
        }.get(plan_key)

        if not plan_config:
            logger.error("Unknown plan_key: %s", plan_key)
            return web.Response(status=400, text="Unknown plan")

        if amount < plan_config["min_amount"]:
            logger.warning("Amount too low: %s for plan %s", amount, plan_key)
            return web.Response(status=400, text="Amount too low")

        if plan_config.get("first_payment_only") and not is_eligible_for_first_payment_promo(user_id):
            logger.warning("First-payment promo denied for user %s plan %s", user_id, plan_key)
            return web.Response(status=400, text="Promo unavailable")

        plan = USDT_PLANS.get(plan_key) or {}
        plan_record = {**plan_config, **plan}
        if not record_cryptobot_payment_once(user_id, plan_key, plan_record, invoice_id):
            logger.info("CryptoBot invoice %s already processed for user %s", invoice_id, user_id)
            return web.Response(status=200, text="Already processed")

        if plan_config["plan_type"] in {"course_solo", "course_tracker", "course_vip"}:
            bundle = _course_bundle(plan_config["plan_type"])
            grant_course_access(user_id, bundle)
            if plan_config["plan_type"] == "course_tracker":
                activate_user_access(
                    user_id=user_id,
                    days=30,
                    plan_type="basic",
                    source="cryptobot_course",
                )
            elif plan_config["plan_type"] == "course_vip":
                activate_user_access(
                    user_id=user_id,
                    days=30,
                    plan_type="vip",
                    source="cryptobot_course",
                )

            await notify_admin_course_purchase_with_bot(
                _bot,
                user_id,
                bundle,
                _course_amount_label(plan_key),
                "USDT",
            )
            if _bot:
                try:
                    await _bot.send_message(chat_id=user_id, text=_course_success_text(plan_key))
                except Exception as exc:
                    logger.error("Failed to notify course user %s: %s", user_id, exc)
            logger.info("Recorded course %s payment for user %s", bundle, user_id)
            return web.Response(status=200, text="OK")

        if plan_config["plan_type"] in {"signals_vip", "signals_elite"}:
            channel_name = "VIP" if plan_config["plan_type"] == "signals_vip" else "ELITE"
            await notify_admin_activation_with_bot(
                _bot,
                user_id,
                f"{channel_name} Сигнали (додати в канал!)",
                "USDT",
            )
            if _bot:
                user = get_user(user_id)
                lang = (user or {}).get("lang", "ua")
                if str(lang).lower().startswith("ru"):
                    text = f"􀀀 Оплата успешна!\n\nСкоро админ добавит тебя в закрытый {channel_name} канал сигналов."
                elif str(lang).lower().startswith("en"):
                    text = f"􀀀 Payment successful!\n\nAdmin will add you to the private {channel_name} signals channel soon."
                else:
                    text = f"􀀀 Оплата успішна!\n\nСкоро адмін додасть тебе в закритий {channel_name} канал сигналів."
                try:
                    await _bot.send_message(chat_id=user_id, text=text)
                except Exception as exc:
                    logger.error("Failed to notify signals channel user %s: %s", user_id, exc)
            logger.info("Recorded %s channel payment for user %s", channel_name, user_id)
            return web.Response(status=200, text="OK")

        if plan_config["plan_type"] == "vip_signals":
            activate_vip_signals_access(user_id=user_id, days=plan_config["duration_days"])
            subscribe_to_signal(user_id, "vip", duration_days=plan_config["duration_days"])
        else:
            activate_user_access(
                user_id=user_id,
                days=plan_config["duration_days"],
                plan_type=plan_config["plan_type"],
                source="cryptobot",
            )
        plan_label = plan.get("plan_name_ua") or plan.get("plan_name_en") or plan_key
        await notify_admin_activation_with_bot(_bot, user_id, plan_label, "USDT")

        logger.info("Activated %s for user %s", plan_config["plan_type"], user_id)

        if _bot:
            user = get_user(user_id)
            lang = (user or {}).get("lang", "ua")
            messages = {
                "ua": (
                    f"✅ Оплата підтверджена!\n\n"
                    f"Твоя підписка активована.\n"
                    f"План: {plan_config['plan_type'].upper()}\n"
                    f"Термін: {plan_config['duration_days']} днів\n\n"
                    f"Дякуємо! Починай відстежувати ставки 🎯"
                ),
                "ru": (
                    f"✅ Оплата подтверждена!\n\n"
                    f"Твоя подписка активирована.\n"
                    f"План: {plan_config['plan_type'].upper()}\n"
                    f"Срок: {plan_config['duration_days']} дней\n\n"
                    f"Спасибо! Начинай отслеживать ставки 🎯"
                ),
                "en": (
                    f"✅ Payment confirmed!\n\n"
                    f"Your subscription is now active.\n"
                    f"Plan: {plan_config['plan_type'].upper()}\n"
                    f"Duration: {plan_config['duration_days']} days\n\n"
                    f"Thank you! Start tracking your bets 🎯"
                ),
            }
            try:
                from keyboards import main_menu_keyboard

                await _bot.send_message(
                    chat_id=user_id,
                    text=messages.get(lang, messages["en"]),
                    reply_markup=main_menu_keyboard(lang, plan_config["plan_type"]),
                )
            except Exception as exc:
                logger.error("Failed to notify user %s: %s", user_id, exc)

        return web.Response(status=200, text="OK")
    except Exception as exc:
        logger.error("Webhook error: %s", exc)
        return web.Response(status=500, text="Internal error")


async def handle_health(request: web.Request):
    """Health check endpoint."""
    return web.Response(text="OK")


def create_webhook_app() -> web.Application:
    """Create aiohttp app for webhook handling."""
    app = web.Application()
    app.router.add_post("/webhook/cryptobot", handle_cryptobot_webhook)
    app.router.add_get("/health", handle_health)
    return app
