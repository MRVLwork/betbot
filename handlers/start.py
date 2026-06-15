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
    is_eligible_for_first_payment_promo,
)
from handlers.onboarding import activate_trial_after_onboarding, start_onboarding


def _normalize_lang(lang: str) -> str:
    lang = (lang or "en").lower()
    if lang.startswith("uk") or lang.startswith("ua"):
        return "ua"
    if lang.startswith("ru"):
        return "ru"
    return "en"

"""
def _welcome_text(lang: str, promo_available: bool) -> str:
    return (
        "💰 Заробляй на ставках розумніше\n"
        "Bet Tracker об'єднує AI-аналітику та професійний облік ставок в одному місці.\n\n"
        "Що ти отримаєш:\n"
        "🔥 AI-сигнали дня \n" "Перспективні ставки, відібрані AI.\n"
        "📊 Повний контроль результатів ROI, Win Rate, прибуток та історія ставок.\n"
        "🎯 Пошук помилок Дізнайся, які ставки зливають твій банк.\n"
        "🤖 AI-аналітика Персональні висновки та рекомендації щодо твоєї гри.\n"
        "🏆 Менше емоцій  більше дисципліни Приймай рішення на основі статистики, а не відчуттів.\n\n"
        "🎁 Новим користувачам доступно:\n"
        "Безкоштовний trail\n"
        "👇 Обери дію:"
    )
"""
def _welcome_text(lang: str, promo_available: bool) -> str:
    return (
        "💰Заробляй на ставках розумніше\n"
        "Bet Tracker об'єднує AI-аналітику та професійний облік ставок в одному місці.\n"
        "📌Що ти отримаєш:\n"
        "🔥AI-сигнали дня\n"
        "Перспективні ставки, відібрані AI.\n"
        "📊Повний контроль результатів\n"
        "ROI, Win Rate, прибуток та історія ставок.\n"
        "🎯Пошук помилок\n"
        "Дізнайся, які ставки зливають твій банк.\n"
        "🤖AI-аналітика\n"
        "Персональні висновки та рекомендації щодо твоєї гри.\n"
        "🏆Менше емоцій — більше дисципліни\n"
        "Приймай рішення на основі статистики, а не відчуттів.\n"
        "━━━━━━━━━━━━━━\n\n"
        "🎁Для нових користувачів:\n"
        "✅ 3 дні безкоштовного доступу\n"
        "👇Обери дію:"
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

    await send_standard_start(update, lang)
    return ConversationHandler.END


async def send_standard_start(update: Update, lang: str):
    user = update.effective_user

    if user_has_access(user.id):
        db_user = get_user(user.id) or {}
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

    promo_available = is_eligible_for_first_payment_promo(user.id)

    await update.message.reply_text(
        _welcome_text(lang, promo_available),
        reply_markup=welcome_offer_keyboard(lang),
        parse_mode="Markdown",
    )


async def start_offer_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    tg_user = update.effective_user
    create_user_if_not_exists(tg_user)

    user = get_user(tg_user.id)
    lang = _normalize_lang((user or {}).get("lang", "en"))

    if query.data == "ai_signals_intro":
        ai_signals_text = (
            "🔥 AI-сигнали дня\n\n"
            "AI аналізує спортивні події та відбирає найперспективніші можливості.\n\n"
            "Для отримання повного доступу до сигналів потрібна активна підписка."
        )
        await query.message.reply_text(ai_signals_text)
        return ConversationHandler.END

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
        return ConversationHandler.END

    if query.data == "try_trial":
        if is_trial_available(tg_user.id):
            if is_onboarding_completed(tg_user.id):
                return await activate_trial_after_onboarding(update, context, lang)
            return await start_onboarding(update, context)
        else:
            remaining = get_trial_remaining(tg_user.id)

            limit_text = {
                "ua": f"❌ Пробний доступ вже використано. Залишилось: {remaining}",
                "ru": f"❌ Пробный доступ уже использован. Осталось: {remaining}",
                "en": f"❌ Trial access has already been used. Remaining: {remaining}",
            }[lang]

            await query.message.reply_text(limit_text)
            return ConversationHandler.END

    elif query.data == "pay_now":
        buy_text = {
            "ua": (
                "💰 Заробляй на ставках розумніше\n\n"
                "Обери тариф:\n\n"
                "🔹 Basic 1 місяць  $7\n"
                "🔥 AI Прогнози дня\n"
                "Аналіз 15 ставок на день\n"
                " Повна статистика і аналітика\n\n"
                " VIP 1 місяць  $19.99\n"
                "🔥 AI Прогнози Basic + VIP\n"
                " 30 скрінів на день\n"
                " AI Тренер\n"
                " Всі функції без обмежень"
            ),
            "ru": (
                "💰 Зарабатывай на ставках умнее\n\n"
                "Выбери тариф:\n\n"
                "🔹 Basic 1 месяц  $7\n"
                "🔥 AI Прогнозы дня\n"
                "Анализ 15 ставок в день\n"
                " Полная статистика и аналитика\n\n"
                " VIP 1 месяц  $19.99\n"
                "🔥 AI Прогнозы Basic + VIP\n"
                " 30 скринов в день\n"
                " AI Тренер\n"
                " Все функции без ограничений"
            ),
            "en": (
                "💰 Bet smarter, earn more\n\n"
                "Choose your plan:\n\n"
                "🔹 Basic 1 month  $7\n"
                "🔥 AI Predictions of the day\n"
                " 15 screenshots per day\n"
                " Full statistics and analytics\n\n"
                " VIP 1 month  $19.99\n"
                "🔥 Basic + VIP AI Predictions\n"
                " 30 screenshots per day\n"
                " AI Coach\n"
                " All features unlimited"
            ),
        }[lang]

        await query.message.reply_text(
            buy_text,
            reply_markup=access_keyboard(lang)
        )
        return ConversationHandler.END
