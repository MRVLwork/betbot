# -*- coding: utf-8 -*-
from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from db import (
    get_user,
    get_subscription_type,
    subscribe_to_signal,
    is_subscribed_to_signal,
    is_eligible_for_first_payment_promo,
    get_free_signals,
    get_basic_signals,
    get_vip_signals,
)

HISTORY_OF_BETS_URL = "https://t.me/+HM_H1lv3zGA1NmMy"


def _normalize_lang(lang):
    lang = (lang or "ua").lower()
    if lang.startswith("uk") or lang.startswith("ua"):
        return "ua"
    if lang.startswith("ru"):
        return "ru"
    if lang.startswith("en"):
        return "en"
    return "ua"


def _get_vip_signals_active(user_id: int) -> bool:
    """VIP signals are active for VIP users or Basic users with separate access."""
    sub_type = get_subscription_type(user_id)
    if sub_type == "vip":
        return True

    user = get_user(user_id) or {}
    expires = user.get("vip_signals_expires_at")
    if not expires:
        return False

    try:
        return datetime.fromisoformat(expires) > datetime.now()
    except Exception:
        return False


def _intro_text(lang: str) -> str:
    if lang == "ru":
        return (
            "🔥 AI Прогнозы дня\n\n"
            "Готовые ставки от AI-агента - бери и играй умнее."
        )
    if lang == "en":
        return (
            "🔥 AI Predictions of the day\n\n"
            "Ready-to-bet picks from the AI agent - take them and play smarter."
        )
    return (
        "🔥 AI Прогнози дня\n\n"
        "Готові ставки від AI-агента - бери й грай розумніше."
    )


def _empty_free_text(lang: str) -> str:
    if lang == "ru":
        return "Сегодня ещё нет бесплатных ставок."
    if lang == "en":
        return "No free bets yet today."
    return "Сьогодні ще немає безкоштовних ставок."


def _empty_paid_text(lang: str, level: str) -> str:
    if lang == "ru":
        return f"Сегодня ещё нет {level} ставок."
    if lang == "en":
        return f"No {level} bets yet today."
    return f"Сьогодні ще немає {level} ставок."


def _format_signal_lines(rows: list[dict], empty_text: str) -> str:
    if not rows:
        return empty_text
    return "\n".join(f"{idx}. {row['text']}" for idx, row in enumerate(rows, start=1))


def _main_signals_text(lang: str) -> str:
    free_list = _format_signal_lines(get_free_signals(), _empty_free_text(lang))
    return f"{_intro_text(lang)}\n\nFree user's bets\n{free_list}"


def _paid_signals_text(lang: str, level: str, rows: list[dict]) -> str:
    title = {
        "basic": "📊 Basic daily AI bets",
        "vip": "💎 VIP daily AI bets",
    }[level]
    empty = _empty_paid_text(lang, "Basic" if level == "basic" else "VIP")
    return f"{title}\n\n{_format_signal_lines(rows, empty)}"


def _signals_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📊 Basic daily AI bets", callback_data="signals_basic_daily"),
            InlineKeyboardButton("📜 History of bets", url=HISTORY_OF_BETS_URL),
        ],
        [InlineKeyboardButton("💎 VIP daily AI bets", callback_data="signals_vip_daily")],
    ])


async def open_signals_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show AI signals tab with free picks and paid-level buttons."""
    if not update.message:
        return

    user_id = update.effective_user.id
    user = get_user(user_id) or {}
    lang = _normalize_lang(user.get("lang"))
    sub_type = get_subscription_type(user_id)

    if sub_type == "trial" and not is_subscribed_to_signal(user_id, "trial"):
        subscribe_to_signal(user_id, "trial")

    if sub_type in ("basic", "vip") and not is_subscribed_to_signal(user_id, "basic"):
        subscribe_to_signal(user_id, "basic")

    if sub_type == "vip" and not is_subscribed_to_signal(user_id, "vip"):
        subscribe_to_signal(user_id, "vip")

    await update.message.reply_text(
        _main_signals_text(lang),
        reply_markup=_signals_keyboard(),
    )


async def _send_basic_offer(message, lang: str):
    from keyboards import access_keyboard

    promo = {
        "ua": (
            "💰 Basic підписка  $7/міс\n\n"
            "Отримуй Basic daily AI bets і повну статистику.\n\n"
            "Обери спосіб оплати:"
        ),
        "ru": (
            "💰 Basic подписка  $7/мес\n\n"
            "Получай Basic daily AI bets и полную статистику.\n\n"
            "Выбери способ оплаты:"
        ),
        "en": (
            "💰 Basic  $7/mo\n\n"
            "Get Basic daily AI bets and full stats.\n\n"
            "Choose payment:"
        ),
    }
    await message.reply_text(promo.get(lang, promo["ua"]), reply_markup=access_keyboard(lang))


async def _send_vip_offer(message, lang: str, user_id: int):
    from keyboards import vip_subscription_keyboard

    promo = {
        "ua": (
            "💎 VIP підписка\n\n"
            "Отримуй Basic + VIP daily AI bets, ColdMind AI Agent і повну статистику.\n\n"
            "Обери план:"
        ),
        "ru": (
            "💎 VIP подписка\n\n"
            "Получай Basic + VIP daily AI bets, ColdMind AI Agent и полную статистику.\n\n"
            "Выбери план:"
        ),
        "en": (
            "💎 VIP\n\n"
            "Get Basic + VIP daily AI bets, ColdMind AI Agent and full stats.\n\n"
            "Choose plan:"
        ),
    }
    await message.reply_text(
        promo.get(lang, promo["ua"]),
        reply_markup=vip_subscription_keyboard(
            lang,
            show_promo=is_eligible_for_first_payment_promo(user_id),
        ),
    )


async def _send_vip_signals_offer(message, lang: str):
    from keyboards import vip_signals_payment_keyboard

    promo = {
        "ua": (
            "💎 VIP daily AI bets  $5 / 10 днів\n\n"
            "Окрема підписка на VIP ставки без апгрейду на повний VIP.\n\n"
            "399⭐ або $5\n\n"
            "Обери спосіб оплати:"
        ),
        "ru": (
            "💎 VIP daily AI bets  $5 / 10 дней\n\n"
            "Отдельная подписка на VIP ставки без апгрейда на полный VIP.\n\n"
            "399⭐ или $5\n\n"
            "Выбери способ оплаты:"
        ),
        "en": (
            "💎 VIP daily AI bets  $5 / 10 days\n\n"
            "Separate VIP bets subscription without full VIP upgrade.\n\n"
            "399⭐ or $5\n\n"
            "Choose payment:"
        ),
    }
    await message.reply_text(promo.get(lang, promo["ua"]), reply_markup=vip_signals_payment_keyboard(lang))


async def signals_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle AI signals menu callbacks."""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    user = get_user(user_id) or {}
    lang = _normalize_lang(user.get("lang"))
    sub_type = get_subscription_type(user_id)
    data = query.data

    if data in ("signals_basic_daily", "signals_basic_info"):
        if sub_type in ("basic", "vip"):
            await query.message.reply_text(_paid_signals_text(lang, "basic", get_basic_signals()))
        else:
            await _send_basic_offer(query.message, lang)
        return

    if data in ("signals_vip_daily", "signals_vip_info"):
        if _get_vip_signals_active(user_id):
            await query.message.reply_text(_paid_signals_text(lang, "vip", get_vip_signals()))
        elif sub_type == "basic":
            await _send_vip_signals_offer(query.message, lang)
        else:
            await _send_vip_offer(query.message, lang, user_id)
        return

    if data == "signals_trial_info":
        await query.message.reply_text(_main_signals_text(lang), reply_markup=_signals_keyboard())
        return

    if data == "signals_buy_basic":
        await _send_basic_offer(query.message, lang)
        return

    if data == "signals_buy_vip":
        await _send_vip_offer(query.message, lang, user_id)
        return

    if data == "signals_buy_vip_for_basic":
        await _send_vip_signals_offer(query.message, lang)
