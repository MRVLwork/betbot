# -*- coding: utf-8 -*-
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from db import get_coldmind_remaining, get_subscription_type, get_user, has_vip_signals_access, user_has_access
from keyboards import access_keyboard
from services.ai_service import ai_coach_reply, is_vip


def _normalize_lang(lang: str) -> str:
    lang = (lang or "en").lower()
    if lang.startswith("uk") or lang.startswith("ua"):
        return "ua"
    if lang.startswith("ru"):
        return "ru"
    return "en"


def _coach_end_keyboard(lang: str) -> InlineKeyboardMarkup:
    labels = {
        "ua": "✅ Завершити чат з ColdMind AI Agent",
        "ru": "✅ Завершить чат с ColdMind AI Agent",
        "en": "✅ End ColdMind AI Agent chat",
    }
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(labels.get(lang, labels["en"]), callback_data="coach_end")]
    ])


def _trial_banner_text(lang: str) -> str:
    texts = {
        "ua": (
            "🧊 ColdMind (пробний доступ)\n"
            "Тобі доступний 1 запит на день. Повний доступ — у Basic і VIP."
        ),
        "ru": (
            "🧊 ColdMind (пробный доступ)\n"
            "Тебе доступен 1 запрос в день. Полный доступ — в Basic и VIP."
        ),
        "en": (
            "🧊 ColdMind (trial access)\n"
            "You have 1 request per day. Full access is in Basic and VIP."
        ),
    }
    return texts.get(lang, texts["en"])


def _coldmind_limit_text(lang: str, plan: str, limit: int) -> str:
    plan = (plan or "none").lower()
    if plan == "trial":
        texts = {
            "ua": (
                "🧊 На пробному доступі — 1 запит ColdMind на день, і він вичерпаний.\n\n"
                "Повний ColdMind (десятки запитів на місяць) доступний у Basic і VIP:\n"
                "👇 Активуй, щоб я стежив за твоїм банком щодня."
            ),
            "ru": (
                "🧊 На пробном доступе — 1 запрос ColdMind в день, и он исчерпан.\n\n"
                "Полный ColdMind (десятки запросов в месяц) доступен в Basic и VIP:\n"
                "👇 Активируй, чтобы я следил за твоим банком каждый день."
            ),
            "en": (
                "🧊 Trial access gives 1 ColdMind request per day, and it is used.\n\n"
                "Full ColdMind (dozens of requests per month) is available in Basic and VIP:\n"
                "👇 Activate access so I can watch your bankroll every day."
            ),
        }
        return texts.get(lang, texts["en"])
    if plan == "basic":
        texts = {
            "ua": (
                f"🧊 Ти використав усі запити ColdMind цього місяця ({limit}).\n\n"
                "Ліміт оновиться на початку наступного місяця.\n"
                "Потрібно більше? VIP дає 150 запитів на місяць."
            ),
            "ru": (
                f"🧊 Ты использовал все запросы ColdMind в этом месяце ({limit}).\n\n"
                "Лимит обновится в начале следующего месяца.\n"
                "Нужно больше? VIP дает 150 запросов в месяц."
            ),
            "en": (
                f"🧊 You used all ColdMind requests this month ({limit}).\n\n"
                "The limit resets at the start of next month.\n"
                "Need more? VIP gives 150 requests per month."
            ),
        }
        return texts.get(lang, texts["en"])
    texts = {
        "ua": (
            f"🧊 Ти використав усі запити ColdMind цього місяця ({limit}).\n\n"
            "Ліміт оновиться на початку наступного місяця.\n"
            "Твоя дисципліна цього місяця вражає — до зустрічі 1 числа."
        ),
        "ru": (
            f"🧊 Ты использовал все запросы ColdMind в этом месяце ({limit}).\n\n"
            "Лимит обновится в начале следующего месяца.\n"
            "Твоя дисциплина в этом месяце впечатляет — до встречи 1 числа."
        ),
        "en": (
            f"🧊 You used all ColdMind requests this month ({limit}).\n\n"
            "The limit resets at the start of next month.\n"
            "Your discipline this month is impressive — see you on the 1st."
        ),
    }
    return texts.get(lang, texts["en"])


def _coldmind_limit_keyboard(lang: str, plan: str):
    plan = (plan or "none").lower()
    if plan == "vip":
        return None
    if plan == "basic":
        labels = {
            "ua": "💎 Перейти на VIP",
            "ru": "💎 Перейти на VIP",
            "en": "💎 Upgrade to VIP",
        }
        return InlineKeyboardMarkup([[
            InlineKeyboardButton(labels.get(lang, labels["en"]), callback_data="vip_buy_1m")
        ]])
    labels = {
        "ua": "💎 Отримати доступ",
        "ru": "💎 Получить доступ",
        "en": "💎 Get access",
    }
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(labels.get(lang, labels["en"]), callback_data="buy_stars")
    ]])


def _resolve_coldmind_plan(user_id: int, user: dict) -> str:
    sub_type = get_subscription_type(user_id)
    plan = (user.get("plan") or "basic").lower()
    if sub_type == "trial":
        return "trial"
    if user_has_access(user_id) and is_vip(plan):
        return "vip"
    if has_vip_signals_access(user_id):
        return "vip"
    if sub_type in {"basic", "vip"}:
        return sub_type
    return "none"


async def open_coach(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    user_id = update.effective_user.id
    user = get_user(user_id) or {}
    lang = _normalize_lang(user.get("lang", "en"))
    coach_plan = _resolve_coldmind_plan(user_id, user)
    if coach_plan == "none":
        texts = {
            "ua": "🧊 ColdMind AI Agent доступний у Trial, Basic і VIP.\n👇 Активуй доступ",
            "ru": "🧊 ColdMind AI Agent доступен в Trial, Basic и VIP.\n👇 Активируй доступ",
            "en": "🧊 ColdMind AI Agent is available in Trial, Basic and VIP.\n👇 Activate access",
        }
        await update.message.reply_text(texts[lang], reply_markup=access_keyboard(lang))
        return

    if coach_plan == "trial":
        remaining, limit, _ = get_coldmind_remaining(user_id, coach_plan)
        if remaining <= 0:
            await update.message.reply_text(
                _coldmind_limit_text(lang, coach_plan, limit),
                reply_markup=_coldmind_limit_keyboard(lang, coach_plan),
            )
            return
        await update.message.reply_text(_trial_banner_text(lang))

    context.user_data["awaiting_coach_reply"] = True
    prompts = {
        "ua": "🧊 ColdMind AI Agent\n\nЗапитай мене про свою статистику або стратегію:",
        "ru": "🧊 ColdMind AI Agent\n\nСпроси меня о своей статистике или стратегии:",
        "en": "🧊 ColdMind AI Agent\n\nAsk me about your stats or strategy:",
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
    coach_plan = _resolve_coldmind_plan(user_id, user)

    if update.message.text in {"✅ Завершити чат з ColdMind AI Agent", "✅ Завершить чат с ColdMind AI Agent", "✅ End ColdMind AI Agent chat"}:
        return

    if coach_plan == "none":
        texts = {
            "ua": "🧊 ColdMind AI Agent доступний у Trial, Basic і VIP.\n👇 Активуй доступ",
            "ru": "🧊 ColdMind AI Agent доступен в Trial, Basic и VIP.\n👇 Активируй доступ",
            "en": "🧊 ColdMind AI Agent is available in Trial, Basic and VIP.\n👇 Activate access",
        }
        await update.message.reply_text(texts[lang], reply_markup=access_keyboard(lang))
        return

    remaining, limit, _ = get_coldmind_remaining(user_id, coach_plan)
    if remaining <= 0:
        await update.message.reply_text(
            _coldmind_limit_text(lang, coach_plan, limit),
            reply_markup=_coldmind_limit_keyboard(lang, coach_plan),
        )
        return

    if coach_plan == "trial":
        await update.message.reply_text(_trial_banner_text(lang))

    processing = {
        "ua": "🧊 Аналізую твою статистику...",
        "ru": "🧊 Анализирую твою статистику...",
        "en": "🧊 Analyzing your stats...",
    }
    await update.message.reply_text(processing[lang])

    reply = await ai_coach_reply(user_id, update.message.text, lang, coach_plan)
    await update.message.reply_text(reply, reply_markup=_coach_end_keyboard(lang))


async def coach_end_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = get_user(update.effective_user.id) or {}
    lang = _normalize_lang(user.get("lang", "en"))
    context.user_data.pop("awaiting_coach_reply", None)

    texts = {
        "ua": "Чат з ColdMind AI Agent завершено.",
        "ru": "Чат с ColdMind AI Agent завершен.",
        "en": "ColdMind AI Agent chat ended.",
    }

    await query.message.edit_reply_markup(None)
    await query.message.reply_text(texts[lang])
