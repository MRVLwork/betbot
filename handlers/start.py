from telegram import Update
from telegram.ext import ContextTypes

from keyboards import main_menu_keyboard, welcome_offer_keyboard, access_keyboard
from db import (
    create_user_if_not_exists,
    get_user,
    user_has_access,
    is_trial_available,
    get_trial_remaining,
    get_trial_used_count,
    start_trial_mode,
    has_used_promo_offer,
)


def _welcome_text(lang: str, promo_available: bool) -> str:
    if lang == "ru":
        if promo_available:
            return (
                "🤖 Добро пожаловать в Bet Tracker Bot\n\n"
                "Бот покажет реальную картину по твоим ставкам:\n"
                "• прибыль / убыток\n"
                "• ROI\n"
                "• winrate\n"
                "• средний коэффициент\n\n"
                "🎁 Сейчас действует акционное подключение:\n"
                "• 99 ⭐ — Basic 7 дней\n"
                "• 399 ⭐ — Basic 1 месяц\n"
                "• VIP 1 месяц: 1500 ⭐ → 999 ⭐\n"
                "• Basic 1 месяц — 4$ USDT\n"
                "• VIP 1 месяц: 15$ → 9.99$ USDT\n\n"
                "После продления или следующих оплат будут действовать полные тарифы.\n\n"
                "Выбери один из вариантов ниже."
            )
        return (
            "🤖 Добро пожаловать в Bet Tracker Bot\n\n"
            "Бот покажет реальную картину по твоим ставкам:\n"
            "• прибыль / убыток\n"
            "• ROI\n"
            "• winrate\n"
            "• средний коэффициент\n\n"
            "Доступны стандартные тарифы:\n"
            "• 99 ⭐ — Basic 7 дней\n"
            "• 399 ⭐ — Basic 1 месяц\n"
            "• 1500 ⭐ — VIP 1 месяц\n"
            "• 4$ USDT — Basic 1 месяц\n"
            "• 15$ USDT — VIP 1 месяц\n\n"
            "Выбери один из вариантов ниже."
        )

    if promo_available:
        return (
            "🤖 Вітаю в Bet Tracker Bot\n\n"
            "Бот покаже реальну картину по твоїх ставках:\n"
            "• прибуток / збиток\n"
            "• ROI\n"
            "• winrate\n"
            "• середній коефіцієнт\n\n"
            "🎁 Зараз діє акційне підключення:\n"
            "• 99 ⭐ — Basic 7 днів\n"
            "• 399 ⭐ — Basic 1 місяць\n"
            "• VIP 1 місяць: 1500 ⭐ → 999 ⭐\n"
            "• Basic 1 місяць — 4$ USDT\n"
            "• VIP 1 місяць: 15$ → 9.99$ USDT\n\n"
            "Після продовження або наступних оплат діятимуть повні тарифи.\n\n"
            "Обери один із варіантів нижче."
        )

    return (
        "🤖 Вітаю в Bet Tracker Bot\n\n"
        "Бот покаже реальну картину по твоїх ставках:\n"
        "• прибуток / збиток\n"
        "• ROI\n"
        "• winrate\n"
        "• середній коефіцієнт\n\n"
        "Доступні стандартні тарифи:\n"
        "• 99 ⭐ — Basic 7 днів\n"
        "• 399 ⭐ — Basic 1 місяць\n"
        "• 1500 ⭐ — VIP 1 місяць\n"
        "• 4$ USDT — Basic 1 місяць\n"
        "• 15$ USDT — VIP 1 місяць\n\n"
        "Обери один із варіантів нижче."
    )


def _trial_continue_text(lang: str, used: int, remaining: int) -> str:
    if lang == "ru":
        return (
            f"🧪 У тебя уже начат тестовый доступ.\n\n"
            f"Использовано: {used}/3\n"
            f"Осталось: {remaining}/3\n\n"
            f"Нажми «Попробовать» и отправь следующий скрин."
        )

    return (
        f"🧪 У тебе вже розпочато тестовий доступ.\n\n"
        f"Використано: {used}/3\n"
        f"Залишилось: {remaining}/3\n\n"
        f"Натисни «Спробувати» і надішли наступний скрін."
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    create_user_if_not_exists(user)
    db_user = get_user(user.id)
    lang = db_user["lang"] or "ua"

    if user_has_access(user.id):
        await update.message.reply_text(
            "✅ Доступ активний." if lang == "ua" else "✅ Доступ активен.",
            reply_markup=main_menu_keyboard(lang)
        )
        return

    used = get_trial_used_count(user.id)
    remaining = get_trial_remaining(user.id)
    promo_available = not has_used_promo_offer(user.id)

    if used > 0 and is_trial_available(user.id):
        text = _trial_continue_text(lang, used, remaining)
    else:
        text = _welcome_text(lang, promo_available)

    await update.message.reply_text(
        text,
        reply_markup=welcome_offer_keyboard(lang)
    )


async def start_offer_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    user = get_user(user_id)
    lang = user["lang"] or "ua"

    if query.data == "pay_now":
        await query.message.reply_text(
            "💳 Обери спосіб оплати:" if lang == "ua" else "💳 Выбери способ оплаты:",
            reply_markup=access_keyboard(lang)
        )
        return

    if query.data == "try_trial":
        if user_has_access(user_id):
            await query.message.reply_text(
                "✅ У тебе вже є активний доступ." if lang == "ua" else "✅ У тебя уже есть активный доступ."
            )
            return

        if not is_trial_available(user_id):
            await query.message.reply_text(
                "⛔ Тест уже використано. Нижче можеш оформити доступ."
                if lang == "ua" else
                "⛔ Тест уже использован. Ниже можешь оформить доступ.",
                reply_markup=access_keyboard(lang)
            )
            return

        start_trial_mode(user_id)

        await query.message.reply_text(
            "🧪 Тест активовано.\n\n"
            "Надішли 3 скріни ставок у цей чат.\n"
            "Після 3-го скріна ти отримаєш базову статистику та актуальну пропозицію."
            if lang == "ua" else
            "🧪 Тест активирован.\n\n"
            "Отправь 3 скрина ставок в этот чат.\n"
            "После 3-го скрина ты получишь базовую статистику и актуальное предложение."
        )
