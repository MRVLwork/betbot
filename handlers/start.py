from telegram import Update
from telegram.ext import ContextTypes

from keyboards import main_menu_keyboard, welcome_offer_keyboard
from db import (
    create_user_if_not_exists,
    get_user,
    user_has_access,
    is_trial_available,
    get_trial_remaining,
    get_trial_used_count,
    start_trial_mode,
    has_used_promo_offer,
)


def _welcome_text(lang: str, promo_available: bool) -> str:
    if lang == "ru":
        if promo_available:
            return "🎁 У тебя есть доступ к пробному периоду!"
        return "Добро пожаловать!"
    else:
        if promo_available:
            return "🎁 У тебе є доступ до пробного періоду!"
        return "Ласкаво просимо!"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    create_user_if_not_exists(user)

    db_user = get_user(user.id)
    lang = (db_user or {}).get("lang", "ua")

    if user_has_access(user.id):
        await update.message.reply_text(
            "✔ Доступ активний." if lang == "ua" else "✔ Доступ активен.",
            reply_markup=main_menu_keyboard(lang)
        )
        return

    promo_available = not has_used_promo_offer(user.id)

    await update.message.reply_text(
        _welcome_text(lang, promo_available),
        reply_markup=welcome_offer_keyboard(lang)
    )


async def start_offer_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_user = update.effective_user

    create_user_if_not_exists(tg_user)

    user = get_user(tg_user.id)
    lang = (user or {}).get("lang", "ua")

    if user_has_access(tg_user.id):
        await update.message.reply_text(
            "✔ Доступ активний." if lang == "ua" else "✔ Доступ активен.",
            reply_markup=main_menu_keyboard(lang)
        )
        return

    if is_trial_available(tg_user.id):
        start_trial_mode(tg_user.id)

        await update.message.reply_text(
            "🚀 Пробний доступ активовано!" if lang == "ua" else "🚀 Пробный доступ активирован!",
            reply_markup=main_menu_keyboard(lang)
        )
    else:
        remaining = get_trial_remaining(tg_user.id)

        await update.message.reply_text(
            f"❌ Пробний доступ вже використано. Залишилось: {remaining}"
            if lang == "ua"
            else f"❌ Пробный доступ уже использован. Осталось: {remaining}"
        )
