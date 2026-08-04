# -*- coding: utf-8 -*-
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, ConversationHandler

from keyboards import main_inline_menu_keyboard, welcome_offer_keyboard, access_keyboard
from db import (
    create_user_if_not_exists,
    get_coldmind_remaining,
    get_subscription_type,
    get_user,
    is_onboarding_completed,
    user_has_access,
    is_trial_available,
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

def _welcome_text(lang: str, promo_available: bool) -> str:
    lang = _normalize_lang(lang)
    texts = {
        "ua": (
            "🎯 Більшість зливають банк не через погані ставки, а через відсутність системи.\n\n"
            "Bet Tracker  це AI-сигнали + повний облік твоєї гри в одному боті:\n\n"
            "🔥 1 сигнал щодня  відібраний AI, з обґрунтуванням\n"
            "📊 Трекер включено  ROI, Win Rate та історія рахуються автоматично\n"
            "🧊 ColdMind  тренер, який тримає тебе в дисципліні проти тільту\n\n"
            "Перший тиждень  безкоштовно. Без карти, без зобов'язань.\n\n"
            "👇 Обери дію:"
        ),
        "ru": (
            "🎯 Большинство сливают банк не из-за плохих ставок, а из-за отсутствия системы.\n\n"
            "Bet Tracker  это AI-сигналы + полный учёт твоей игры в одном боте:\n\n"
            "🔥 1 сигнал каждый день  отобран AI, с обоснованием\n"
            "📊 Трекер включён  ROI, Win Rate и история считаются автоматически\n"
            "🧊 ColdMind  тренер, который держит тебя в дисциплине против тильта\n\n"
            "Первая неделя  бесплатно. Без карты, без обязательств.\n\n"
            "👇 Выбери действие:"
        ),
        "en": (
            "🎯 Most bettors don't lose because of bad picks  they lose because they have no system.\n\n"
            "Bet Tracker = AI signals + full tracking of your game in one bot:\n\n"
            "🔥 1 signal daily  picked by AI, with reasoning\n"
            "📊 Tracker included  ROI, Win Rate and history counted automatically\n"
            "🧊 ColdMind  a discipline coach that keeps you off tilt\n\n"
            "First week is free. No card, no strings attached.\n\n"
            "👇 Choose an action:"
        ),
    }
    return texts[lang]


def _activate_trial_keyboard(lang: str) -> InlineKeyboardMarkup:
    labels = {
        "ua": "🎁 Активувати Trial",
        "ru": "🎁 Активировать Trial",
        "en": "🎁 Activate Trial",
    }
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(labels.get(_normalize_lang(lang), labels["en"]), callback_data="try_trial")
    ]])


def _bet_tracker_intro_text(lang: str) -> str:
    lang = _normalize_lang(lang)
    texts = {
        "ua": (
            "📊 Bet Tracker\n\n"
            "Надсилаєш скрін купона  бот автоматично розпізнає ставку, коефіцієнт і суму.\n\n"
            "Далі все рахується без ручних таблиць:\n"
            "ROI, Win Rate, прибуток, серії та історія ставок.\n\n"
            "AI показує, які типи ставок зливають банк, а які реально працюють.\n"
            "Емоційний трекер разом із ColdMind помічає тільт і допомагає тримати дисципліну.\n\n"
            "Tracker is included in Trial and every plan"
        ),
        "ru": (
            "📊 Bet Tracker\n\n"
            "Отправляешь скрин купона  бот автоматически распознаёт ставку, коэффициент и сумму.\n\n"
            "Дальше всё считается без ручных таблиц:\n"
            "ROI, Win Rate, прибыль, серии и история ставок.\n\n"
            "AI показывает, какие типы ставок сливают банк, а какие реально работают.\n"
            "Эмоциональный трекер вместе с ColdMind замечает тильт и помогает держать дисциплину.\n\n"
            "Tracker is included in Trial and every plan"
        ),
        "en": (
            "📊 Bet Tracker\n\n"
            "Send a bet slip screenshot  the bot automatically reads the pick, odds and stake.\n\n"
            "Then everything is counted without spreadsheets:\n"
            "ROI, Win Rate, profit, streaks and bet history.\n\n"
            "AI shows which bet types leak money and which ones actually work.\n"
            "The emotion tracker and ColdMind spot tilt and help you stay disciplined.\n\n"
            "Tracker is included in Trial and every plan"
        ),
    }
    return texts[lang]


def _education_intro_text(lang: str) -> str:
    lang = _normalize_lang(lang)
    texts = {
        "ua": (
            "🎓 Навчання з ColdMind\n\n"
            "Буде структуроване навчання: основи беттингу, патерни, психологія, дисципліна банку та стратегії.\n\n"
            "Перший модуль скоро. Активуй Trial, щоб бути серед перших, хто отримає доступ."
        ),
        "ru": (
            "🎓 Обучение с ColdMind\n\n"
            "Будет структурированное обучение: основы беттинга, паттерны, психология, дисциплина банка и стратегии.\n\n"
            "Первый модуль скоро. Активируй Trial, чтобы быть среди первых, кто получит доступ."
        ),
        "en": (
            "🎓 Learning with ColdMind\n\n"
            "Structured learning is coming: betting fundamentals, patterns, psychology, bankroll discipline and strategies.\n\n"
            "The first module is coming soon. Activate Trial to be among the first to get access."
        ),
    }
    return texts[lang]

def _access_status_banner(lang: str, user_id: int) -> str:
    sub_type = get_subscription_type(user_id)
    if sub_type == "trial":
        remaining, limit, _ = get_coldmind_remaining(user_id, "trial")
        used = max(0, limit - remaining)
        if lang == "ru":
            return f"🎁 Пробный доступ: {used}/{limit} запрос сегодня\nПолный доступ в Basic и VIP"
        if lang == "en":
            return f"🎁 Trial access: {used}/{limit} request today\nFull access in Basic and VIP"
        return f"🎁 Пробний доступ: {used}/{limit} запит сьогодні\nПовний доступ у Basic та VIP"

    if sub_type == "vip":
        return {"ua": "💎 VIP активний", "ru": "💎 VIP активен", "en": "💎 VIP active"}.get(lang, "💎 VIP active")
    if sub_type == "basic":
        return {"ua": "🔹 Basic активний", "ru": "🔹 Basic активен", "en": "🔹 Basic active"}.get(lang, "🔹 Basic active")
    return {"ua": "⛔ Доступ не активний", "ru": "⛔ Доступ не активен", "en": "⛔ Access is not active"}.get(lang, "⛔ Access is not active")


def _main_menu_text(lang: str, user_id: int) -> str:
    status = _access_status_banner(lang, user_id)
    if lang == "ru":
        return (
            f"{status}\n\n"
            "Главное меню\n\n"
            "🔥 AI-сигналы дня - готовые ставки и история\n"
            "📊 Моя статистика - ROI, прибыль, серии\n"
            "🤖 AI-анализ PRO - разбор матча по фото или тексту\n"
            "📸 Добавить ставку - пришли скрин купона\n"
            "💎 VIP - полный доступ и ColdMind"
        )
    if lang == "en":
        return (
            f"{status}\n\n"
            "Main menu\n\n"
            "🔥 AI signals today - ready picks and history\n"
            "📊 My stats - ROI, profit, streaks\n"
            "🤖 AI analysis PRO - match analysis from photo or text\n"
            "📸 Add bet - send a bet slip screenshot\n"
            "💎 VIP - full access and ColdMind"
        )
    return (
        f"{status}\n\n"
        "Головне меню\n\n"
        "🔥 AI-сигнали дня - готові ставки та історія\n"
        "📊 Моя статистика - ROI, прибуток, серії\n"
        "🤖 AI-аналіз PRO - розбір матчу з фото або тексту\n"
        "📸 Додати ставку - надішли скрін купона\n"
        "💎 VIP - повний доступ і ColdMind"
    )


async def send_main_menu(message, user_id: int, lang: str | None = None):
    user = get_user(user_id) or {}
    normalized_lang = _normalize_lang(lang or user.get("lang", "en"))
    await message.reply_text(
        _main_menu_text(normalized_lang, user_id),
        reply_markup=main_inline_menu_keyboard(normalized_lang),
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    existing_user = get_user(user.id)
    create_user_if_not_exists(user)

    if context.args:
        payload = context.args[0]
        if payload.startswith("ref_") and len(payload) > 4:
            source_key = payload[4:].lower()
            if source_key.isdigit():
                referrer_id = int(source_key)
                if not existing_user and referrer_id != user.id:
                    from db import register_user_referral

                    register_user_referral(referrer_id, user.id)
            else:
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
        await send_main_menu(update.message, user.id, lang)
        return

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

    if query.data == "bet_tracker_intro":
        await query.message.reply_text(
            _bet_tracker_intro_text(lang),
            reply_markup=_activate_trial_keyboard(lang),
        )
        return ConversationHandler.END

    if query.data == "education_intro":
        await query.message.reply_text(
            _education_intro_text(lang),
            reply_markup=_activate_trial_keyboard(lang),
        )
        return ConversationHandler.END

    if user_has_access(tg_user.id):
        await send_main_menu(query.message, tg_user.id, lang)
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
            limit_text = {
                "ua": "❌ Пробний доступ вже використано.",
                "ru": "❌ Пробный доступ уже использован.",
                "en": "❌ Trial access has already been used.",
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
                " 🧊 ColdMind AI Agent\n"
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
                " 🧊 ColdMind AI Agent\n"
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
                " 🧊 ColdMind AI Agent\n"
                " All features unlimited"
            ),
        }[lang]

        await query.message.reply_text(
            buy_text,
            reply_markup=access_keyboard(lang)
        )
        return ConversationHandler.END
