# -*- coding: utf-8 -*-
from telegram import LabeledPrice, Update
from telegram.ext import ContextTypes

from db import (
    activate_user_access,
    save_star_payment,
    get_user,
    has_used_promo_offer,
    mark_promo_offer_used,
    activate_vip_bet_day_access,
)
from keyboards import stars_plans_keyboard
from services.stars_service import get_stars_plan


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
        return "Акційна ціна вже використана. Доступні лише повні тарифи."
    if lang == "ru":
        return "Акционная цена уже использована. Доступны только полные тарифы."
    return "The promo price has already been used. Only full-price plans are available."


def _plan_title(plan: dict, lang: str) -> str:
    if lang == "ua":
        return plan["title_ua"]
    if lang == "ru":
        return plan["title_ru"]
    return plan.get("title_en") or plan["title_ru"]


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


async def open_stars_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    user = get_user(user_id)
    lang = _normalize_lang(user["lang"] if user and user.get("lang") else "en")
    promo_available = not has_used_promo_offer(user_id)

    if query.data == "buy_stars":
        await query.message.reply_text(
            _stars_menu_text(lang),
            reply_markup=stars_plans_keyboard(lang, promo_available=promo_available)
        )
        return

    plan = get_stars_plan(query.data)
    if not plan:
        await query.message.reply_text(_unknown_plan_text(lang))
        return

    if not promo_available and plan.get("is_promo"):
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
        payload=query.data,
        provider_token="",
        currency="XTR",
        prices=[LabeledPrice(label=title, amount=amount_xtr)],
    )


async def precheckout_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.pre_checkout_query
    await query.answer(ok=True)


async def successful_payment_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    payment = update.message.successful_payment
    plan_key = payment.invoice_payload
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

    if plan_key == "stars_vip_bet_day_month":
        activate_vip_bet_day_access(user_id=user_id, days=plan["duration_days"])
    else:
        activate_user_access(
            user_id=user_id,
            days=plan["duration_days"],
            plan_type=plan["plan_type"],
            source=f"stars:{plan_key}",
        )

    if plan_key == "stars_vip_month_promo":
        mark_promo_offer_used(user_id)

    user = get_user(user_id)
    lang = _normalize_lang(user["lang"] if user and user.get("lang") else "en")

    await update.message.reply_text(_success_text(lang))
