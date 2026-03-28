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
    if lang == "ru":
        return (
            "Привет 👋\n\n"
            "❗️ Ты уверен, что не в минусе на ставках?\n\n"
            "Большинство игроков **теряют деньги**, даже когда им кажется, что всё идёт нормально.\n\n"
            "Почему так происходит:\n"
            "— не считают реальную прибыль\n"
            "— не видят свой ROI\n"
            "— не замечают, какие ставки реально тянут вниз\n"
            "— играют по ощущениям, а не по цифрам\n\n"
            "📊 Bet Tracker Bot покажет правду о твоих ставках:\n"
            "• прибыль или убыток 💰\n"
            "• ROI 📈\n"
            "• винрейт 🎯\n"
            "• средний коэффициент\n"
            "• серии выигрышей и проигрышей\n\n"
            "⚡️ Уже после нескольких ставок ты увидишь:\n"
            "👉 ты реально в плюсе или тебе только так кажется\n"
            "👉 где именно теряешь деньги\n"
            "👉 есть ли у тебя система, а не случайные результаты\n\n"
            "👇 Выбери, с чего начать:"
        )
    else:
        return (
            "Привіт 👋\n\n"
            "❗️ Ти впевнений, що не в мінусі на ставках?\n\n"
            "Більшість гравців **втрачають гроші**, навіть коли їм здається, що все йде нормально.\n\n"
            "Чому так відбувається:\n"
            "— не рахують реальний прибуток\n"
            "— не бачать свій ROI\n"
            "— не помічають, які ставки реально тягнуть вниз\n"
            "— грають на відчуттях, а не по цифрах\n\n"
            "📊 Bet Tracker Bot покаже правду про твої ставки:\n"
            "• прибуток або збиток 💰\n"
            "• ROI 📈\n"
            "• винрейт 🎯\n"
            "• середній коефіцієнт\n"
            "• серії виграшів і програшів\n\n"
            "⚡️ Уже після кількох ставок ти побачиш:\n"
            "👉 ти реально в плюсі чи лише так здається\n"
            "👉 де саме втрачаєш гроші\n"
            "👉 чи є у тебе система, а не випадкові результати\n\n"
            "👇 Обери, з чого почати:"
        )


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
                "🚀 Пробний доступ активовано!" if lang == "ua" else "🚀 Пробный доступ активирован!",
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
            "💳 Обери спосіб оплати:" if lang == "ua" else "💳 Выбери способ оплаты:",
            reply_markup=access_keyboard(lang)
        )
