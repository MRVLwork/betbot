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


def _welcome_text(lang: str, promo_available: bool) -> str:
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
            "🔥 Want to win consistently on sports bets?\n\n"
            "Most people bet randomly\n"
            "and lose their bankroll\n\n"
            "👇 Inside this bot you get:\n\n"
            "📊 High-probability bets\n"
            "📈 Real stats (ROI / Winrate)\n"
            "🧠 Analysis of your mistakes\n\n"
            "❗ But most importantly:\n\n"
            "You will see whether you are actually profitable\n"
            "or just think you are\n\n"
            "⚡ Just send 1 bet screenshot\n"
            "and get analysis in 5 seconds\n\n"
            "🔥 + access to daily bets\n\n"
            "👇 Try it for free"
        )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    create_user_if_not_exists(user)

    db_user = get_user(user.id)
    lang = (db_user or {}).get("lang", "ua")

    if user_has_access(user.id):
        await update.message.reply_text(
            "✔ Доступ активний." if lang == "ua" else
            "✔ Access is active." if not lang.startswith("ru") and not lang.startswith("uk") else
            "✔ Доступ активен.",
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
    lang_low = (lang or "ua").lower()

    if user_has_access(tg_user.id):
        await query.message.reply_text(
            "✔ Доступ активний." if lang_low.startswith("uk") else
            "✔ Access is active." if not lang_low.startswith("ru") else
            "✔ Доступ активен.",
            reply_markup=main_menu_keyboard(lang)
        )
        return

    if query.data == "try_trial":
        if is_trial_available(tg_user.id):
            start_trial_mode(tg_user.id)

            trial_text = (
                "🚀 Пробний доступ активовано!\n\n"
                "⚠️ У тебе є 10 аналізів на день\n\n"
                "👇 Надішли перший скрін"
                if lang_low.startswith("uk") else
                "🚀 Trial access activated!\n\n"
                "⚠️ You have 10 analyses per day\n\n"
                "👇 Send your first screenshot"
                if not lang_low.startswith("ru") else
                "🚀 Пробный доступ активирован!\n\n"
                "⚠️ У тебя есть 10 анализов в день\n\n"
                "👇 Отправь первый скрин"
            )

            await query.message.reply_text(
                trial_text,
                reply_markup=main_menu_keyboard(lang)
            )
        else:
            remaining = get_trial_remaining(tg_user.id)

            limit_text = (
                f"❌ Пробний доступ вже використано. Залишилось: {remaining}"
                if lang_low.startswith("uk") else
                f"❌ Trial access has already been used. Remaining: {remaining}"
                if not lang_low.startswith("ru") else
                f"❌ Пробный доступ уже использован. Осталось: {remaining}"
            )

            await query.message.reply_text(limit_text)

    elif query.data == "pay_now":
        buy_text = (
            "🚀 Повний доступ дає:\n\n"
            "📊 Повну статистику\n"
            "🧠 Аналітику\n"
            "📈 Контроль ROI\n\n"
            "👇 Обери тариф"
            if lang_low.startswith("uk") else
            "🚀 Full access gives you:\n\n"
            "📊 Full statistics\n"
            "🧠 Analytics\n"
            "📈 ROI control\n\n"
            "👇 Choose a plan"
            if not lang_low.startswith("ru") else
            "🚀 Полный доступ даёт:\n\n"
            "📊 Полную статистику\n"
            "🧠 Аналитику\n"
            "📈 Контроль ROI\n\n"
            "👇 Выбери тариф"
        )

        await query.message.reply_text(
            buy_text,
            reply_markup=access_keyboard(lang)
        )
