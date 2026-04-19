from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from db import get_ai_daily_remaining, get_user, user_has_access
from keyboards import access_keyboard
from services.ai_service import ai_coach_reply


def _normalize_lang(lang: str) -> str:
    lang = (lang or "en").lower()
    if lang.startswith("uk") or lang.startswith("ua"):
        return "ua"
    if lang.startswith("ru"):
        return "ru"
    return "en"


def _coach_end_keyboard(lang: str) -> InlineKeyboardMarkup:
    labels = {
        "ua": "✅ Завершити чат з тренером",
        "ru": "✅ Завершить чат с тренером",
        "en": "✅ End coach chat",
    }
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(labels.get(lang, labels["en"]), callback_data="coach_end")]
    ])


async def open_coach(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    user_id = update.effective_user.id
    user = get_user(user_id) or {}
    lang = _normalize_lang(user.get("lang", "en"))
    plan = (user.get("plan") or "basic").lower()

    if not user_has_access(user_id) or plan != "vip":
        texts = {
            "ua": "🧠 AI Тренер доступний тільки для VIP підписки\n👇 Оновити підписку",
            "ru": "🧠 AI Тренер доступен только для VIP подписки\n👇 Обновить подписку",
            "en": "🧠 AI Coach is available only with VIP subscription\n👇 Upgrade your plan",
        }
        await update.message.reply_text(texts[lang], reply_markup=access_keyboard(lang))
        return

    remaining = get_ai_daily_remaining(user_id)
    if remaining <= 0:
        texts = {
            "ua": "Ліміт AI запитів на сьогодні вичерпано.",
            "ru": "Лимит AI запросов на сегодня исчерпан.",
            "en": "Your AI daily limit has been reached for today.",
        }
        await update.message.reply_text(texts[lang])
        return

    context.user_data["awaiting_coach_reply"] = True
    prompts = {
        "ua": "🧠 Запитай мене про свою статистику або стратегію:",
        "ru": "🧠 Спроси меня о своей статистике или стратегии:",
        "en": "🧠 Ask me about your stats or strategy:",
    }
    await update.message.reply_text(prompts[lang], reply_markup=_coach_end_keyboard(lang))


async def handle_coach_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    if not context.user_data.get("awaiting_coach_reply"):
        return

    user_id = update.effective_user.id
    user = get_user(user_id) or {}
    lang = _normalize_lang(user.get("lang", "en"))
    plan = (user.get("plan") or "basic").lower()

    if update.message.text in {"✅ Завершити чат з тренером", "✅ Завершить чат с тренером", "✅ End coach chat"}:
        return

    processing = {
        "ua": "🧠 Аналізую твою статистику...",
        "ru": "🧠 Анализирую твою статистику...",
        "en": "🧠 Analyzing your stats...",
    }
    await update.message.reply_text(processing[lang])

    reply = await ai_coach_reply(user_id, update.message.text, lang, plan)
    await update.message.reply_text(reply, reply_markup=_coach_end_keyboard(lang))


async def coach_end_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = get_user(update.effective_user.id) or {}
    lang = _normalize_lang(user.get("lang", "en"))
    context.user_data.pop("awaiting_coach_reply", None)

    texts = {
        "ua": "Чат з AI тренером завершено.",
        "ru": "Чат с AI тренером завершен.",
        "en": "AI coach chat ended.",
    }

    await query.message.edit_reply_markup(None)
    await query.message.reply_text(texts[lang])
