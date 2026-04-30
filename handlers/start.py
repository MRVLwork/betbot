# -*- coding: utf-8 -*-
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from keyboards import main_menu_keyboard, welcome_offer_keyboard, access_keyboard
from db import (
    create_user_if_not_exists,
    get_user,
    is_onboarding_completed,
    user_has_access,
    is_trial_available,
    get_trial_remaining,
    start_trial_mode,
    has_used_promo_offer,
)
from handlers.onboarding import start_onboarding


def _normalize_lang(lang: str) -> str:
    lang = (lang or "en").lower()
    if lang.startswith("uk") or lang.startswith("ua"):
        return "ua"
    if lang.startswith("ru"):
        return "ru"
    return "en"


def _welcome_text(lang: str, promo_available: bool) -> str:
    lang = _normalize_lang(lang)

    if lang == "ua":
        return (
            "😤 Ти зараз в мінусі чи в плюсі?\n\n"
            "Більшість беттерів думають що в плюсі.\n"
            "Реальна статистика показує інше.\n\n"
            "Bet Tracker Bot аналізує твої ставки і показує:\n"
            " Коли ти ставиш на тілті  і скільки це коштує\n"
            " Які типи ставок реально дають плюс\n"
            " Твій чесний ROI без самообману\n\n"
            "Надішли перший скрін \n"
            "і за 30 секунд побачиш реальну картину.\n\n"
            "🎁 7 днів безкоштовно 👇"
        )

    if lang == "ru":
        return (
            "😤 Ты сейчас в минусе или в плюсе?\n\n"
            "Большинство беттеров думают что в плюсе.\n"
            "Реальная статистика показывает другое.\n\n"
            "Bet Tracker Bot анализирует твои ставки и показывает:\n"
            " Когда ты ставишь на тилте  и сколько это стоит\n"
            " Какие типы ставок реально дают плюс\n"
            " Твой честный ROI без самообмана\n\n"
            "Отправь первый скрин \n"
            "и за 30 секунд увидишь реальную картину.\n\n"
            "🎁 7 дней бесплатно 👇"
        )

    return (
        "😤 Are you currently in profit or loss?\n\n"
        "Most bettors think they're in profit.\n"
        "Real stats show something different.\n\n"
        "Bet Tracker Bot analyzes your bets and shows:\n"
        " When you bet on tilt  and what it costs you\n"
        " Which bet types actually make profit\n"
        " Your honest ROI without self-deception\n\n"
        "Send your first screenshot \n"
        "and see the real picture in 30 seconds.\n\n"
        "🎁 7 days free 👇"
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    create_user_if_not_exists(user)

    if context.args:
        payload = context.args[0]
        if payload.startswith("ref_") and len(payload) > 4:
            source_key = payload[4:].lower()
            clean_key = source_key.replace("_", "").replace("-", "")
            if clean_key.isascii() and clean_key.isalnum():
                from db import increment_referral_clicks, set_user_ref_source

                increment_referral_clicks(source_key)
                set_user_ref_source(user.id, source_key)

    db_user = get_user(user.id)
    lang = _normalize_lang((db_user or {}).get("lang", "en"))

    if not is_onboarding_completed(user.id):
        return await start_onboarding(update, context)

    await send_standard_start(update, lang)
    return ConversationHandler.END


async def send_standard_start(update: Update, lang: str):
    user = update.effective_user

    if user_has_access(user.id):
        active_text = {
            "ua": "✔ Доступ активний.",
            "ru": "✔ Доступ активен.",
            "en": "✔ Access is active.",
        }[lang]

        await update.message.reply_text(
            active_text,
            reply_markup=main_menu_keyboard(lang, (db_user or {}).get("plan", "basic"))
        )
        return

    promo_available = not has_used_promo_offer(user.id)

    await update.message.reply_text(
        _welcome_text(lang, promo_available),
        reply_markup=welcome_offer_keyboard(lang)
    )


async def start_offer_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    tg_user = update.effective_user
    create_user_if_not_exists(tg_user)

    user = get_user(tg_user.id)
    lang = _normalize_lang((user or {}).get("lang", "en"))

    if user_has_access(tg_user.id):
        active_text = {
            "ua": "✔ Доступ активний.",
            "ru": "✔ Доступ активен.",
            "en": "✔ Access is active.",
        }[lang]

        await query.message.reply_text(
            active_text,
            reply_markup=main_menu_keyboard(lang, (user or {}).get("plan", "basic"))
        )
        return

    if query.data == "try_trial":
        if is_trial_available(tg_user.id):
            start_trial_mode(tg_user.id)

            trial_text = {
                "ua": (
                    "🚀 Пробний доступ активовано!\n\n"
                    "У тебе є 7 днів і аналіз 5 ставок на день.\n"
                    "Надішли перший скрін ставки 👇"
                ),
                "ru": (
                    "🚀 Пробный доступ активирован!\n\n"
                    "У тебя есть 7 дней и анализ 5 ставок в день.\n"
                    "Отправь первый скрин ставки 👇"
                ),
                "en": (
                    "🚀 Trial access activated!\n\n"
                    "You have 7 days and 5 screenshots per day.\n"
                    "Send your first bet screenshot 👇"
                ),
            }[lang]

            await query.message.reply_text(
                trial_text,
                reply_markup=main_menu_keyboard(lang, (user or {}).get("plan", "basic"))
            )
        else:
            remaining = get_trial_remaining(tg_user.id)

            limit_text = {
                "ua": f"❌ Пробний доступ вже використано. Залишилось: {remaining}",
                "ru": f"❌ Пробный доступ уже использован. Осталось: {remaining}",
                "en": f"❌ Trial access has already been used. Remaining: {remaining}",
            }[lang]

            await query.message.reply_text(limit_text)

    elif query.data == "pay_now":
        buy_text = {
            "ua": (
                "💳 Обери тариф:\n\n"
                "🔹 Basic 1 місяць  $5\n"
                "Аналіз 15 ставок на день\n"
                " Повна статистика і аналітика\n\n"
                " VIP 1 місяць  $19.99\n"
                " 30 скрінів на день\n"
                " AI Тренер\n"
                " Всі функції без обмежень"
            ),
            "ru": (
                "💳 Выбери тариф:\n\n"
                "🔹 Basic 1 месяц  $5\n"
                "Анализ 15 ставок в день\n"
                " Полная статистика и аналитика\n\n"
                " VIP 1 месяц  $19.99\n"
                " 30 скринов в день\n"
                " AI Тренер\n"
                " Все функции без ограничений"
            ),
            "en": (
                "💳 Choose your plan:\n\n"
                "🔹 Basic 1 month  $5\n"
                " 15 screenshots per day\n"
                " Full statistics and analytics\n\n"
                " VIP 1 month  $19.99\n"
                " 30 screenshots per day\n"
                " AI Coach\n"
                " All features unlimited"
            ),
        }[lang]

        await query.message.reply_text(
            buy_text,
            reply_markup=access_keyboard(lang)
        )
