# -*- coding: utf-8 -*-
from datetime import datetime

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from db import (
    get_daily_limit_usage,
    get_user,
    get_user_limits,
    has_vip_signals_access,
    mark_limits_configured,
    set_limit_bets_count,
    set_limit_lose_amount,
    set_limit_lose_count,
    set_limit_stake_amount,
    user_has_access,
)
from keyboards import main_menu_keyboard
from services.ai_service import is_vip


LIMIT_FIELD_CONFIG = {
    "stake_amount": {
        "column": "limit_stake_amount",
        "kind": "amount",
        "emoji": "💰",
        "labels": {
            "ua": "Ліміт суми однієї ставки",
            "ru": "Лимит суммы одной ставки",
            "en": "Single stake limit",
        },
        "ask": {
            "ua": "🧊 Введи макс суму однієї ставки (грн):",
            "ru": "🧊 Введи макс сумму одной ставки:",
            "en": "🧊 Enter the max amount for one bet:",
        },
        "setters": set_limit_stake_amount,
    },
    "bets_count": {
        "column": "limit_bets_count",
        "kind": "int",
        "emoji": "🔢",
        "labels": {
            "ua": "Ліміт кількості ставок",
            "ru": "Лимит количества ставок",
            "en": "Daily bets count limit",
        },
        "ask": {
            "ua": "🧊 Введи макс кількість ставок за день:",
            "ru": "🧊 Введи макс количество ставок за день:",
            "en": "🧊 Enter the max number of bets per day:",
        },
        "setters": set_limit_bets_count,
    },
    "lose_count": {
        "column": "limit_lose_count",
        "kind": "int",
        "emoji": "📉",
        "labels": {
            "ua": "Ліміт програшів за день",
            "ru": "Лимит проигрышей за день",
            "en": "Daily losses count limit",
        },
        "ask": {
            "ua": "🧊 Введи макс кількість програшів за день:",
            "ru": "🧊 Введи макс количество проигрышей за день:",
            "en": "🧊 Enter the max number of losses per day:",
        },
        "setters": set_limit_lose_count,
    },
    "lose_amount": {
        "column": "limit_lose_amount",
        "kind": "amount",
        "emoji": "💸",
        "labels": {
            "ua": "Ліміт суми зливу за день",
            "ru": "Лимит суммы слива за день",
            "en": "Daily loss amount limit",
        },
        "ask": {
            "ua": "🧊 Введи макс суму зливу за день:",
            "ru": "🧊 Введи макс сумму слива за день:",
            "en": "🧊 Enter the max daily loss amount:",
        },
        "setters": set_limit_lose_amount,
    },
}


def _normalize_lang(lang: str) -> str:
    lang = (lang or "en").lower()
    if lang.startswith("uk") or lang.startswith("ua"):
        return "ua"
    if lang.startswith("ru"):
        return "ru"
    return "en"


def _fmt_value(value, kind: str, lang: str) -> str:
    if value is None:
        return {"ua": "не задано", "ru": "не задано", "en": "not set"}[lang]
    if kind == "int":
        return str(int(value))
    number = float(value)
    return str(int(number)) if number.is_integer() else f"{number:.2f}"


def _limits_lines(lang: str, limits: dict) -> list[str]:
    rows = []
    for field in ("stake_amount", "bets_count", "lose_count", "lose_amount"):
        cfg = LIMIT_FIELD_CONFIG[field]
        rows.append(
            f"{cfg['emoji']} {cfg['labels'][lang]}: "
            f"{_fmt_value(limits.get(cfg['column']), cfg['kind'], lang)}"
        )
    return rows


def limits_setup_text(lang: str, limits: dict) -> str:
    lang = _normalize_lang(lang)
    intro = {
        "ua": (
            "🧊 ColdMind: почнемо день з дисципліни.\n\n"
            "Встанови ліміти — я стежитиму, щоб ти їх не порушив.\n"
            "По кожному: натисни, щоб задати, або пропусти.\n\n"
        ),
        "ru": (
            "🧊 ColdMind: начнем день с дисциплины.\n\n"
            "Установи лимиты — я буду следить, чтобы ты их не нарушил.\n"
            "По каждому: нажми, чтобы задать, или пропусти.\n\n"
        ),
        "en": (
            "🧊 ColdMind: start the day with discipline.\n\n"
            "Set limits — I will watch that you do not break them.\n"
            "For each one: tap to set it, or skip it.\n\n"
        ),
    }[lang]
    return intro + "\n".join(_limits_lines(lang, limits))


def limits_status_text(lang: str, limits: dict) -> str:
    lang = _normalize_lang(lang)
    headings = {
        "ua": "🧊 Твої ліміти на сьогодні:",
        "ru": "🧊 Твои лимиты на сегодня:",
        "en": "🧊 Your limits for today:",
    }
    return headings[lang] + "\n\n" + "\n".join(_limits_lines(lang, limits))


def limits_summary_text(lang: str, limits: dict) -> str:
    lang = _normalize_lang(lang)
    headings = {
        "ua": "🧊 Ліміти збережено. Я стежу.",
        "ru": "🧊 Лимиты сохранены. Я слежу.",
        "en": "🧊 Limits saved. I am watching.",
    }
    return headings[lang] + "\n\n" + "\n".join(_limits_lines(lang, limits))


def limits_keyboard(lang: str) -> InlineKeyboardMarkup:
    lang = _normalize_lang(lang)
    labels = {
        "ua": {
            "set_stake_amount": "💰 Задати суму ставки",
            "set_bets_count": "🔢 Задати к-сть ставок",
            "set_lose_count": "📉 Задати ліміт програшів",
            "set_lose_amount": "💸 Задати суму зливу",
            "skip": "Пропустити",
            "done": "Готово",
        },
        "ru": {
            "set_stake_amount": "💰 Задать сумму ставки",
            "set_bets_count": "🔢 Задать к-во ставок",
            "set_lose_count": "📉 Задать лимит проигрышей",
            "set_lose_amount": "💸 Задать сумму слива",
            "skip": "Пропустить",
            "done": "Готово",
        },
        "en": {
            "set_stake_amount": "💰 Set stake amount",
            "set_bets_count": "🔢 Set bets count",
            "set_lose_count": "📉 Set losses limit",
            "set_lose_amount": "💸 Set loss amount",
            "skip": "Skip",
            "done": "Done",
        },
    }[lang]
    rows = []
    for field in ("stake_amount", "bets_count", "lose_count", "lose_amount"):
        rows.append([
            InlineKeyboardButton(labels[f"set_{field}"], callback_data=f"limits_set_{field}"),
            InlineKeyboardButton(labels["skip"], callback_data=f"limits_skip_{field}"),
        ])
    rows.append([InlineKeyboardButton(labels["done"], callback_data="limits_done")])
    return InlineKeyboardMarkup(rows)


def limits_status_keyboard(lang: str) -> InlineKeyboardMarkup:
    lang = _normalize_lang(lang)
    label = {
        "ua": "Змінити ліміти",
        "ru": "Изменить лимиты",
        "en": "Change limits",
    }[lang]
    return InlineKeyboardMarkup([[InlineKeyboardButton(label, callback_data="limits_open")]])


async def send_limits_prompt(bot, user: dict, today: str | None = None):
    user_id = int(user["user_id"])
    lang = _normalize_lang(user.get("lang") or "ua")
    limits = dict(user)
    configured = bool(user.get("limits_configured_at"))
    if configured:
        text = limits_status_text(lang, limits)
        keyboard = limits_status_keyboard(lang)
    else:
        text = limits_setup_text(lang, limits)
        keyboard = limits_keyboard(lang)
    await bot.send_message(chat_id=user_id, text=text, reply_markup=keyboard)


async def open_limits_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = get_user(user_id) or {}
    lang = _normalize_lang(user.get("lang") or "ua")
    limits = get_user_limits(user_id)
    await update.message.reply_text(
        limits_setup_text(lang, limits),
        reply_markup=limits_keyboard(lang),
    )


async def limits_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    user = get_user(user_id) or {}
    lang = _normalize_lang(user.get("lang") or "ua")
    data = query.data or ""

    if data == "limits_open":
        await query.message.reply_text(
            limits_setup_text(lang, get_user_limits(user_id)),
            reply_markup=limits_keyboard(lang),
        )
        return

    if data == "limits_ask_coldmind":
        plan = (user.get("plan") or "basic").lower()
        if not ((user_has_access(user_id) and is_vip(plan)) or has_vip_signals_access(user_id)):
            await query.message.reply_text({
                "ua": "🧊 ColdMind AI Agent доступний тільки для VIP підписки.",
                "ru": "🧊 ColdMind AI Agent доступен только для VIP подписки.",
                "en": "🧊 ColdMind AI Agent is available only with VIP subscription.",
            }[lang])
            return
        context.user_data["awaiting_coach_reply"] = True
        await query.message.reply_text({
            "ua": "🧊 ColdMind AI Agent\n\nНапиши, що сталося зі ставками сьогодні.",
            "ru": "🧊 ColdMind AI Agent\n\nНапиши, что случилось со ставками сегодня.",
            "en": "🧊 ColdMind AI Agent\n\nTell me what happened with your bets today.",
        }[lang])
        return

    if data == "limits_done":
        mark_limits_configured(user_id)
        context.user_data.pop("awaiting_limit_field", None)
        await query.message.edit_reply_markup(None)
        await query.message.reply_text(
            limits_summary_text(lang, get_user_limits(user_id)),
            reply_markup=main_menu_keyboard(lang, user.get("plan", "basic")),
        )
        return

    if data.startswith("limits_skip_"):
        field = data.removeprefix("limits_skip_")
        cfg = LIMIT_FIELD_CONFIG.get(field)
        if not cfg:
            return
        cfg["setters"](user_id, None)
        await query.message.reply_text(
            limits_setup_text(lang, get_user_limits(user_id)),
            reply_markup=limits_keyboard(lang),
        )
        return

    if data.startswith("limits_set_"):
        field = data.removeprefix("limits_set_")
        cfg = LIMIT_FIELD_CONFIG.get(field)
        if not cfg:
            return
        context.user_data["awaiting_limit_field"] = field
        await query.message.reply_text(cfg["ask"][lang])


async def handle_limit_value_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    field = context.user_data.get("awaiting_limit_field")
    if not field:
        return False

    user_id = update.effective_user.id
    user = get_user(user_id) or {}
    lang = _normalize_lang(user.get("lang") or "ua")
    cfg = LIMIT_FIELD_CONFIG.get(field)
    if not cfg:
        context.user_data.pop("awaiting_limit_field", None)
        return False

    raw = (update.message.text or "").strip().replace(",", ".")
    try:
        if cfg["kind"] == "int":
            value = int(float(raw))
            if value <= 0 or float(raw) != value:
                raise ValueError
        else:
            value = float(raw)
            if value <= 0:
                raise ValueError
    except Exception:
        await update.message.reply_text({
            "ua": "Введи додатне число.",
            "ru": "Введи положительное число.",
            "en": "Enter a positive number.",
        }[lang])
        return True

    cfg["setters"](user_id, value)
    context.user_data.pop("awaiting_limit_field", None)
    value_text = _fmt_value(value, cfg["kind"], lang)
    await update.message.reply_text(
        {
            "ua": f"🧊 {cfg['labels'][lang]}: {value_text}. Я стежу.",
            "ru": f"🧊 {cfg['labels'][lang]}: {value_text}. Я слежу.",
            "en": f"🧊 {cfg['labels'][lang]}: {value_text}. I am watching.",
        }[lang]
    )
    await update.message.reply_text(
        limits_setup_text(lang, get_user_limits(user_id)),
        reply_markup=limits_keyboard(lang),
    )
    return True


def build_limit_warning_texts(
    user_id: int,
    lang: str,
    stake_amount=None,
    include_stake: bool = True,
    include_bets_count: bool = True,
    include_losses: bool = True,
) -> list[str]:
    lang = _normalize_lang(lang)
    limits = get_user_limits(user_id)
    usage = get_daily_limit_usage(user_id)
    warnings = []

    stake_limit = limits.get("limit_stake_amount")
    if include_stake and stake_limit is not None and stake_amount is not None:
        stake = float(stake_amount or 0)
        limit = float(stake_limit)
        if stake > limit:
            warnings.append({
                "ua": f"🧊 Ставка {stake:g} перевищує твій ліміт {limit:g}. Ти сам його поставив. Подумай.",
                "ru": f"🧊 Ставка {stake:g} превышает твой лимит {limit:g}. Ты сам его поставил. Подумай.",
                "en": f"🧊 Bet {stake:g} exceeds your limit {limit:g}. You set it yourself. Think.",
            }[lang])

    bets_limit = limits.get("limit_bets_count")
    if include_bets_count and bets_limit is not None:
        current = int(usage["bets_count"])
        limit = int(bets_limit)
        if current > limit:
            warnings.append({
                "ua": f"🧊 Це твоя {current}-та ставка при ліміті {limit}. Стоп.",
                "ru": f"🧊 Это твоя {current}-я ставка при лимите {limit}. Стоп.",
                "en": f"🧊 This is bet #{current} with a limit of {limit}. Stop.",
            }[lang])

    lose_limit = limits.get("limit_lose_count")
    if include_losses and lose_limit is not None:
        current = int(usage["lose_count"])
        limit = int(lose_limit)
        if current >= limit and current > 0:
            warnings.append({
                "ua": f"🧊 Ти вже програв {current} за ліміту {limit}. Це сигнал зупинитись на сьогодні.",
                "ru": f"🧊 Ты уже проиграл {current} при лимите {limit}. Это сигнал остановиться на сегодня.",
                "en": f"🧊 You already have {current} losses with a limit of {limit}. That is a signal to stop today.",
            }[lang])

    lose_amount_limit = limits.get("limit_lose_amount")
    if include_losses and lose_amount_limit is not None:
        current = float(usage["lose_amount"])
        limit = float(lose_amount_limit)
        if current >= limit and current > 0:
            warnings.append({
                "ua": f"🧊 Твій злив сьогодні {current:g} досяг ліміту {limit:g}. Закривай додаток.",
                "ru": f"🧊 Твой слив сегодня {current:g} достиг лимита {limit:g}. Закрывай приложение.",
                "en": f"🧊 Your loss today {current:g} has reached the limit {limit:g}. Close the app.",
            }[lang])

    return warnings


def limit_warning_keyboard(lang: str) -> InlineKeyboardMarkup:
    label = {
        "ua": "🧊 Порадитись з ColdMind",
        "ru": "🧊 Посоветоваться с ColdMind",
        "en": "🧊 Ask ColdMind",
    }[_normalize_lang(lang)]
    return InlineKeyboardMarkup([[InlineKeyboardButton(label, callback_data="limits_ask_coldmind")]])
