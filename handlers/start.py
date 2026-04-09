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
            "🔥 Хочеш перестати зливати на ставках?\n\n"
            "90% гравців:\n"
            "❌ ставлять на емоціях\n"
            "❌ відіграються\n"
            "❌ зливають банк\n\n"
            "👇 Проблема не в ставках,\n"
            "а у відсутності системи\n\n"
            "📊 Як виглядає результат при правильному підході:\n\n"
            "+20-30% ROI за 7 днів\n"
            "85% прохід ставок\n\n"
            "⚡ Це не удача\n"
            "це поєднання системи + правильно відібраних ставок\n\n"
            "💡 Що ти отримуєш у боті:\n\n"
            "🎯 Ставки з високою ймовірністю (спеціалізований AI шукає ставки із value коефіцієнтом)\n"
            "📊 Реальну статистику (ROI, winrate твоїх ставок і системи)\n"
            "🧠 Розуміння, чому ставка має перевагу\n"
            "📈 Контроль емоцій і ріст банку\n"
            "📝 Навчання: патерни, аналіз, системи пошуку ставок із value кф., сигнали для входу в лайві...\n\n"
            "❌ Це не “залізобетон”\n"
            "❌ І не договірняки\n\n"
            "✔ Це інструмент, який допомагає бути в плюсі на дистанції\n"
            "✔ Платформа, з якою ти заробляєш, отримуєш досвід та навички\n\n"
            "🎯 Ти не просто ставиш\n"
            "ти починаєш контролювати результат\n\n"
            "⚠️ Ти вже зробив перший крок\n"
            "тепер головне — не повернутись до хаосу\n\n"
            "👇 Спробуй і подивись результат:"
        )

    if lang == "ru":
        return (
            "🔥 Хочешь перестать сливать на ставках?\n\n"
            "90% игроков:\n"
            "❌ ставят на эмоциях\n"
            "❌ отыгрываются\n"
            "❌ сливают банк\n\n"
            "👇 Проблема не в ставках,\n"
            "а в отсутствии системы\n\n"
            "📊 Как выглядит результат при правильном подходе:\n\n"
            "+20-30% ROI за 7 дней\n"
            "85% проход ставок\n\n"
            "⚡ Это не удача\n"
            "это сочетание системы + правильно отобранных ставок\n\n"
            "💡 Что ты получаешь в боте:\n\n"
            "🎯 Ставки с высокой вероятностью (специализированный AI ищет ставки с value коэффициентом)\n"
            "📊 Реальную статистику (ROI, winrate твоих ставок и системы)\n"
            "🧠 Понимание, почему ставка имеет преимущество\n"
            "📈 Контроль эмоций и рост банка\n"
            "📝 Обучение: паттерны, анализ, системы поиска ставок с value кф., сигналы для входа в лайве...\n\n"
            "❌ Это не “железобетон”\n"
            "❌ И не договорняки\n\n"
            "✔ Это инструмент, который помогает быть в плюсе на дистанции\n"
            "✔ Платформа, с которой ты зарабатываешь, получаешь опыт и навыки\n\n"
            "🎯 Ты не просто ставишь\n"
            "ты начинаешь контролировать результат\n\n"
            "⚠️ Ты уже сделал первый шаг\n"
            "теперь главное — не возвращаться к хаосу\n\n"
            "👇 Попробуй и посмотри результат:"
        )

    return (
        "🔥 Want to stop losing on bets?\n\n"
        "90% of players:\n"
        "❌ bet emotionally\n"
        "❌ chase losses\n"
        "❌ lose their bankroll\n\n"
        "👇 The problem is not the bets,\n"
        "but the lack of a system\n\n"
        "📊 What the result looks like with the right approach:\n\n"
        "+20-30% ROI in 7 days\n"
        "85% bet hit rate\n\n"
        "⚡ This is not luck\n"
        "it is a combination of system + properly selected bets\n\n"
        "💡 What you get inside the bot:\n\n"
        "🎯 High-probability bets (a specialized AI searches for bets with value odds)\n"
        "📊 Real statistics (ROI, win rate of your bets and the system)\n"
        "🧠 Understanding why a bet has an edge\n"
        "📈 Emotional control and bankroll growth\n"
        "📝 Learning: patterns, analysis, value-bet search systems, live entry signals...\n\n"
        "❌ This is not a “sure thing”\n"
        "❌ And not fixed matches\n\n"
        "✔ This is a tool that helps you stay profitable in the long run\n"
        "✔ A platform where you earn, gain experience, and build skills\n\n"
        "🎯 You do not just place bets\n"
        "you start controlling the result\n\n"
        "⚠️ You have already taken the first step\n"
        "now the key is not to go back to chaos\n\n"
        "👇 Try it and see the result:"
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    create_user_if_not_exists(user)

    db_user = get_user(user.id)
    lang = _normalize_lang((db_user or {}).get("lang", "en"))

    if user_has_access(user.id):
        active_text = {
            "ua": "✔ Доступ активний.",
            "ru": "✔ Доступ активен.",
            "en": "✔ Access is active.",
        }[lang]

        await update.message.reply_text(
            active_text,
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
    lang = _normalize_lang((user or {}).get("lang", "en"))

    if user_has_access(tg_user.id):
        active_text = {
            "ua": "✔ Доступ активний.",
            "ru": "✔ Доступ активен.",
            "en": "✔ Access is active.",
        }[lang]

        await query.message.reply_text(
            active_text,
            reply_markup=main_menu_keyboard(lang)
        )
        return

    if query.data == "try_trial":
        if is_trial_available(tg_user.id):
            start_trial_mode(tg_user.id)

            trial_text = {
                "ua": (
                    "🚀 Пробний доступ активовано!\n\n"
                    "⚠️ У тебе є можливість перевірити\n"
                    "частину функціоналу, як бот вестиме\n"
                    " твою статистику, надіславши 3 скріна\n"
                    " вже зіграних ставок або дізнайся більше про\n"
                    " платформу за info посиланням\n\n"
                    "👇 Надішли перший скрін або @bet_tracker_info_ua"
                ),
                "ru": (
                    "🚀 Пробный доступ активирован!\n\n"
                    "⚠️ У тебя есть возможность протестировать часть функционала\n"
                    "и посмотреть, как бот ведёт твою статистику, отправив 3 скрина\n"
                    "уже сыгранных ставок или\n"
                    "узнать больше о платформе по info ссылке\n\n"
                    "👇 Отправь первый скрин или @bet_tracker_info_ua"
                ),
                "en": (
                    "🚀 Trial access activated!\n\n"
                    "⚠️ You can test part of the functionality\n"
                    "and see how the bot tracks your stats by sending 3 screenshots\n"
                    "of your completed bets or\n"
                    "learn more about the platform via the info link\n\n"
                    "👇 Send your first screenshot or @bet_tracker_info_ua"
                ),
            }[lang]

            await query.message.reply_text(
                trial_text,
                reply_markup=main_menu_keyboard(lang)
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
                "🚀 Повний доступ дає:\n\n"
                "📊 Повну статистику\n"
                "🧠 Аналітику\n"
                "📈 Контроль ROI\n"
                "🎯 Ставки з високою ймовірністю\n\n"
                "👇 Обери тариф"
            ),
            "ru": (
                "🚀 Полный доступ даёт:\n\n"
                "📊 Полную статистику\n"
                "🧠 Аналитику\n"
                "📈 Контроль ROI\n"
                "🎯 Ставки с высокой вероятностью\n\n"
                "👇 Выбери тариф"
            ),
            "en": (
                "🚀 Full access gives you:\n\n"
                "📊 Full statistics\n"
                "🧠 Analytics\n"
                "📈 ROI control\n"
                "🎯 High-probability bets\n\n"
                "👇 Choose a plan"
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