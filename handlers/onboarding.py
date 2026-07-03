# -*- coding: utf-8 -*-
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import ContextTypes, ConversationHandler

from db import complete_onboarding, get_user, is_trial_available, save_onboarding_data, start_trial_mode
from keyboards import main_menu_keyboard
from handlers.admin_notify import notify_admin_activation
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


def _clean_choice_text(value: str) -> str:
    value = (value or "").strip()
    if " " in value:
        prefix, rest = value.split(" ", 1)
        if len(prefix) <= 8 and not any(char.isalnum() for char in prefix):
            return rest.strip()
    return value


def _demo_stats_text(lang: str, sport: str, goal: str) -> str:
    sport = (_clean_choice_text(sport) or "-").lower()
    goal = (_clean_choice_text(goal) or "-").lower()

    if lang == "ru":
        return (
            f"Настроено под тебя: {sport}, цель  {goal}.\n"
            "Вот как будет выглядеть твоя панель (пример на демо-данных):\n"
            "--------------------------------------------------\n"
            "📊 Моя статистика (Сегодня)\n\n"
            "💰 Прибыль: 3071.41\n"
            "📈 ROI: 21.76%\n"
            "🎯 % выигрышных ставок: 66.67%\n"
            "📊 Средний коэф: 1.64\n\n"
            "🔥 Серия: 2"
        )
    if lang == "en":
        return (
            f"Set up for you: {sport}, goal  {goal}.\n"
            "Here's how your dashboard will look (demo data example):\n"
            "--------------------------------------------------\n"
            "📊 My stats (Today)\n\n"
            "💰 Profit: 3071.41\n"
            "📈 ROI: 21.76%\n"
            "🎯 Win rate: 66.67%\n"
            "📊 Avg odds: 1.64\n\n"
            "🔥 Streak: 2"
        )
    return (
        f"Налаштовано під тебе: {sport}, ціль  {goal}.\n"
        "Ось як виглядатиме твоя панель (приклад на демо-даних):\n"
        "--------------------------------------------------\n"
        "📊 Моя статистика (Сьогодні)\n\n"
        "💰 Прибуток: 3071.41\n"
        "📈 ROI: 21.76%\n"
        "🎯 % виграшних ставок: 66.67%\n"
        "📊 Середній коеф: 1.64\n\n"
        "🔥 Серія: 2"
    )


def _trial_activated_text(lang: str) -> str:
    return (
        "🎉 *Пробний доступ активовано!*\n"
        "🔥 AI-сигнали дня\n"
        "📊 ROI та Win Rate\n"
        "🤖 AI-аналіз ставок\n"
        "💡 Персональні рекомендації\n"
        "👇 Почни з AI-сигналів або додай свою першу ставку"
    )


def _first_bet_cta_text(lang: str) -> str:
    if lang == "ru":
        return (
            "🎯 Остался один шаг до твоей реальной статистики.\n\n"
            "Добавь первую ставку - это займет 20 секунд:\n"
            "📸 Пришли скрин своей ставки из БК\n"
            "   (купон со ставкой, коэфом и суммой)\n\n"
            "AI сам распознает ставку, коэф и сумму\n"
            "и твоя панель начнет заполняться.\n"
            "👇 Нажми Добавить ставку или просто пришли фото купона."
        )
    if lang == "en":
        return (
            "🎯 One step left to your real stats.\n\n"
            "Add your first bet - it takes 20 seconds:\n"
            "📸 Send a screenshot of your bet from the bookmaker\n"
            "   (bet slip with the pick, odds, and stake)\n\n"
            "AI will detect the bet, odds, and stake\n"
            "and your dashboard will start filling up.\n"
            "👇 Tap Add bet or just send a photo of the slip."
        )
    return (
        "🎯 Залишився один крок до твоєї реальної статистики.\n\n"
        "Додай першу ставку - це займе 20 секунд:\n"
        "📸 Надішли скрін своєї ставки з букмекера\n"
        "   (купон зі ставкою, коефом і сумою)\n\n"
        "AI сам розпізнає ставку, коеф і суму\n"
        "і твоя панель почне заповнюватися.\n"
        "👇 Натисни Додати ставку або просто надішли фото купона."
    )


async def activate_trial_after_onboarding(update: Update, context: ContextTypes.DEFAULT_TYPE, lang: str, remove_reply_keyboard: bool = False):
    user_id = update.effective_user.id
    message = update.effective_message

    if remove_reply_keyboard:
        await message.reply_text("✓", reply_markup=ReplyKeyboardRemove())

    await message.reply_text(
        _demo_stats_text(
            lang,
            context.user_data.get("onboarding_sport", ""),
            context.user_data.get("onboarding_goal", ""),
        ),
        parse_mode="Markdown",
    )

    if is_trial_available(user_id):
        start_trial_mode(user_id)
        await notify_admin_activation(context, user_id, "Trial")

    user = get_user(user_id) or {}
    await message.reply_text(
        _first_bet_cta_text(lang),
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
    context.user_data["onboarding_goal"] = main_goal

    save_onboarding_data(user_id, sport, "", "", main_goal)
    complete_onboarding(user_id)

    return await activate_trial_after_onboarding(update, context, lang, remove_reply_keyboard=True)
