# -*- coding: utf-8 -*-
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import ContextTypes, ConversationHandler

from db import complete_onboarding, get_user, is_trial_available, save_onboarding_data, start_trial_mode
from keyboards import main_menu_keyboard
from states import ONBOARDING_GOAL, ONBOARDING_SPORT


def _normalize_lang(lang: str) -> str:
    lang = (lang or "en").lower()
    if lang.startswith("uk") or lang.startswith("ua"):
        return "ua"
    if lang.startswith("ru"):
        return "ru"
    return "en"


def _keyboard(options: list[str]) -> ReplyKeyboardMarkup:
    rows = [[option] for option in options]
    return ReplyKeyboardMarkup(rows, resize_keyboard=True, one_time_keyboard=True)


def _get_lang(user_id: int) -> str:
    user = get_user(user_id)
    return _normalize_lang((user or {}).get("lang", "en"))


def _sport_options(lang: str) -> list[str]:
    if lang == "ru":
        return ["⚽ Футбол", "🎾 Теннис", "🏀 Баскет", "🏒 Хоккей", "🎯 Микс"]
    if lang == "en":
        return ["⚽ Football", "🎾 Tennis", "🏀 Basketball", "🏒 Hockey", "🎯 Mixed"]
    return ["⚽ Футбол", "🎾 Теніс", "🏀 Баскет", "🏒 Хокей", "🎯 Мікс"]


def _goal_options(lang: str) -> list[str]:
    if lang == "ru":
        return ["💰 Зарабатывать", "🛑 Не сливать", "📊 Анализировать"]
    if lang == "en":
        return ["💰 Earn", "🛑 Stop losing", "📊 Analyze"]
    return ["💰 Заробляти", "🛑 Не зливати", "📊 Аналізувати"]


def _sport_prompt(lang: str) -> str:
    if lang == "ru":
        return "Привет! Давай настроим бота под тебя. Это займет 1 минуту 🎯\n\nНа какой спорт ты ставишь чаще всего?"
    if lang == "en":
        return "Hi! Let's set up the bot for you. It takes 1 minute 🎯\n\nWhich sport do you bet on most often?"
    return "Привіт! Давай налаштуємо бота під тебе. Це займе 1 хвилину 🎯\n\nЯкий спорт ставиш найчастіше?"


def _goal_prompt(lang: str) -> str:
    if lang == "ru":
        return "Какая у тебя главная цель?"
    if lang == "en":
        return "What is your main goal?"
    return "Яка твоя головна ціль?"


def _invalid_choice_text(lang: str) -> str:
    if lang == "ru":
        return "Выбери один из вариантов на кнопках."
    if lang == "en":
        return "Choose one of the button options."
    return "Обері варіант з кнопок."


def _trial_activated_text(lang: str) -> str:
    if lang == "ru":
        return (
            "🎁 *Пробный доступ активирован!*\n\n"
            "💰 Зарабатывай на ставках умнее:\n"
            "🔥 Глянь AI Прогнозы дня - готовые ставки\n"
            "📊 Или кинь скрин ставки для статистики\n\n"
            "🎁 У тебя 3 дня и 5 ставок в день"
        )
    if lang == "en":
        return (
            "🎁 *Trial activated!*\n\n"
            "💰 Bet smarter, earn more:\n"
            "🔥 Check AI Predictions - ready picks\n"
            "📊 Or send a bet screenshot for stats\n\n"
            "🎁 You have 3 days and 5 bets per day"
        )
    return (
        "🎁 *Пробний доступ активовано!*\n\n"
        "💰 Заробляй на ставках розумніше:\n"
        "🔥 Глянь AI Прогнози дня - готові ставки\n"
        "📊 Або кинь скрін ставки для статистики\n\n"
        "🎁 У тебе 3 дні і 5 ставок на день"
    )


async def activate_trial_after_onboarding(update: Update, lang: str, remove_reply_keyboard: bool = False):
    user_id = update.effective_user.id

    if is_trial_available(user_id):
        start_trial_mode(user_id)

    message = update.effective_message
    if remove_reply_keyboard:
        await message.reply_text("✓", reply_markup=ReplyKeyboardRemove())

    user = get_user(user_id) or {}
    await message.reply_text(
        _trial_activated_text(lang),
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard(lang, user.get("plan", "basic")),
    )
    return ConversationHandler.END


async def start_onboarding(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = _get_lang(update.effective_user.id)
    context.user_data["onboarding_lang"] = lang
    context.user_data.pop("onboarding_sport", None)
    context.user_data.pop("onboarding_goal", None)

    await update.effective_message.reply_text(
        _sport_prompt(lang),
        reply_markup=_keyboard(_sport_options(lang)),
    )
    return ONBOARDING_SPORT


async def onboarding_sport(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get("onboarding_lang", _get_lang(update.effective_user.id))
    text = (update.message.text or "").strip()
    if text not in _sport_options(lang):
        await update.message.reply_text(_invalid_choice_text(lang), reply_markup=_keyboard(_sport_options(lang)))
        return ONBOARDING_SPORT

    context.user_data["onboarding_sport"] = text
    await update.message.reply_text(
        _goal_prompt(lang),
        reply_markup=_keyboard(_goal_options(lang)),
    )
    return ONBOARDING_GOAL


async def onboarding_goal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get("onboarding_lang", _get_lang(update.effective_user.id))
    text = (update.message.text or "").strip()
    if text not in _goal_options(lang):
        await update.message.reply_text(_invalid_choice_text(lang), reply_markup=_keyboard(_goal_options(lang)))
        return ONBOARDING_GOAL

    user_id = update.effective_user.id
    sport = context.user_data.get("onboarding_sport", "")
    main_goal = text

    save_onboarding_data(user_id, sport, "", "", main_goal)
    complete_onboarding(user_id)

    return await activate_trial_after_onboarding(update, lang, remove_reply_keyboard=True)
