from aiohttp import web
import logging

from config import WEBHOOK_SECRET
from db import activate_user_access, get_user
from services.cryptobot_service import parse_webhook_payload, verify_webhook_signature


logger = logging.getLogger(__name__)
_bot = None


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

        plan_config = {
            "usdt_basic_month": {"plan_type": "basic", "duration_days": 30, "min_amount": 4.9},
            "usdt_vip_month": {"plan_type": "vip", "duration_days": 30, "min_amount": 19.0},
            "usdt_vip_month_promo": {"plan_type": "vip", "duration_days": 30, "min_amount": 14.9},
        }.get(plan_key)

        if not plan_config:
            logger.error("Unknown plan_key: %s", plan_key)
            return web.Response(status=400, text="Unknown plan")

        if amount < plan_config["min_amount"]:
            logger.warning("Amount too low: %s for plan %s", amount, plan_key)
            return web.Response(status=400, text="Amount too low")

        activate_user_access(
            user_id=user_id,
            days=plan_config["duration_days"],
            plan_type=plan_config["plan_type"],
            source="cryptobot",
        )
        logger.info("Activated %s for user %s", plan_config["plan_type"], user_id)

        if _bot:
            user = get_user(user_id)
            lang = (user or {}).get("lang", "ua")
            messages = {
                "ua": (
                    f"✅ Оплата підтверджена!\n\n"
                    f"Твоя підписка активована.\n"
                    f"План: {plan_config['plan_type'].upper()}\n"
                    f"Термін: 30 днів\n\n"
                    f"Дякуємо! Починай відстежувати ставки 🎯"
                ),
                "ru": (
                    f"✅ Оплата подтверждена!\n\n"
                    f"Твоя подписка активирована.\n"
                    f"План: {plan_config['plan_type'].upper()}\n"
                    f"Срок: 30 дней\n\n"
                    f"Спасибо! Начинай отслеживать ставки 🎯"
                ),
                "en": (
                    f"✅ Payment confirmed!\n\n"
                    f"Your subscription is now active.\n"
                    f"Plan: {plan_config['plan_type'].upper()}\n"
                    f"Duration: 30 days\n\n"
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
