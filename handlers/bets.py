from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from telegram import Update
from telegram.ext import ContextTypes

from db import (
    create_user_if_not_exists,
    get_user,
    user_has_access,
    get_user_daily_limit,
    count_user_photos_today,
    get_user_remaining_photos_today,
    log_user_photo,
    is_trial_available,
    get_trial_remaining,
    increment_trial_usage,
    get_trial_used_count,
)
from bets_db import get_basic_stats_between
from keyboards import access_keyboard
from languages import get_text
from services import ai_service
import bets_db


def _safe_lang(user_id: int) -> str:
    user = get_user(user_id)
    if not user:
        return "ua"
    return user.get("lang") or "ua"


def _as_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(str(value).replace(",", ".").replace(" ", ""))
    except Exception:
        return default


def _normalize_bet(parsed: dict[str, Any]) -> dict[str, Any]:
    bet_type = (
        parsed.get("bet_type")
        or parsed.get("type")
        or parsed.get("market_type")
        or "result"
    )
    bet_result = (
        parsed.get("bet_result")
        or parsed.get("result")
        or parsed.get("status")
        or "pending"
    )

    stake_amount = _as_float(
        parsed.get("stake_amount")
        or parsed.get("stake")
        or parsed.get("amount")
    )
    odds = _as_float(parsed.get("odds") or parsed.get("coefficient") or parsed.get("kef"), 1.0)

    if bet_type not in ("total", "result"):
        low = str(bet_type).lower()
        bet_type = "total" if "total" in low or "тот" in low else "result"

    low_res = str(bet_result).lower()
    if low_res in ("win", "won", "виграш", "выигрыш", "green", "success"):
        bet_result = "win"
    elif low_res in ("lose", "lost", "програш", "проигрыш", "red", "fail"):
        bet_result = "lose"
    elif low_res in ("refund", "return", "повернення", "возврат", "void"):
        bet_result = "refund"
    else:
        bet_result = "pending"

    return {
        "bet_type": bet_type,
        "bet_result": bet_result,
        "stake_amount": stake_amount,
        "odds": odds,
    }


def _call_first_existing(module: Any, names: list[str], *args, **kwargs):
    for name in names:
        fn = getattr(module, name, None)
        if callable(fn):
            return fn(*args, **kwargs)
    return None


def _parse_bet(photo_bytes: bytes) -> dict[str, Any] | None:
    parsed = _call_first_existing(
        ai_service,
        [
            "parse_bet_from_image_bytes",
            "parse_bet_from_photo_bytes",
            "parse_bet_from_image",
            "parse_bet_screenshot",
            "analyze_bet_screenshot",
            "analyze_image",
        ],
        photo_bytes,
    )

    if not parsed:
        return None
    if not isinstance(parsed, dict):
        return None
    return _normalize_bet(parsed)


def _save_bet(user_id: int, bet: dict[str, Any]) -> bool:
    result = _call_first_existing(
        bets_db,
        [
            "save_bet",
            "create_bet",
            "insert_bet",
            "add_bet",
            "save_parsed_bet",
        ],
        user_id=user_id,
        bet_type=bet["bet_type"],
        bet_result=bet["bet_result"],
        stake_amount=bet["stake_amount"],
        odds=bet["odds"],
        created_at=datetime.now().isoformat(),
    )

    if result is not None:
        return True

    # positional fallback
    result = _call_first_existing(
        bets_db,
        [
            "save_bet",
            "create_bet",
            "insert_bet",
            "add_bet",
            "save_parsed_bet",
        ],
        user_id,
        bet["bet_type"],
        bet["bet_result"],
        bet["stake_amount"],
        bet["odds"],
    )
    return result is not None


def _period_name_today(lang: str) -> str:
    return get_text(lang, "period_today")


def _render_single_stats_block(lang: str, stats: dict[str, Any], title: str | None = None) -> str:
    body = (
        f"💰 {'Прибуток' if lang == 'ua' else 'Прибыль'}: {stats['net_profit']}\n"
        f"📈 ROI: {stats['roi']}%\n"
        f"🎯 Winrate: {stats['win_rate']}%\n"
        f"📊 {'Середній коефіцієнт' if lang == 'ua' else 'Средний коэффициент'}: {stats['avg_odds']}"
    )
    if title:
        return f"{title}\n\n{body}"
    return body


def _render_trial_pitch(lang: str, stats: dict[str, Any]) -> str:
    if lang == "ru":
        intro = "🔥 Неплохой результат." if _as_float(stats["net_profit"]) >= 0 else "⚠️ Уже видно, где ты теряешь."
        return (
            "⛔ Лимит достигнут\n\n"
            f"{_render_single_stats_block(lang, stats, '📊 За это время:')}\n\n"
            f"{intro}\n\n"
            "Но главный вопрос:\n\n"
            "👉 это система или просто короткая серия?\n\n"
            "❗ Именно здесь большинство игроков:\n"
            "— теряют прибыль\n"
            "— начинают играть агрессивнее\n"
            "— сливают банк\n\n"
            "⚡ Полный доступ нужен,\n"
            "чтобы зафиксировать и масштабировать результат\n\n"
            "👇 Не останавливайся на этом"
        )

    intro = "🔥 Непоганий результат." if _as_float(stats["net_profit"]) >= 0 else "⚠️ Уже видно, де ти втрачаєш."
    return (
        "⛔ Ліміт досягнуто\n\n"
        f"{_render_single_stats_block(lang, stats, '📊 За цей час:')}\n\n"
        f"{intro}\n\n"
        "Але головне питання:\n\n"
        "👉 це система чи просто коротка серія?\n\n"
        "❗ Саме тут більшість гравців:\n"
        "— втрачають прибуток\n"
        "— починають грати агресивніше\n"
        "— зливають банк\n\n"
        "⚡ Повний доступ потрібен,\n"
        "щоб зафіксувати і масштабувати результат\n\n"
        "👇 Не зупиняйся на цьому"
    )


async def _download_last_photo_bytes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bytes | None:
    if not update.message or not update.message.photo:
        return None

    photo = update.message.photo[-1]
    tg_file = await context.bot.get_file(photo.file_id)
    raw = await tg_file.download_as_bytearray()
    return bytes(raw)


async def process_bet_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.photo:
        return

    tg_user = update.effective_user
    user_id = tg_user.id

    create_user_if_not_exists(tg_user)
    lang = _safe_lang(user_id)

    has_access = user_has_access(user_id)
    trial_open = is_trial_available(user_id)

    if not has_access and not trial_open:
        await update.message.reply_text(
            get_text(lang, "trial_limit_push").format(
                used=get_trial_used_count(user_id),
                limit=3,
            ),
            reply_markup=access_keyboard(lang),
        )
        return

    if has_access:
        limit = get_user_daily_limit(user_id)
        used_before = count_user_photos_today(user_id)
        remaining_before = get_user_remaining_photos_today(user_id)

        if remaining_before <= 0:
            await update.message.reply_text(
                get_text(lang, "daily_limit_reached").format(limit=limit),
                reply_markup=access_keyboard(lang),
            )
            return
    else:
        limit = 3
        used_before = get_trial_used_count(user_id)
        remaining_before = get_trial_remaining(user_id)

        if remaining_before <= 0:
            start_dt = datetime.now() - timedelta(days=30)
            stats = get_basic_stats_between(user_id, start_dt, datetime.now())
            await update.message.reply_text(
                _render_trial_pitch(lang, stats),
                reply_markup=access_keyboard(lang),
            )
            return

    await update.message.reply_text(get_text(lang, "bet_analysis_started"))

    photo_bytes = await _download_last_photo_bytes(update, context)
    if not photo_bytes:
        await update.message.reply_text(get_text(lang, "bet_parse_failed"))
        return

    parsed = _parse_bet(photo_bytes)
    if not parsed:
        await update.message.reply_text(get_text(lang, "bet_parse_failed"))
        return

    log_user_photo(user_id, update.message.photo[-1].file_id)

    if not has_access:
        increment_trial_usage(user_id)

    _save_bet(user_id, parsed)

    if has_access:
        remaining_after = get_user_remaining_photos_today(user_id)
        limit_after = get_user_daily_limit(user_id)
    else:
        remaining_after = get_trial_remaining(user_id)
        limit_after = 3

    bet_type_key = "bet_type_total" if parsed["bet_type"] == "total" else "bet_type_result"
    bet_result_key = {
        "win": "bet_result_win",
        "lose": "bet_result_lose",
        "refund": "bet_result_refund",
        "pending": "bet_result_pending",
    }[parsed["bet_result"]]

    result_text = get_text(lang, "bet_saved" if parsed["bet_result"] != "pending" else "bet_pending_saved").format(
        bet_result=get_text(lang, bet_result_key),
        bet_type=get_text(lang, bet_type_key),
        stake_amount=parsed["stake_amount"],
        odds=parsed["odds"],
        remaining=remaining_after,
        limit=limit_after,
    )
    await update.message.reply_text(result_text)

    if has_access:
        return

    used_after = get_trial_used_count(user_id)
    stats = get_basic_stats_between(user_id, datetime.now() - timedelta(days=30), datetime.now())

    if used_after == 1:
        await update.message.reply_text(
            get_text(lang, "trial_after_first_push") + "\n\n" + _render_single_stats_block(lang, stats, "📊")
        )
        return

    if used_after == 3 or get_trial_remaining(user_id) <= 0:
        await update.message.reply_text(
            _render_trial_pitch(lang, stats),
            reply_markup=access_keyboard(lang),
        )
        return

    if used_after >= 2:
        await update.message.reply_text(
            get_text(lang, "trial_after_third_push") + "\n\n" + _render_single_stats_block(lang, stats, "📊")
        )
