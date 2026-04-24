# -*- coding: utf-8 -*-
from telegram import Update
from telegram.ext import ContextTypes


async def send_weekly_wrap(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    if not update.message:
        return

    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "ua")

    try:
        from db import get_user
        user = get_user(user_id)
        if user and user.get("lang"):
            lang = user["lang"].lower()
            if lang.startswith("uk"):
                lang = "ua"
    except Exception:
        pass

    texts = {
        "ua": (
            "🛠 Функція Weekly Wrapped\n"
            "зараз в розробці.\n\n"
            "Незабаром тут буде твоя\n"
            "тижнева статистика у вигляді\n"
            "красивої картки 📊"
        ),
        "ru": (
            "🛠 Функция Weekly Wrapped\n"
            "сейчас в разработке.\n\n"
            "Скоро здесь будет твоя\n"
            "недельная статистика в виде\n"
            "красивой карточки 📊"
        ),
        "en": (
            "🛠 Weekly Wrapped feature\n"
            "is coming soon.\n\n"
            "Your weekly stats card\n"
            "will be available here 📊"
        ),
    }

    await update.message.reply_text(
        texts.get(lang, texts["ua"])
    )


async def send_weekly_wrap_broadcast(bot):
    pass
