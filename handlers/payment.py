from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from config import ADMIN_ID
from db import (
    create_payment,
    get_last_pending_payment,
    set_payment_screenshot,
    mark_payment_submitted,
    set_payment_admin_message,
    get_payment_by_id,
    mark_payment_promo_sent,
    get_user,
    has_used_promo_offer,
    mark_promo_offer_used,
)
from keyboards import usdt_plans_keyboard, payment_check_keyboard
from services.payment_service import get_usdt_plan
from states import WAITING_PAYMENT_SCREEN


async def payment_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    user = get_user(user_id)
    lang = user["lang"] if user and user.get("lang") else "ua"
    promo_available = not has_used_promo_offer(user_id)

    if query.data == "buy_usdt":
        await query.message.reply_text(
            "💸 Обери USDT тариф:" if lang == "ua" else "💸 Выбери USDT тариф:",
            reply_markup=usdt_plans_keyboard(lang, promo_available=promo_available)
        )
        return ConversationHandler.END

    if query.data == "cancel_payment":
        await query.message.reply_text(
            "❌ Оплату скасовано. Тепер можеш надсилати скріни ставок."
            if lang == "ua" else
            "❌ Оплата отменена. Теперь можешь отправлять скрины ставок."
        )
        return ConversationHandler.END

    plan = get_usdt_plan(query.data)
    if not plan:
        await query.message.reply_text(
            "Невідомий тариф." if lang == "ua" else "Неизвестный тариф."
        )
        return ConversationHandler.END

    if not promo_available and plan.get("is_promo"):
        await query.message.reply_text(
            "Акційна ціна вже використана. Доступні лише повні тарифи."
            if lang == "ua" else
            "Акционная цена уже использована. Доступны только полные тарифы."
        )
        await query.message.reply_text(
            "💸 Обери USDT тариф:" if lang == "ua" else "💸 Выбери USDT тариф:",
            reply_markup=usdt_plans_keyboard(lang, promo_available=False)
        )
        return ConversationHandler.END

    plan_name = plan["plan_name_ua"] if lang == "ua" else plan["plan_name_ru"]

    create_payment(
        user_id=user_id,
        plan_key=query.data,
        plan_name=plan_name,
        plan_type=plan["plan_type"],
        duration_days=plan["duration_days"],
        amount_usd=plan["amount_usd"],
        wallet_address=plan["wallet_address"],
    )

    promo_hint = ""
    if plan.get("is_promo") and plan["full_amount_usd"] > plan["amount_usd"]:
        promo_hint = (
            f"\n🔥 Акційна ціна: {plan['full_amount_usd']}$ → {plan['amount_usd']}$"
            if lang == "ua" else
            f"\n🔥 Акционная цена: {plan['full_amount_usd']}$ → {plan['amount_usd']}$"
        )

    text = (
        f"💸 Тариф: {plan_name}\n"
        f"Сума: {plan['amount_usd']}$\n"
        f"Мережа: TRC20\n"
        f"Гаманець: `{plan['wallet_address']}`{promo_hint}\n\n"
        f"Надішли скрін оплати у цей чат, а потім натисни кнопку нижче."
        if lang == "ua" else
        f"💸 Тариф: {plan_name}\n"
        f"Сумма: {plan['amount_usd']}$\n"
        f"Сеть: TRC20\n"
        f"Кошелек: `{plan['wallet_address']}`{promo_hint}\n\n"
        f"Отправь скрин оплаты в этот чат, а затем нажми кнопку ниже."
    )

    await query.message.reply_text(
        text,
        reply_markup=payment_check_keyboard(lang),
        parse_mode="Markdown"
    )
    return WAITING_PAYMENT_SCREEN


async def handle_payment_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    payment = get_last_pending_payment(user_id)
    user = get_user(user_id)
    lang = user["lang"] if user and user.get("lang") else "ua"

    if not payment:
        await update.message.reply_text(
            "Спочатку обери тариф." if lang == "ua" else "Сначала выбери тариф."
        )
        return WAITING_PAYMENT_SCREEN

    if payment.get("status") == "submitted":
        await update.message.reply_text(
            "Ти вже надіслав заявку адміну. Очікуй промокод або натисни /start."
            if lang == "ua" else
            "Ты уже отправил заявку админу. Ожидай промокод или нажми /start."
        )
        return ConversationHandler.END

    if payment.get("screenshot_file_id"):
        await update.message.reply_text(
            "⚠️ Скрін оплати вже збережено.\nНатисни «Я оплатив» або «Скасувати»."
            if lang == "ua" else
            "⚠️ Скрин оплаты уже сохранён.\nНажми «Я оплатил» или «Отменить».",
            reply_markup=payment_check_keyboard(lang)
        )
        return WAITING_PAYMENT_SCREEN

    file_id = update.message.photo[-1].file_id
    set_payment_screenshot(payment["id"], file_id)

    await update.message.reply_text(
        "✅ Скрін збережено. Тепер натисни «Я оплатив»."
        if lang == "ua" else
        "✅ Скрин сохранён. Теперь нажми «Я оплатил».",
        reply_markup=payment_check_keyboard(lang)
    )
    return WAITING_PAYMENT_SCREEN


async def payment_sent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    payment = get_last_pending_payment(user_id)
    user = get_user(user_id)
    lang = user["lang"] if user and user.get("lang") else "ua"

    if not payment or not payment.get("screenshot_file_id"):
        await query.message.reply_text(
            "Спочатку надішли скрін оплати." if lang == "ua" else "Сначала отправь скрин оплаты."
        )
        return WAITING_PAYMENT_SCREEN

    if payment.get("status") == "submitted":
        await query.message.reply_text(
            "✅ Заявку вже відправлено адміну. Очікуй промокод."
            if lang == "ua" else
            "✅ Заявка уже отправлена администратору. Ожидай промокод."
        )
        return ConversationHandler.END

    mark_payment_submitted(payment["id"])

    caption = (
        f"💸 Нова USDT заявка\n\n"
        f"user_id: {payment['user_id']}\n"
        f"Тариф: {payment['plan_name']}\n"
        f"Сума: {payment['amount_usd']}$\n"
        f"payment_id: {payment['id']}\n\n"
        f"Відповідай на це повідомлення промокодом — бот перешле його користувачу."
        if lang == "ua" else
        f"💸 Новая USDT заявка\n\n"
        f"user_id: {payment['user_id']}\n"
        f"Тариф: {payment['plan_name']}\n"
        f"Сумма: {payment['amount_usd']}$\n"
        f"payment_id: {payment['id']}\n\n"
        f"Ответь на это сообщение промокодом — бот перешлёт его пользователю."
    )

    sent = await context.bot.send_photo(
        chat_id=ADMIN_ID,
        photo=payment["screenshot_file_id"],
        caption=caption
    )

    set_payment_admin_message(payment["id"], sent.message_id)

    await query.message.reply_text(
        "✅ Заявку відправлено адміну. Очікуй промокод."
        if lang == "ua" else
        "✅ Заявка отправлена администратору. Ожидай промокод."
    )
    return ConversationHandler.END


async def admin_payment_reply_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.reply_to_message or not update.message.text:
        return

    if update.effective_user.id != ADMIN_ID:
        return

    reply_to = update.message.reply_to_message
    caption = reply_to.caption or ""

    payment_id = None
    for line in caption.splitlines():
        if "payment_id:" in line:
            try:
                payment_id = int(line.split("payment_id:")[1].strip())
            except Exception:
                payment_id = None
            break

    if not payment_id:
        return

    payment = get_payment_by_id(payment_id)
    if not payment:
        return

    target_user = get_user(payment["user_id"])
    target_lang = target_user["lang"] if target_user and target_user.get("lang") else "ua"

    await context.bot.send_message(
        chat_id=payment["user_id"],
        text=(
            f"🎁 Твій промокод: {update.message.text}"
            if target_lang == "ua"
            else f"🎁 Твой промокод: {update.message.text}"
        )
    )

    mark_payment_promo_sent(payment_id, update.message.text)

    if payment.get("plan_key") in ("usdt_basic_month", "usdt_vip_month_promo"):
        mark_promo_offer_used(payment["user_id"])
