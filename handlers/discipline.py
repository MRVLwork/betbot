from datetime import datetime, timedelta

from telegram import Update
from telegram.ext import ContextTypes

from bets_db import _get_rows_between, check_discipline_for_day
from db import get_streak, get_user, update_streak


def _normalize_lang(lang: str) -> str:
    lang = (lang or "en").lower()
    if lang.startswith("uk") or lang.startswith("ua"):
        return "ua"
    if lang.startswith("ru"):
        return "ru"
    return "en"


def _streak_message(lang: str, streak: int, best_streak: int) -> str:
    if lang == "ua":
        return (
            f"🔥 Серія дисципліни: {streak} днів\n\n"
            "✅ Не більше 3 ставок на день\n"
            "✅ Без ставок на тілті\n\n"
            f"🏆 Рекорд: {best_streak} днів"
        )
    if lang == "ru":
        return (
            f"🔥 Серия дисциплины: {streak} дней\n\n"
            "✅ Не больше 3 ставок в день\n"
            "✅ Без ставок на тилте\n\n"
            f"🏆 Рекорд: {best_streak} дней"
        )
    return (
        f"🔥 Discipline streak: {streak} days\n\n"
        "✅ No more than 3 bets per day\n"
        "✅ No bets made on tilt\n\n"
        f"🏆 Best: {best_streak} days"
    )


def _streak_broken_message(lang: str, old_streak: int) -> str:
    if lang == "ua":
        return f"💔 Твоя серія {old_streak} днів перервана.\nПочинаємо з нуля 💪"
    if lang == "ru":
        return f"💔 Твоя серия {old_streak} дней прервана.\nНачинаем с нуля 💪"
    return f"💔 Your {old_streak}-day streak is broken.\nStarting again from zero 💪"


async def show_streak(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    user_id = update.effective_user.id
    user = get_user(user_id)
    lang = _normalize_lang(user["lang"] if user and user.get("lang") else "en")

    yesterday = (datetime.now() - timedelta(days=1)).date()
    start_dt = datetime.combine(yesterday, datetime.min.time())
    end_dt = start_dt + timedelta(days=1)
    yesterday_rows = _get_rows_between(user_id, start_dt, end_dt, include_trial=False)

    streak_before = get_streak(user_id)
    current_streak = streak_before["current_streak"]
    best_streak = streak_before["best_streak"]

    if yesterday_rows:
        discipline_ok = check_discipline_for_day(user_id, yesterday)
        new_streak = update_streak(user_id, discipline_ok)
        streak_after = get_streak(user_id)

        if not discipline_ok and current_streak > 0 and new_streak == 0:
            await update.message.reply_text(_streak_broken_message(lang, current_streak))
            return

        current_streak = streak_after["current_streak"]
        best_streak = streak_after["best_streak"]

    await update.message.reply_text(_streak_message(lang, current_streak, best_streak))
