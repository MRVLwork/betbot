# -*- coding: utf-8 -*-
from telegram import LabeledPrice, Update
from telegram.ext import ContextTypes

from db import (
    activate_user_access,
    save_star_payment,
    get_user,
    mark_promo_offer_used,
    is_eligible_for_first_payment_promo,
    activate_vip_bet_day_access,
    activate_vip_signals_access,
    is_vip_week_199_offer_available,
    clear_vip_week_promo,
    mark_vip_week_message_sent,
    mark_vip_week_promo_started,
    record_referral_earning_from_stars,
    subscribe_to_signal,
)
from keyboards import stars_plans_keyboard
from services.stars_service import get_stars_plan
from handlers.admin_notify import notify_admin_activation


def _normalize_lang(lang: str) -> str:
    lang = (lang or "en").lower()
    if lang.startswith("uk") or lang.startswith("ua"):
        return "ua"
    if lang.startswith("ru"):
        return "ru"
    return "en"


def _stars_menu_text(lang: str) -> str:
    if lang == "ua":
        return "⭐ Обери тариф Stars:"
    if lang == "ru":
        return "⭐ Выбери тариф Stars:"
    return "⭐ Choose a Stars plan:"


def _unknown_plan_text(lang: str) -> str:
    if lang == "ua":
        return "Невідомий тариф."
    if lang == "ru":
        return "Неизвестный тариф."
    return "Unknown plan."


def _promo_used_text(lang: str) -> str:
    if lang == "ua":
        return "⭐ Ця акція доступна тільки при першій оплаті."
    if lang == "ru":
        return "⭐ Эта акция доступна только при первой оплате."
    return "⭐ This offer is available only for the first payment."


def _plan_title(plan: dict, lang: str) -> str:
    if lang == "ua":
        return plan.get("title_ua") or plan.get("title")
    if lang == "ru":
        return plan.get("title_ru") or plan.get("title")
    return plan.get("title_en") or plan.get("title_ru") or plan.get("title")


def _normalize_plan_key(plan_key: str) -> str:
    aliases = {
        "vip_buy_1m": "stars_vip_1m",
        "vip_buy_3m": "stars_vip_3m_promo",
        "vip_buy_6m": "stars_vip_6m_promo",
        "vip_buy_3m_promo": "stars_vip_3m_promo",
        "vip_buy_6m_promo": "stars_vip_6m_promo",
        "basic_buy_1m": "stars_basic_month",
        "basic_buy_6m_promo": "stars_basic_6m_promo",
    }
    return aliases.get(plan_key, plan_key)


def _description(plan: dict, title: str, lang: str) -> str:
    amount_xtr = plan["amount_xtr"]
    if plan.get("is_promo") and plan["full_price_xtr"] > amount_xtr:
        if lang == "ua":
            return f"{title}\nАкційна ціна: {plan['full_price_xtr']} → {amount_xtr} ⭐"
        if lang == "ru":
            return f"{title}\nАкционная цена: {plan['full_price_xtr']} → {amount_xtr} ⭐"
        return f"{title}\nPromo price: {plan['full_price_xtr']} → {amount_xtr} ⭐"
    return title


def _success_text(lang: str) -> str:
    if lang == "ua":
        return "✅ Оплату отримано. Доступ активовано."
    if lang == "ru":
        return "✅ Оплата получена. Доступ активирован."
    return "✅ Payment received. Access activated."


async def _notify_referral_earning(context: ContextTypes.DEFAULT_TYPE, earning: dict | None):
    if not earning:
        return
    referrer_id = int(earning["referrer_id"])
    earned = float(earning["earned_usd"])
    referrer = get_user(referrer_id) or {}
    lang = _normalize_lang(referrer.get("lang", "en"))
    text = {
        "ua": f"💰 Твій реферал оформив підписку. Нараховано ${earned:.2f}.",
        "ru": f"💰 Твой реферал оформил подписку. Начислено ${earned:.2f}.",
        "en": f"💰 Your referral bought a subscription. ${earned:.2f} credited.",
    }.get(lang, f"💰 Your referral bought a subscription. ${earned:.2f} credited.")
    try:
        await context.bot.send_message(chat_id=referrer_id, text=text)
    except Exception as exc:
        print(f"referral earning notification failed: {exc}")


async def open_stars_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    user = get_user(user_id)
    lang = _normalize_lang(user["lang"] if user and user.get("lang") else "en")
    promo_available = is_eligible_for_first_payment_promo(user_id)

    if query.data == "buy_stars":
        await query.message.reply_text(
            _stars_menu_text(lang),
            reply_markup=stars_plans_keyboard(lang, promo_available=promo_available)
        )
        return

    plan_key = _normalize_plan_key(query.data)
    plan = get_stars_plan(plan_key)
    if not plan:
        await query.message.reply_text(_unknown_plan_text(lang))
        return

    if plan_key == "stars_vip_week_199" and not is_vip_week_199_offer_available(user_id):
        await query.message.reply_text(
            {
                "ua": "⏳ Спец-ціна 199⭐ вже недоступна. Показую стандартний VIP.",
                "ru": "⏳ Спеццена 199⭐ уже недоступна. Показываю стандартный VIP.",
                "en": "⏳ The 199⭐ special price is no longer available. Showing standard VIP.",
            }.get(lang, "⏳ The 199⭐ special price is no longer available. Showing standard VIP.")
        )
        plan_key = "stars_vip_1m"
        plan = get_stars_plan(plan_key)

    if plan.get("first_payment_only") and not is_eligible_for_first_payment_promo(user_id):
        await query.message.reply_text(_promo_used_text(lang))
        await query.message.reply_text(
            _stars_menu_text(lang),
            reply_markup=stars_plans_keyboard(lang, promo_available=False)
        )
        return

    title = _plan_title(plan, lang)
    amount_xtr = plan["amount_xtr"]
    description = _description(plan, title, lang)

    await context.bot.send_invoice(
        chat_id=user_id,
        title=title,
        description=description,
        payload=plan_key,
        provider_token="",
        currency="XTR",
        prices=[LabeledPrice(label=title, amount=amount_xtr)],
    )


async def precheckout_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.pre_checkout_query
    await query.answer(ok=True)


async def successful_payment_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    payment = update.message.successful_payment
    plan_key = _normalize_plan_key(payment.invoice_payload)
    plan = get_stars_plan(plan_key)
    user_id = update.effective_user.id

    if not plan:
        return

    save_star_payment(
        user_id=user_id,
        plan_key=plan_key,
        plan_type=plan["plan_type"],
        title=plan.get("title_en") or plan["title_ua"],
        duration_days=plan["duration_days"],
        amount_xtr=plan["amount_xtr"],
        telegram_charge_id=payment.telegram_payment_charge_id,
        provider_charge_id=payment.provider_payment_charge_id,
    )
    await _notify_referral_earning(
        context,
        record_referral_earning_from_stars(user_id, int(plan["amount_xtr"] or 0)),
    )

    if plan_key == "stars_vip_bet_day_month":
        activate_vip_bet_day_access(user_id=user_id, days=plan["duration_days"])
    elif plan_key == "stars_vip_signals_10d":
        activate_vip_signals_access(user_id=user_id, days=plan["duration_days"])
        subscribe_to_signal(user_id, "vip", duration_days=plan["duration_days"])
    else:
        activate_user_access(
            user_id=user_id,
            days=plan["duration_days"],
            plan_type=plan["plan_type"],
            source=f"stars:{plan_key}",
        )
        if plan_key == "stars_vip_week_199":
            mark_vip_week_promo_started(user_id)
        elif plan_key in {"stars_vip_month", "stars_vip_1m", "stars_vip_winback_1299"} and plan.get("plan_type") == "vip":
            clear_vip_week_promo(user_id)

    if plan.get("first_payment_only"):
        mark_promo_offer_used(user_id)

    plan_label = plan.get("title_ua") or plan.get("title_en") or plan_key
    await notify_admin_activation(context, user_id, plan_label, "Stars")

    user = get_user(user_id)
    lang = _normalize_lang(user["lang"] if user and user.get("lang") else "en")

    await update.message.reply_text(_success_text(lang))

    if plan_key == "stars_vip_week_199" and mark_vip_week_message_sent(user_id, "welcome"):
        await update.message.reply_text(
            {
                "ua": "🧊 Тепер я в грі. Стежу за твоїм банком щодня.\nДодавай ставки — покажу, де ти зливаєш і де заробляєш.\nЗа цей тиждень зроблю з твоєї гри систему.",
                "ru": "🧊 Теперь я в игре. Слежу за твоим банком каждый день.\nДобавляй ставки — покажу, где ты сливаешь и где зарабатываешь.\nЗа эту неделю сделаю из твоей игры систему.",
                "en": "🧊 I am in the game now. Watching your bankroll every day.\nAdd bets — I will show where you leak and where you earn.\nThis week I will turn your game into a system.",
            }.get(lang, "🧊 I am in the game now. Watching your bankroll every day.\nAdd bets — I will show where you leak and where you earn.\nThis week I will turn your game into a system.")
        )
