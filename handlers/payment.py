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


def _normalize_lang(lang: str) -> str:
    lang = (lang or "en").lower()
    if lang.startswith("uk") or lang.startswith("ua"):
        return "ua"
    if lang.startswith("ru"):
        return "ru"
    return "en"


def _plan_name(plan: dict, lang: str) -> str:
    if lang == "ua":
        return plan["plan_name_ua"]
    if lang == "ru":
        return plan["plan_name_ru"]
    return plan.get("plan_name_en") or plan["plan_name_ru"]


def _usdt_menu_text(lang: str) -> str:
    if lang == "ua":
        return "💸 Обери USDT тариф:"
    if lang == "ru":
        return "💸 Выбери USDT тариф:"
    return "💸 Choose a USDT plan:"


def _unknown_plan_text(lang: str) -> str:
    if lang == "ua":
        return "Невідомий тариф."
    if lang == "ru":
        return "Неизвестный тариф."
    return "Unknown plan."


def _promo_already_used_text(lang: str) -> str:
    if lang == "ua":
        return "Акційна ціна вже використана. Доступні лише повні тарифи."
    if lang == "ru":
        return "Акционная цена уже использована. Доступны только полные тарифы."
    return "The promo price has already been used. Only full-price plans are available."


def _cancel_payment_text(lang: str) -> str:
    if lang == "ua":
        return "❌ Оплату скасовано. Тепер можеш надсилати скріни ставок."
    if lang == "ru":
        return "❌ Оплата отменена. Теперь можешь отправлять скрины ставок."
    return "❌ Payment cancelled. You can now send bet screenshots."


def _payment_card_text(lang: str, plan_name: str, amount_usd: float, wallet: str, promo_hint: str) -> str:
    if lang == "ua":
        return (
            f"💸 Тариф: {plan_name}\n"
            f"Сума: {amount_usd}$\n"
            f"Мережа: TRC20\n"
            f"Гаманець: `{wallet}`{promo_hint}\n\n"
            "Надішли скрін оплати у цей чат, а потім натисни кнопку нижче."
        )
    if lang == "ru":
        return (
            f"💸 Тариф: {plan_name}\n"
            f"Сумма: {amount_usd}$\n"
            f"Сеть: TRC20\n"
            f"Кошелек: `{wallet}`{promo_hint}\n\n"
            "Отправь скрин оплаты в этот чат, а затем нажми кнопку ниже."
        )
    return (
        f"💸 Plan: {plan_name}\n"
        f"Amount: ${amount_usd}\n"
        f"Network: TRC20\n"
        f"Wallet: `{wallet}`{promo_hint}\n\n"
        "Send the payment screenshot to this chat, then press the button below."
    )


def _promo_hint_text(lang: str, full_price: float, promo_price: float) -> str:
    if full_price <= promo_price:
        return ""
    if lang == "ua":
        return f"\n🔥 Акційна ціна: {full_price}$ → {promo_price}$"
    if lang == "ru":
        return f"\n🔥 Акционная цена: {full_price}$ → {promo_price}$"
    return f"\n🔥 Promo price: ${full_price} → ${promo_price}"


def _choose_plan_first_text(lang: str) -> str:
    if lang == "ua":
        return "Спочатку обери тариф."
    if lang == "ru":
        return "Сначала выбери тариф."
    return "Choose a plan first."


def _already_submitted_text(lang: str) -> str:
    if lang == "ua":
        return "Ти вже надіслав заявку адміну. Очікуй промокод або натисни /start."
    if lang == "ru":
        return "Ты уже отправил заявку админу. Ожидай промокод или нажми /start."
    return "You have already submitted the request to the admin. Wait for the promo code or press /start."


def _screenshot_already_saved_text(lang: str) -> str:
    if lang == "ua":
        return "⚠️ Скрін оплати вже збережено.\nНатисни «Я оплатив» або «Скасувати»."
    if lang == "ru":
        return "⚠️ Скрин оплаты уже сохранён.\nНажми «Я оплатил» или «Отменить»."
    return "⚠️ The payment screenshot has already been saved.\nPress “I paid” or “Cancel”."


def _screenshot_saved_text(lang: str) -> str:
    if lang == "ua":
        return "✅ Скрін збережено. Тепер натисни «Я оплатив»."
    if lang == "ru":
        return "✅ Скрин сохранён. Теперь нажми «Я оплатил»."
    return "✅ Screenshot saved. Now press “I paid”."


def _send_screenshot_first_text(lang: str) -> str:
    if lang == "ua":
        return "Спочатку надішли скрін оплати."
    if lang == "ru":
        return "Сначала отправь скрин оплаты."
    return "Send the payment screenshot first."


def _already_sent_to_admin_text(lang: str) -> str:
    if lang == "ua":
        return "✅ Заявку вже відправлено адміну. Очікуй промокод."
    if lang == "ru":
        return "✅ Заявка уже отправлена администратору. Ожидай промокод."
    return "✅ The request has already been sent to the admin. Wait for the promo code."


def _admin_caption_text(payment: dict) -> str:
    return (
        f"💸 New USDT request\n\n"
        f"user_id: {payment['user_id']}\n"
        f"Plan: {payment['plan_name']}\n"
        f"Amount: {payment['amount_usd']}$\n"
        f"payment_id: {payment['id']}\n\n"
        f"Reply to this message with a promo code — the bot will forward it to the user."
    )


def _request_sent_text(lang: str) -> str:
    if lang == "ua":
        return "✅ Заявку відправлено адміну. Очікуй промокод."
    if lang == "ru":
        return "✅ Заявка отправлена администратору. Ожидай промокод."
    return "✅ The request has been sent to the admin. Wait for the promo code."


def _promo_to_user_text(lang: str, promo: str) -> str:
    if lang == "ua":
        return f"🎁 Твій промокод: {promo}"
    if lang == "ru":
        return f"🎁 Твой промокод: {promo}"
    return f"🎁 Your promo code: {promo}"


async def payment_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    user = get_user(user_id)
    lang = _normalize_lang(user["lang"] if user and user.get("lang") else "en")
    promo_available = not has_used_promo_offer(user_id)

    if query.data == "buy_usdt":
        await query.message.reply_text(
            _usdt_menu_text(lang),
            reply_markup=usdt_plans_keyboard(lang, promo_available=promo_available)
        )
        return ConversationHandler.END

    if query.data == "cancel_payment":
        await query.message.reply_text(_cancel_payment_text(lang))
        return ConversationHandler.END

    plan = get_usdt_plan(query.data)
    if not plan:
        await query.message.reply_text(_unknown_plan_text(lang))
        return ConversationHandler.END

    if not promo_available and plan.get("is_promo"):
        await query.message.reply_text(_promo_already_used_text(lang))
        await query.message.reply_text(
            _usdt_menu_text(lang),
            reply_markup=usdt_plans_keyboard(lang, promo_available=False)
        )
        return ConversationHandler.END

    plan_name = _plan_name(plan, lang)

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
        promo_hint = _promo_hint_text(lang, plan["full_amount_usd"], plan["amount_usd"])

    await query.message.reply_text(
        _payment_card_text(lang, plan_name, plan["amount_usd"], plan["wallet_address"], promo_hint),
        reply_markup=payment_check_keyboard(lang),
        parse_mode="Markdown"
    )
    return WAITING_PAYMENT_SCREEN


async def handle_payment_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    payment = get_last_pending_payment(user_id)
    user = get_user(user_id)
    lang = _normalize_lang(user["lang"] if user and user.get("lang") else "en")

    if not payment:
        await update.message.reply_text(_choose_plan_first_text(lang))
        return WAITING_PAYMENT_SCREEN

    if payment.get("status") == "submitted":
        await update.message.reply_text(_already_submitted_text(lang))
        return ConversationHandler.END

    if payment.get("screenshot_file_id"):
        await update.message.reply_text(
            _screenshot_already_saved_text(lang),
            reply_markup=payment_check_keyboard(lang)
        )
        return WAITING_PAYMENT_SCREEN

    file_id = update.message.photo[-1].file_id
    set_payment_screenshot(payment["id"], file_id)

    await update.message.reply_text(
        _screenshot_saved_text(lang),
        reply_markup=payment_check_keyboard(lang)
    )
    return WAITING_PAYMENT_SCREEN


async def payment_sent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    payment = get_last_pending_payment(user_id)
    user = get_user(user_id)
    lang = _normalize_lang(user["lang"] if user and user.get("lang") else "en")

    if not payment or not payment.get("screenshot_file_id"):
        await query.message.reply_text(_send_screenshot_first_text(lang))
        return WAITING_PAYMENT_SCREEN

    if payment.get("status") == "submitted":
        await query.message.reply_text(_already_sent_to_admin_text(lang))
        return ConversationHandler.END

    mark_payment_submitted(payment["id"])

    sent = await context.bot.send_photo(
        chat_id=ADMIN_ID,
        photo=payment["screenshot_file_id"],
        caption=_admin_caption_text(payment)
    )

    set_payment_admin_message(payment["id"], sent.message_id)

    await query.message.reply_text(_request_sent_text(lang))
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
    target_lang = _normalize_lang(target_user["lang"] if target_user and target_user.get("lang") else "en")

    await context.bot.send_message(
        chat_id=payment["user_id"],
        text=_promo_to_user_text(target_lang, update.message.text)
    )

    mark_payment_promo_sent(payment_id, update.message.text)

    if payment.get("plan_key") in ("usdt_basic_month", "usdt_vip_month_promo"):
        mark_promo_offer_used(payment["user_id"])
