# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
import urllib.parse

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes


def _normalize_lang(lang):
    lang = (lang or "ua").lower()
    if lang.startswith("uk"):
        return "ua"
    if lang.startswith("ru"):
        return "ru"
    if lang.startswith("en"):
        return "en"
    return "ua"


def _best_worst_market(stats):
    """Find the best and worst market/type by ROI."""
    best_name, best_roi = None, None
    worst_name, worst_roi = None, None

    all_buckets = {}
    all_buckets.update(stats.get("types", {}))
    all_buckets.update(stats.get("markets", {}))

    for name, bucket in all_buckets.items():
        stake = float(bucket.get("settled_stake") or bucket.get("stake") or 0)
        count = int(bucket.get("settled_count") or bucket.get("count") or 0)
        if stake <= 0 or count < 2:
            continue

        roi = float(bucket.get("roi") or ((bucket.get("profit", 0) / stake) * 100))
        if best_roi is None or roi > best_roi:
            best_roi, best_name = roi, name
        if worst_roi is None or roi < worst_roi:
            worst_roi, worst_name = roi, name

    return (best_name, best_roi), (worst_name, worst_roi)


def _build_wrapped_text(stats, lang, username=None, period_label=""):
    """Build a shareable weekly recap card."""
    total = int(stats.get("total_bets") or 0)
    settled = int(stats.get("settled_bets") or 0)
    wins = int(stats.get("wins") or 0)
    profit = float(stats.get("net_profit") or 0.0)
    roi = float(stats.get("roi") or 0.0)
    avg_odds = float(stats.get("avg_odds") or 0.0)
    best_streak = int(stats.get("best_win_streak") or 0)
    winrate = (wins / settled * 100) if settled > 0 else 0

    (best_name, best_roi), (worst_name, worst_roi) = _best_worst_market(stats)

    trend = "🚀" if profit > 0 else ("📉" if profit < 0 else "⚖️")
    profit_sign = "+" if profit >= 0 else ""
    name_part = f"@{username}" if username else ""

    if lang == "ru":
        lines = [
            f"🏁 *ИТОГИ НЕДЕЛИ* {trend}",
            f"{name_part}" if name_part else "",
            "",
            f"💰 Прибыль: *{profit_sign}{profit:.0f}*",
            f"📈 ROI: *{roi:+.1f}%*",
            f"🎯 Winrate: *{winrate:.0f}%* ({wins}/{settled})",
            f"📊 Средний кэф: {avg_odds:.2f}",
            f"🧾 Ставок: {total}",
            f"🔥 Лучшая серия: {best_streak}",
        ]
        if best_name:
            lines.append(f"\n✅ Лучший рынок: {best_name} ({best_roi:+.0f}%)")
        if worst_name and worst_name != best_name:
            lines.append(f"⚠️ Слабое место: {worst_name} ({worst_roi:+.0f}%)")
        lines.append("\n📲 Веду статистику в @bet_tracker_stats_bot")
    elif lang == "en":
        lines = [
            f"🏁 *WEEKLY RECAP* {trend}",
            f"{name_part}" if name_part else "",
            "",
            f"💰 Profit: *{profit_sign}{profit:.0f}*",
            f"📈 ROI: *{roi:+.1f}%*",
            f"🎯 Winrate: *{winrate:.0f}%* ({wins}/{settled})",
            f"📊 Avg odds: {avg_odds:.2f}",
            f"🧾 Bets: {total}",
            f"🔥 Best streak: {best_streak}",
        ]
        if best_name:
            lines.append(f"\n✅ Best market: {best_name} ({best_roi:+.0f}%)")
        if worst_name and worst_name != best_name:
            lines.append(f"⚠️ Weak spot: {worst_name} ({worst_roi:+.0f}%)")
        lines.append("\n📲 Tracking with @bet_tracker_stats_bot")
    else:
        lines = [
            f"🏁 *ПІДСУМКИ ТИЖНЯ* {trend}",
            f"{name_part}" if name_part else "",
            "",
            f"💰 Прибуток: *{profit_sign}{profit:.0f}*",
            f"📈 ROI: *{roi:+.1f}%*",
            f"🎯 Winrate: *{winrate:.0f}%* ({wins}/{settled})",
            f"📊 Середній коеф: {avg_odds:.2f}",
            f"🧾 Ставок: {total}",
            f"🔥 Найкраща серія: {best_streak}",
        ]
        if best_name:
            lines.append(f"\n✅ Кращий ринок: {best_name} ({best_roi:+.0f}%)")
        if worst_name and worst_name != best_name:
            lines.append(f"⚠️ Слабке місце: {worst_name} ({worst_roi:+.0f}%)")
        lines.append("\n📲 Веду статистику в @bet_tracker_stats_bot")

    return "\n".join(line for line in lines if line is not None)


def _no_data_text(lang):
    texts = {
        "ua": (
            "🏁 *Підсумки тижня*\n\n"
            "За останні 7 днів ще недостатньо ставок\n"
            "для підсумку.\n\n"
            "Додай кілька ставок цього тижня\n"
            "і отримаєш красиву картку статистики! 📊"
        ),
        "ru": (
            "🏁 *Итоги недели*\n\n"
            "За последние 7 дней ещё недостаточно\n"
            "ставок для итога.\n\n"
            "Добавь несколько ставок на этой неделе\n"
            "и получишь красивую карточку статистики! 📊"
        ),
        "en": (
            "🏁 *Weekly Recap*\n\n"
            "Not enough bets in the last 7 days\n"
            "for a recap yet.\n\n"
            "Add a few bets this week\n"
            "and get a beautiful stats card! 📊"
        ),
    }
    return texts.get(lang, texts["ua"])


async def send_weekly_wrap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    user_id = update.effective_user.id

    from db import get_user, should_include_trial
    from bets_db import get_full_stats_between

    user = get_user(user_id) or {}
    lang = _normalize_lang(user.get("lang"))
    username = user.get("username")

    end_dt = datetime.now()
    start_dt = end_dt - timedelta(days=7)
    include_trial = should_include_trial(user_id)

    try:
        stats = get_full_stats_between(user_id, start_dt, end_dt, include_trial)
    except Exception as exc:
        print(f"weekly_wrap stats error: {exc}")
        stats = None

    if not stats or int(stats.get("total_bets") or 0) < 3:
        await update.message.reply_text(
            _no_data_text(lang),
            parse_mode="Markdown",
        )
        return

    wrapped_text = _build_wrapped_text(stats, lang, username)

    share_labels = {
        "ua": "📤 Поділитись результатом",
        "ru": "📤 Поделиться результатом",
        "en": "📤 Share result",
    }
    share_text = wrapped_text.replace("*", "")
    encoded = urllib.parse.quote(share_text)
    share_url = f"https://t.me/share/url?url=&text={encoded}"
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton(
            share_labels.get(lang, share_labels["ua"]),
            url=share_url,
        )
    ]])

    await update.message.reply_text(
        wrapped_text,
        parse_mode="Markdown",
        reply_markup=keyboard,
    )


async def send_weekly_wrap_broadcast(bot):
    pass
