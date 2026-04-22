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
            "😤 Зливаєш гроші на ставках?\n\n"
            "Bet Tracker Bot аналізує твої ставки і показує:\n"
            " Де ти зливаєш найбільше\n"
            " Коли ставиш на емоціях\n"
            " Твій реальний ROI і winrate\n\n"
            "📊 1,847 беттерів вже контролюють свої ставки\n\n"
            "🎁 Спробуй 7 днів безкоштовно 👇"
        )

    if lang == "ru":
        return (
            "😤 Сливаешь деньги на ставках?\n\n"
            "Bet Tracker Bot анализирует твои ставки и показывает:\n"
            " Где ты теряешь больше всего\n"
            " Когда ставишь на эмоциях\n"
            " Твой реальный ROI и winrate\n\n"
            "📊 1,847 беттеров уже контролируют свои ставки\n\n"
            "🎁 Попробуй 7 дней бесплатно 👇"
        )

    return (
        "😤 Losing money on bets?\n\n"
        "Bet Tracker Bot analyzes your bets and shows:\n"
        " Where you lose the most\n"
        " When you bet on emotions\n"
        " Your real ROI and winrate\n\n"
        "📊 1,847 bettors already track their stats\n\n"
        "🎁 Try free for 7 days 👇"
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    create_user_if_not_exists(user)

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
                    "У тебе є 7 днів і 5 скрінів на день.\n"
                    "Надішли перший скрін ставки 👇"
                ),
                "ru": (
                    "🚀 Пробный доступ активирован!\n\n"
                    "У тебя есть 7 дней и 5 скринов в день.\n"
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
                " 15 скрінів на день\n"
                " Повна статистика\n"
                " Аналітика\n\n"
                " VIP 1 місяць  $19.99\n"
                " 30 скрінів на день\n"
                " AI Тренер\n"
                " Всі функції без обмежень"
            ),
            "ru": (
                "💳 Выбери тариф:\n\n"
                "🔹 Basic 1 месяц  $5\n"
                " 15 скринов в день\n"
                " Полная статистика\n"
                " Аналитика\n\n"
                " VIP 1 месяц  $19.99\n"
                " 30 скринов в день\n"
                " AI Тренер\n"
                " Все функции без ограничений"
            ),
            "en": (
                "💳 Choose your plan:\n\n"
                "🔹 Basic 1 month  $5\n"
                " 15 screenshots per day\n"
                " Full statistics\n"
                " Analytics\n\n"
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


#def _welcome_text(lang: str, promo_available: bool) -> str:
#    if lang == "ru":
#       return (
#            "Привет 👋\n\n"
#           "Это Bet Tracker Bot — инструмент для анализа твоих ставок 📊\n\n"
#            "Что ты получишь:\n"
#            "• Статистику прибыли и убытков 💰\n"
#           "• ROI и винрейт 📈\n"
#            "• Средний коэффициент 🎯\n"
#            "• Аналитику по ставкам\n\n"
#            "🔥 Уже 1200+ пользователей\n"
#            "📊 Средний ROI: +11%\n\n"
#            "Инструкция @bets_academy_platform\n"
#            "👇 Попробуй сам"
#        )
#    else:
#        return (
#            "Привіт 👋\n\n"
#            "Це Bet Tracker Bot — інструмент для аналізу твоїх ставок 📊\n\n"
#            "Що ти отримаєш:\n"
#            "• Статистику прибутку та збитків 💰\n"
#            "• ROI і вінрейт 📈\n"
#            "• Середній коефіцієнт 🎯\n"
#            "• Аналітику по ставках\n\n"
#            "🔥 Вже 1200+ користувачів\n"
#            "📊 Середній ROI: +11%\n\n"
#            "Інструкція @bets_academy_platform\n"
#            "👇 Спробуй сам"
#        )
