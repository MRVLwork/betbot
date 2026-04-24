# -*- coding: utf-8 -*-
from io import BytesIO

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InputFile, Update
from telegram.ext import ContextTypes

from db import get_broadcast_recipients, get_user, user_has_access, is_trial_available
from services.weekly_card_service import generate_weekly_card, get_user_rank_percentile, get_week_stats


def _share_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📤 Поділитись", url="https://t.me/bet_tracker_stats_bot")]
    ])


def _weekly_caption(lang: str) -> str:
    lang = (lang or "en").lower()
    if lang.startswith("ru"):
        return "📊 Твоя неделя! Жми поделиться 👇"
    if lang.startswith("en"):
        return "📊 Your week! Tap share 👇"
    return "📊 Твій тиждень! Тисни поділитись 👇"


def _resolve_username(user: dict | None, user_id: int) -> str:
    if user and user.get("username"):
        return str(user["username"]).replace("@", "")
    if user and user.get("first_name"):
        return str(user["first_name"])
    return str(user_id)


async def _send_weekly_card_to_user(bot, user_id: int):
    user = get_user(user_id)
    has_access = user_has_access(user_id)
    trial_started = user.get("trial_started_at") if user else None
    in_trial = (
        not has_access
        and trial_started is not None
        and is_trial_available(user_id)
    )

    if not user or (not has_access and not in_trial):
        return

    stats = get_week_stats(user_id)
    rank_percentile = get_user_rank_percentile(user_id)
    username = _resolve_username(user, user_id)
    image_bytes = generate_weekly_card(user_id, stats, username, rank_percentile)
    photo = InputFile(BytesIO(image_bytes), filename="weekly_wrap.png")

    await bot.send_photo(
        chat_id=user_id,
        photo=photo,
        caption=_weekly_caption(user.get("lang") or "ua"),
        reply_markup=_share_keyboard(),
    )


async def send_weekly_wrap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    user_id = update.effective_user.id
    user = get_user(user_id)
    has_access = user_has_access(user_id)
    trial_started = (user or {}).get("trial_started_at")
    in_trial = (
        not has_access
        and trial_started is not None
        and is_trial_available(user_id)
    )

    if not has_access and not in_trial:
        lang = (user or {}).get("lang", "ua")
        texts = {
            "ua": " Для перегляду Wrapped потрібен активний доступ.",
            "ru": " Для просмотра Wrapped нужен активный доступ.",
            "en": " Active access required to view Wrapped.",
        }
        await update.message.reply_text(
            texts.get(lang, texts["en"])
        )
        return

    await _send_weekly_card_to_user(context.bot, user_id)


async def send_weekly_wrap_broadcast(bot):
    user_ids = get_broadcast_recipients(lang_tag="alllangs", audience_tag="all")
    for user_id in user_ids:
        try:
            await _send_weekly_card_to_user(bot, user_id)
        except Exception:
            pass
