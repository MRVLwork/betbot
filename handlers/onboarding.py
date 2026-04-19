from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import ContextTypes, ConversationHandler

from db import complete_onboarding, get_user, has_used_promo_offer, save_onboarding_data, user_has_access
from keyboards import main_menu_keyboard, welcome_offer_keyboard
from states import ONBOARDING_DEPOSIT, ONBOARDING_EXPERIENCE, ONBOARDING_GOAL, ONBOARDING_SPORT


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


def _experience_options(lang: str) -> list[str]:
    if lang == "ru":
        return ["Новичок (<6мес)", "1-2 года", "3+ года"]
    if lang == "en":
        return ["Beginner (<6mo)", "1-2 years", "3+ years"]
    return ["Новачок (<6міс)", "1-2 роки", "3+ роки"]


def _deposit_options() -> list[str]:
    return ["до $100", "$100-300", "$300-1000", "$1000+"]


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


def _experience_prompt(lang: str) -> str:
    if lang == "ru":
        return "Сколько времени ты занимаешься беттингом?"
    if lang == "en":
        return "How long have you been betting?"
    return "Скільки часу займаєшся беттінгом?"


def _deposit_prompt(lang: str) -> str:
    if lang == "ru":
        return "Какой у тебя средний депозит в месяц?"
    if lang == "en":
        return "What is your average monthly deposit?"
    return "Який твій середній депозит на місяць?"


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


def _personalized_text(lang: str, experience: str, goal: str) -> str:
    experience_value = experience.lower()
    goal_value = goal.lower()

    is_beginner = "новач" in experience_value or "beginner" in experience_value or "нович" in experience_value
    is_advanced_earn = (
        ("3+" in experience_value)
        and ("зароб" in goal_value or "earn" in goal_value or "зарабат" in goal_value)
    )
    is_stop_losing = "не злив" in goal_value or "stop losing" in goal_value or "не сливать" in goal_value

    if is_advanced_earn:
        if lang == "ru":
            return "🔥 Отлично! Опытные беттеры с системным подходом показывают ROI +8-15%.\nТы на правильном пути."
        if lang == "en":
            return "🔥 Excellent! Experienced bettors with a systematic approach often show ROI of +8-15%.\nYou are on the right track."
        return "🔥 Відмінно! Досвідчені беттери з системним підходом показують ROI +8-15%.\nТи на правильному шляху."

    if is_stop_losing:
        if lang == "ru":
            return "🛡 Правильный приоритет! 73% убытков беттеров  это эмоциональные решения.\nЭтот бот покажет, где ты теряешь."
        if lang == "en":
            return "🛡 The right priority! 73% of bettor losses come from emotional decisions.\nThis bot will show where you are losing."
        return "🛡 Правильний пріоритет! 73% збитків беттерів  емоційні рішення.\nЦей бот покаже де ти втрачаєш."

    if is_beginner:
        if lang == "ru":
            return "👋 Добро пожаловать! Начнем с основ  просто присылай скрины своих ставок."
        if lang == "en":
            return "👋 Welcome! Let's start with the basics  just send screenshots of your bets."
        return "👋 Добро пожаловать! Почнемо з основ  просто надсилай скріни своїх ставок."

    if lang == "ru":
        return "🎯 Отлично, профиль настроен. Теперь бот будет полезнее именно под твой стиль."
    if lang == "en":
        return "🎯 Great, your profile is set. The bot will now fit your style better."
    return "🎯 Чудово, профіль налаштовано. Тепер бот буде кориснішим саме під твій стиль."


async def _send_standard_welcome(update: Update, lang: str):
    user_id = update.effective_user.id

    if user_has_access(user_id):
        active_text = {
            "ua": "✔ Доступ активний.",
            "ru": "✔ Доступ активен.",
            "en": "✔ Access is active.",
        }[lang]
        await update.message.reply_text(active_text, reply_markup=main_menu_keyboard(lang))
        return

    promo_available = not has_used_promo_offer(user_id)
    from handlers.start import _welcome_text  # local import to avoid circular import at module load

    await update.message.reply_text(
        _welcome_text(lang, promo_available),
        reply_markup=welcome_offer_keyboard(lang),
    )


async def start_onboarding(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = _get_lang(update.effective_user.id)
    context.user_data["onboarding_lang"] = lang
    context.user_data.pop("onboarding_sport", None)
    context.user_data.pop("onboarding_experience", None)
    context.user_data.pop("onboarding_deposit", None)
    context.user_data.pop("onboarding_goal", None)

    await update.message.reply_text(
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
        _experience_prompt(lang),
        reply_markup=_keyboard(_experience_options(lang)),
    )
    return ONBOARDING_EXPERIENCE


async def onboarding_experience(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get("onboarding_lang", _get_lang(update.effective_user.id))
    text = (update.message.text or "").strip()
    if text not in _experience_options(lang):
        await update.message.reply_text(_invalid_choice_text(lang), reply_markup=_keyboard(_experience_options(lang)))
        return ONBOARDING_EXPERIENCE

    context.user_data["onboarding_experience"] = text
    await update.message.reply_text(
        _deposit_prompt(lang),
        reply_markup=_keyboard(_deposit_options()),
    )
    return ONBOARDING_DEPOSIT


async def onboarding_deposit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get("onboarding_lang", _get_lang(update.effective_user.id))
    text = (update.message.text or "").strip()
    if text not in _deposit_options():
        await update.message.reply_text(_invalid_choice_text(lang), reply_markup=_keyboard(_deposit_options()))
        return ONBOARDING_DEPOSIT

    context.user_data["onboarding_deposit"] = text
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
    experience = context.user_data.get("onboarding_experience", "")
    monthly_deposit = context.user_data.get("onboarding_deposit", "")
    main_goal = text

    save_onboarding_data(user_id, sport, experience, monthly_deposit, main_goal)
    complete_onboarding(user_id)

    await update.message.reply_text(
        _personalized_text(lang, experience, main_goal),
        reply_markup=ReplyKeyboardRemove(),
    )
    await _send_standard_welcome(update, lang)
    return ConversationHandler.END
