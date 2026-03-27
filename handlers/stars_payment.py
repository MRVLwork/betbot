from telegram import LabeledPrice, Update
from telegram.ext import ContextTypes

from db import (
    activate_user_access,
    save_star_payment,
    get_user,
    has_used_promo_offer,
    mark_promo_offer_used,
)
from keyboards import stars_plans_keyboard
from services.stars_service import get_stars_plan


async def open_stars_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    user = get_user(user_id)
    lang = user["lang"] if user and user.get("lang") else "ua"
    promo_available = not has_used_promo_offer(user_id)

    if query.data == "buy_stars":
        await query.message.reply_text(
            "⭐ Обери тариф Stars:" if lang == "ua" else "⭐ Выбери тариф Stars:",
            reply_markup=stars_plans_keyboard(lang, promo_available=promo_available)
        )
        return

    plan = get_stars_plan(query.data)
    if not plan:
        await query.message.reply_text(
            "Невідомий тариф." if lang == "ua" else "Неизвестный тариф."
        )
        return

    if not promo_available and plan.get("is_promo"):
        await query.message.reply_text(
            "Акційна ціна вже використана. Доступні лише повні тарифи."
            if lang == "ua" else
            "Акционная цена уже использована. Доступны только полные тарифы."
        )
        await query.message.reply_text(
            "⭐ Обери тариф Stars:" if lang == "ua" else "⭐ Выбери тариф Stars:",
            reply_markup=stars_plans_keyboard(lang, promo_available=False)
        )
        return

    title = plan["title_ua"] if lang == "ua" else plan["title_ru"]
    amount_xtr = plan["amount_xtr"]

    description = title
    if plan.get("is_promo") and plan["full_price_xtr"] > amount_xtr:
        description = (
            f"{title}\nАкційна ціна: {plan['full_price_xtr']} → {amount_xtr} ⭐"
            if lang == "ua"
            else f"{title}\nАкционная цена: {plan['full_price_xtr']} → {amount_xtr} ⭐"
        )

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
        title=plan["title_ua"],
        duration_days=plan["duration_days"],
        amount_xtr=plan["amount_xtr"],
        telegram_charge_id=payment.telegram_payment_charge_id,
        provider_charge_id=payment.provider_payment_charge_id,
    )

    activate_user_access(
        user_id=user_id,
        days=plan["duration_days"],
        plan_type=plan["plan_type"],
        source=f"stars:{plan_key}",
    )

    if plan.get("is_promo"):
        mark_promo_offer_used(user_id)

    user = get_user(user_id)
    lang = user["lang"] if user and user.get("lang") else "ua"

    await update.message.reply_text(
        "✅ Оплату отримано. Доступ активовано."
        if lang == "ua" else
        "✅ Оплата получена. Доступ активирован."
    )
