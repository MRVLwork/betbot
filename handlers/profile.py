# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bets_db import get_full_stats_between
from db import (
    ALL_ACHIEVEMENTS,
    check_and_unlock_achievements,
    get_streak,
    get_user,
    get_user_achievements,
    get_user_rank_percentile,
    get_xp,
    user_has_access,
)


LEVEL_NAMES = {
    "ua": {1: "Новачок", 2: "Аналітик", 3: "Стратег", 4: "Профі", 5: "Шарп"},
    "ru": {1: "Новичок", 2: "Аналитик", 3: "Стратег", 4: "Профи", 5: "Шарп"},
    "en": {1: "Beginner", 2: "Analyst", 3: "Strategist", 4: "Pro", 5: "Sharp"},
}

LEVEL_XP = (0, 500, 1500, 3000, 6000, 999999)


def _normalize_lang(lang: str) -> str:
    lang = (lang or "ua").lower()
    if lang.startswith("uk") or lang.startswith("ua"):
        return "ua"
    if lang.startswith("ru"):
        return "ru"
    return "en"


def _xp_progress_bar(current_xp: int, level: int) -> str:
    if level >= 5:
        return "██████████ MAX"

    level_start = LEVEL_XP[level - 1]
    level_end = LEVEL_XP[level]
    progress = max(0, current_xp - level_start)
    total = max(1, level_end - level_start)

    filled = max(0, min(10, int((progress / total) * 10)))
    empty = 10 - filled
    bar = ("█" * filled) + ("░" * empty)
    return f"{bar} {progress}/{total}"


def _achievements_block(unlocked: list[str], lang: str) -> str:
    all_ids = list(ALL_ACHIEVEMENTS.keys())[:6]
    lines: list[str] = []
    name_key = f"name_{lang}" if lang in ("ua", "ru", "en") else "name_ua"

    for achievement_id in all_ids:
        achievement = ALL_ACHIEVEMENTS[achievement_id]
        if achievement_id in unlocked:
            lines.append(f"{achievement['emoji']} {achievement.get(name_key, achievement['name_ua'])}")
        else:
            lines.append("🔒 ???")

    unlocked_count = sum(1 for achievement_id in ALL_ACHIEVEMENTS if achievement_id in unlocked)
    total_count = len(ALL_ACHIEVEMENTS)

    result = " | ".join(lines[:3]) + "\n" + " | ".join(lines[3:6]) + "\n"
    if lang == "ua":
        result += f"({unlocked_count}/{total_count} розблоковано)"
    elif lang == "ru":
        result += f"({unlocked_count}/{total_count} разблокировано)"
    else:
        result += f"({unlocked_count}/{total_count} unlocked)"
    return result


async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    user_id = update.effective_user.id
    tg_user = update.effective_user
    user = get_user(user_id) or {}
    lang = _normalize_lang(user.get("lang") or "ua")

    newly_unlocked = check_and_unlock_achievements(user_id)

    xp_data = get_xp(user_id)
    total_xp = int(xp_data["total_xp"])
    level = int(xp_data["current_level"])
    level_name = LEVEL_NAMES.get(lang, LEVEL_NAMES["ua"]).get(level, "")
    progress_bar = _xp_progress_bar(total_xp, level)

    streak_data = get_streak(user_id)
    current_streak = int(streak_data.get("current_streak") or 0)

    end_dt = datetime.now()
    start_dt = end_dt - timedelta(days=30)
    stats = get_full_stats_between(user_id, start_dt, end_dt, include_trial=True)
    roi = round(float(stats.get("roi", 0) or 0), 2)
    winrate = round(float(stats.get("win_rate", 0) or 0), 2)
    total_bets = int(stats.get("total_bets") or 0)

    rank = int(get_user_rank_percentile(user_id))
    top_percent = max(1, 100 - rank)
    unlocked = get_user_achievements(user_id)

    plan = (user.get("plan") or "trial").lower()
    has_access = user_has_access(user_id)
    if not has_access:
        plan_label = "Trial 🔸"
    elif plan == "vip":
        plan_label = "VIP ⭐"
    else:
        plan_label = "Basic 🔹"

    username = f"@{tg_user.username}" if tg_user.username else (tg_user.first_name or "Беттер")
    roi_str = f"+{roi}%" if roi > 0 else f"{roi}%"
    roi_emoji = "📈" if roi >= 0 else "📉"

    if lang == "ua":
        text = (
            f"👤 {username}\n"
            f"📋 План: {plan_label}\n\n"
            f"🏅 Рівень {level} - {level_name}\n"
            f"{progress_bar}\n"
            f"💎 {total_xp} XP\n\n"
            f"📊 Статистика за 30 днів:\n"
            f"{roi_emoji} ROI: {roi_str} | 🎯 Winrate: {winrate}%\n"
            f"📝 Ставок: {total_bets}\n\n"
            f"🔥 Streak дисципліни: {current_streak} днів\n"
            f"🌍 Рейтинг: топ {top_percent}% беттерів\n\n"
            f"🏆 Досягнення:\n"
            f"{_achievements_block(unlocked, lang)}"
        )
    elif lang == "ru":
        text = (
            f"👤 {username}\n"
            f"📋 План: {plan_label}\n\n"
            f"🏅 Уровень {level} - {level_name}\n"
            f"{progress_bar}\n"
            f"💎 {total_xp} XP\n\n"
            f"📊 Статистика за 30 дней:\n"
            f"{roi_emoji} ROI: {roi_str} | 🎯 Winrate: {winrate}%\n"
            f"📝 Ставок: {total_bets}\n\n"
            f"🔥 Streak дисциплины: {current_streak} дней\n"
            f"🌍 Рейтинг: топ {top_percent}% беттеров\n\n"
            f"🏆 Достижения:\n"
            f"{_achievements_block(unlocked, lang)}"
        )
    else:
        text = (
            f"👤 {username}\n"
            f"📋 Plan: {plan_label}\n\n"
            f"🏅 Level {level} - {level_name}\n"
            f"{progress_bar}\n"
            f"💎 {total_xp} XP\n\n"
            f"📊 Stats last 30 days:\n"
            f"{roi_emoji} ROI: {roi_str} | 🎯 Winrate: {winrate}%\n"
            f"📝 Bets: {total_bets}\n\n"
            f"🔥 Discipline streak: {current_streak} days\n"
            f"🌍 Rank: top {top_percent}% bettors\n\n"
            f"🏆 Achievements:\n"
            f"{_achievements_block(unlocked, lang)}"
        )

    share_labels = {"ua": "📤 Моя картка", "ru": "📤 Моя карточка", "en": "📤 My card"}
    upgrade_labels = {"ua": "💳 Підписка", "ru": "💳 Подписка", "en": "💳 Subscription"}
    ref_labels = {"ua": "👥 Реферали", "ru": "👥 Рефералы", "en": "👥 Referrals"}

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(share_labels.get(lang, "📤 My card"), callback_data="profile_share_card")],
        [InlineKeyboardButton(upgrade_labels.get(lang, "💳 Subscription"), callback_data="profile_upgrade")],
        [InlineKeyboardButton(ref_labels.get(lang, "👥 Referrals"), callback_data="profile_referrals")],
    ])

    await update.message.reply_text(text, reply_markup=keyboard)

    if newly_unlocked:
        for achievement_id in newly_unlocked:
            achievement = ALL_ACHIEVEMENTS.get(achievement_id, {})
            emoji = achievement.get("emoji", "🏆")
            name_key = f"name_{lang}"
            name = achievement.get(name_key, achievement.get("name_ua", achievement_id))
            xp_reward = int(achievement.get("xp_reward") or 0)
            if lang == "ua":
                await update.message.reply_text(f"🎉 Нове досягнення!\n\n{emoji} {name}\n+{xp_reward} XP")
            elif lang == "ru":
                await update.message.reply_text(f"🎉 Новое достижение!\n\n{emoji} {name}\n+{xp_reward} XP")
            else:
                await update.message.reply_text(f"🎉 New achievement!\n\n{emoji} {name}\n+{xp_reward} XP")


async def profile_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    user = get_user(user_id) or {}
    lang = _normalize_lang(user.get("lang") or "ua")

    if query.data == "profile_share_card":
        texts = {
            "ua": "🛠 Картка профілю в розробці. Скоро буде доступна!",
            "ru": "🛠 Карточка профиля в разработке. Скоро будет доступна!",
            "en": "🛠 Profile card coming soon!",
        }
        await query.message.reply_text(
            texts.get(lang, texts["ua"])
        )

    elif query.data == "profile_upgrade":
        from keyboards import access_keyboard

        texts = {
            "ua": "💳 Обери тариф:",
            "ru": "💳 Выбери тариф:",
            "en": "💳 Choose your plan:",
        }
        await query.message.reply_text(
            texts.get(lang, texts["en"]),
            reply_markup=access_keyboard(lang),
        )

    elif query.data == "profile_referrals":
        bot = context.bot
        bot_username = bot.username or "bet_tracker_stats_bot"
        ref_link = f"https://t.me/{bot_username}?start=ref_{user_id}"
        texts = {
            "ua": (
                f"👥 Твоє реферальне посилання:\n\n{ref_link}\n\n"
                f"За кожного друга який оформить підписку\n"
                f"ти отримаєш 7 днів безкоштовно! 🎁"
            ),
            "ru": (
                f"👥 Твоя реферальная ссылка:\n\n{ref_link}\n\n"
                f"За каждого друга который оформит подписку\n"
                f"ты получишь 7 дней бесплатно! 🎁"
            ),
            "en": (
                f"👥 Your referral link:\n\n{ref_link}\n\n"
                f"For every friend who subscribes\n"
                f"you get 7 days free! 🎁"
            ),
        }
        await query.message.reply_text(texts.get(lang, texts["en"]))
