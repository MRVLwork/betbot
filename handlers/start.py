from telegram import Update
from telegram.ext import ContextTypes

from keyboards import main_menu_keyboard, welcome_offer_keyboard, access_keyboard
from db import (
    create_user_if_not_exists,
    get_user,
    user_has_access,
    is_trial_available,
    get_trial_remaining,
    start_trial_mode,
    has_used_promo_offer,
)

def _welcome_text(lang: str) -> str:
    lang = (lang or "ru").lower()

    if lang.startswith("uk"):
        return (
            "🔥 Хочеш стабільно вигравати на ставках?\n\n"
            "Більшість просто ставить навмання\n"
            "і зливає банк\n\n"
            "👇 У цьому боті ти отримуєш:\n\n"
            "📊 Ставки з високою проходимістю\n"
            "📈 Реальну статистику (ROI / Winrate)\n"
            "🧠 Аналіз твоїх помилок\n\n"
            "❗ Але головне:\n\n"
            "Ти побачиш, чи ти реально в плюсі\n"
            "чи просто думаєш, що виграєш\n\n"
            "⚡ Просто відправ 1 скрін ставки\n"
            "і отримай аналіз за 5 секунд\n\n"
            "🔥 + доступ до щоденних ставок\n\n"
            "👇 Спробуй безкоштовно"
        )

    elif lang.startswith("ru"):
        return (
            "🔥 Хочешь стабильно выигрывать на ставках?\n\n"
            "Большинство ставит наугад\n"
            "и сливает банк\n\n"
            "👇 В этом боте ты получаешь:\n\n"
            "📊 Ставки с высокой проходимостью\n"
            "📈 Реальную статистику (ROI / Winrate)\n"
            "🧠 Анализ твоих ошибок\n\n"
            "❗ Но главное:\n\n"
            "Ты увидишь, реально ли ты в плюсе\n"
            "или просто думаешь, что выигрываешь\n\n"
            "⚡ Просто отправь 1 скрин ставки\n"
            "и получи анализ за 5 секунд\n\n"
            "🔥 + доступ к ежедневным ставкам\n\n"
            "👇 Попробуй бесплатно"
        )

    else:
        return (
            "🔥 Want to win consistently in betting?\n\n"
            "Most people bet randomly\n"
            "and lose their bankroll\n\n"
            "👇 In this bot you get:\n\n"
            "📊 High winrate bets\n"
            "📈 Real stats (ROI / Winrate)\n"
            "🧠 Analysis of your mistakes\n\n"
            "❗ Most important:\n\n"
            "You will see if you are really profitable\n"
            "or just think you are\n\n"
            "⚡ Send 1 bet screenshot\n"
            "and get analysis in 5 seconds\n\n"
            "🔥 + access to daily bets\n\n"
            "👇 Try for free"
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
    query = update.callback_query
    await query.answer()

    tg_user = update.effective_user
    create_user_if_not_exists(tg_user)

    user = get_user(tg_user.id)
    lang = (user or {}).get("lang", "ua")

    if user_has_access(tg_user.id):
        await query.message.reply_text(
            "✔ Доступ активний." if lang == "ua" else "✔ Доступ активен.",
            reply_markup=main_menu_keyboard(lang)
        )
        return

    if query.data == "try_trial":
        if is_trial_available(tg_user.id):
            start_trial_mode(tg_user.id)

            await query.message.reply_text(
                "🚀 Пробний доступ активовано!\n\n"
                "⚠️ У тебе є 10 аналізів на день\n\n"
                "👇 Надішли перший скрін"
                if lang == "ua"
                else "🚀 Пробный доступ активирован!\n\n"
                     "⚠️ У тебя есть 10 анализов в день\n\n"
                     "👇 Отправь первый скрин",
                reply_markup=main_menu_keyboard(lang)
            )
        else:
            remaining = get_trial_remaining(tg_user.id)

            await query.message.reply_text(
                f"❌ Пробний доступ вже використано. Залишилось: {remaining}"
                if lang == "ua"
                else f"❌ Пробный доступ уже использован. Осталось: {remaining}"
            )

    elif query.data == "pay_now":
        await query.message.reply_text(
            "🚀 Повний доступ дає:\n\n"
            "📊 Повну статистику\n"
            "🧠 Аналітику\n"
            "📈 Контроль ROI\n\n"
            "👇 Обери тариф"
            if lang == "ua"
            else "🚀 Полный доступ даёт:\n\n"
                 "📊 Полную статистику\n"
                 "🧠 Аналитику\n"
                 "📈 Контроль ROI\n\n"
                 "👇 Выбери тариф",
            reply_markup=access_keyboard(lang)
        )
