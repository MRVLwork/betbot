from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from db import validate_promo, activate_user_by_promo, get_user
from keyboards import access_keyboard, main_menu_keyboard
from languages import get_text
from states import WAITING_PROMO


async def access_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    user = get_user(user_id)
    lang = user["lang"] or "ua"

    if query.data == "enter_promo":
        await query.message.reply_text(get_text(lang, "enter_promo_hint"))
        return WAITING_PROMO

    if query.data == "back_to_access":
        await query.message.reply_text(
            get_text(lang, "choose_access_option"),
            reply_markup=access_keyboard(lang)
        )
        return ConversationHandler.END

    return ConversationHandler.END


async def promo_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = get_user(user_id)
    lang = user["lang"] or "ua"

    code = update.message.text.strip()
    promo = validate_promo(code)

    if not promo:
        await update.message.reply_text(get_text(lang, "promo_not_found"))
        return ConversationHandler.END

    activate_user_by_promo(
        user_id=user_id,
        promo_code=promo["code"],
        days=promo["days"],
        plan_type=promo["plan_type"]
    )

    updated_user = get_user(user_id)
    updated_lang = updated_user["lang"] or lang
    plan = (updated_user["plan"] or promo["plan_type"]).upper()

    await update.message.reply_text(
        get_text(updated_lang, "promo_activated").format(
            plan=plan,
            days=promo["days"]
        ),
        reply_markup=main_menu_keyboard(updated_lang)
    )

    return ConversationHandler.END


async def cancel_promo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = get_user(user_id)
    lang = user["lang"] or "ua"

    await update.message.reply_text(get_text(lang, "promo_cancelled"))
    return ConversationHandler.END