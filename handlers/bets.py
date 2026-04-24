# -*- coding: utf-8 -*-
from datetime import datetime

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bets_db import create_bet, get_basic_stats_between, get_tilt_signal_context, update_bet_emotion
from db import (
    TRIAL_SCREEN_LIMIT,
    XP_TABLE,
    add_xp,
    get_subscription_type,
    get_user,
    user_has_access,
    get_user_daily_limit,
    count_user_photos_today,
    get_user_remaining_photos_today,
    log_user_photo,
    is_trial_available,
    get_trial_remaining,
    get_trial_used_count,
    increment_trial_usage,
    get_trial_start,
    should_include_trial,
)
from keyboards import access_keyboard, welcome_offer_keyboard
from languages import get_text
from services.ai_service import analyze_basic_bet_screenshot
from handlers.tools import handle_ai_analysis_input


LEVEL_NAMES = {
    "ua": {1: "Новачок", 2: "Аналітик", 3: "Стратег", 4: "Профі", 5: "Шарп"},
    "ru": {1: "Новичок", 2: "Аналитик", 3: "Стратег", 4: "Профи", 5: "Шарп"},
    "en": {1: "Beginner", 2: "Analyst", 3: "Strategist", 4: "Pro", 5: "Sharp"},
}


def _normalize_lang(lang: str) -> str:
    lang = (lang or "en").lower()
    if lang.startswith("uk") or lang.startswith("ua"):
        return "ua"
    if lang.startswith("ru"):
        return "ru"
    return "en"


def _result_label(lang: str, result: str) -> str:
    if result == "win":
        return get_text(lang, "bet_result_win")
    if result == "lose":
        return get_text(lang, "bet_result_lose")
    if result == "refund":
        return get_text(lang, "bet_result_refund")
    if result == "pending":
        return get_text(lang, "bet_result_pending")
    return result


def _bet_type_label(lang: str, bet_type: str | None = None, bet_market: str | None = None) -> str:
    lang = _normalize_lang(lang)

    labels = {
        "ua": {
            "1x2": "1X2",
            "total": "тотал",
            "btts": "обидві заб'ють",
            "handicap": "фора",
            "double_chance": "1X/2X",
            "corners": "кутові",
            "cards": "картки",
            "other": "інше",
            "result": "результат",
        },
        "ru": {
            "1x2": "1X2",
            "total": "тотал",
            "btts": "обе забьют",
            "handicap": "фора",
            "double_chance": "1X/2X",
            "corners": "угловые",
            "cards": "карточки",
            "other": "другое",
            "result": "результат",
        },
        "en": {
            "1x2": "1X2",
            "total": "total",
            "btts": "both teams to score",
            "handicap": "handicap",
            "double_chance": "1X/2X",
            "corners": "corners",
            "cards": "cards",
            "other": "other",
            "result": "result",
        },
    }

    if bet_market:
        return labels.get(lang, labels["en"]).get(bet_market, bet_market)
    if bet_type:
        return labels.get(lang, labels["en"]).get(bet_type, bet_type)
    return "-"


def _daily_limit_reached_text(lang: str, plan: str, limit: int) -> str:
    lang = _normalize_lang(lang)
    plan = (plan or "basic").lower()

    texts = {
        "ua": {
            "trial": f"🚫 Ліміт на сьогодні: {limit}/{limit} скрінів використано\n\nВ Basic: 15 скрінів/день\nВ VIP: 30 скрінів/день\n\n👇 Оновити план",
            "basic": f"🚫 Ліміт на сьогодні: {limit}/{limit} скрінів використано\n\nВ VIP: 30 скрінів/день + AI Тренер\n\n👇 Оновити до VIP",
            "vip": f"🚫 Ліміт на сьогодні: {limit}/{limit} скрінів використано\nПовернись завтра 🌙",
        },
        "ru": {
            "trial": f"🚫 Лимит на сегодня: {limit}/{limit} скринов использовано\n\nВ Basic: 15 скринов/день\nВ VIP: 30 скринов/день\n\n👇 Обновить план",
            "basic": f"🚫 Лимит на сегодня: {limit}/{limit} скринов использовано\n\nВ VIP: 30 скринов/день + AI Тренер\n\n👇 Обновить до VIP",
            "vip": f"🚫 Лимит на сегодня: {limit}/{limit} скринов использовано\nВозвращайся завтра 🌙",
        },
        "en": {
            "trial": f"🚫 Today's limit reached: {limit}/{limit} screenshots used\n\nIn Basic: 15 screenshots/day\nIn VIP: 30 screenshots/day\n\n👇 Upgrade plan",
            "basic": f"🚫 Today's limit reached: {limit}/{limit} screenshots used\n\nIn VIP: 30 screenshots/day + AI Coach\n\n👇 Upgrade to VIP",
            "vip": f"🚫 Today's limit reached: {limit}/{limit} screenshots used\nCome back tomorrow 🌙",
        },
    }

    return texts.get(lang, texts["en"]).get(plan, texts.get(lang, texts["en"])["basic"])


def _trial_progress_text(lang: str, used_today: int, remaining_today: int, days_left: int) -> str:
    lang = _normalize_lang(lang)

    if lang == "ua":
        return (
            f"✅ Скрін зараховано.\n"
            f"Сьогодні використано: {used_today}/{TRIAL_SCREEN_LIMIT}\n"
            f"Залишилось сьогодні: {remaining_today}\n"
            f"Днів пробного доступу: {days_left}"
        )
    if lang == "ru":
        return (
            f"✅ Скрин засчитан.\n"
            f"Сегодня использовано: {used_today}/{TRIAL_SCREEN_LIMIT}\n"
            f"Осталось сегодня: {remaining_today}\n"
            f"Дней пробного доступа: {days_left}"
        )
    return (
        f"Screenshot saved.\n"
        f"Used today: {used_today}/{TRIAL_SCREEN_LIMIT}\n"
        f"Remaining today: {remaining_today}\n"
        f"Trial days left: {days_left}"
    )


def _trial_fail_text(lang: str, used_trial: int, remaining_trial: int) -> str:
    lang = _normalize_lang(lang)

    if lang == "ua":
        return (
            "⚠️ Цей скрін не вдалося розпізнати, але він зарахований у trial.\n"
            f"Залишилось днів пробного доступу: {remaining_trial}"
        )
    if lang == "ru":
        return (
            "⚠️ Этот скрин не удалось распознать, но он засчитан в trial.\n"
            f"Осталось дней пробного доступа: {remaining_trial}"
        )
    return (
        "⚠️ This screenshot could not be recognized, but it was counted in the trial.\n"
        f"Trial days remaining: {remaining_trial}"
    )


def _build_trial_pitch(lang: str, stats: dict, used_trial: int) -> str | None:
    if used_trial < 3:
        return None

    lang = _normalize_lang(lang)
    profit = float(stats.get("net_profit", 0) or 0)
    roi = float(stats.get("roi", 0) or 0)
    win_rate = float(stats.get("win_rate", 0) or 0)
    avg_odds = float(stats.get("avg_odds", 0) or 0)

    if lang == "ua":
        return (
            "📊 Уже вимальовується перша картина\n\n"
            f"💰 Прибуток: {profit}\n"
            f"📈 ROI: {roi}%\n"
            f"🎯 Winrate: {win_rate}%\n"
            f"📊 Середній коефіцієнт: {avg_odds}\n\n"
            "Ще кілька ставок покажуть, чи це система, чи випадковість.\n\n"
            "👇 Продовжуй аналіз або відкрий повний доступ"
        )
    if lang == "ru":
        return (
            "📊 Уже вырисовывается первая картина\n\n"
            f"💰 Прибыль: {profit}\n"
            f"📈 ROI: {roi}%\n"
            f"🎯 Winrate: {win_rate}%\n"
            f"📊 Средний коэффициент: {avg_odds}\n\n"
            "Ещё несколько ставок покажут, это система или случайность.\n\n"
            "👇 Продолжай анализ или открой полный доступ"
        )
    return (
        "📊 The first picture is already forming\n\n"
        f"💰 Profit: {profit}\n"
        f"📈 ROI: {roi}%\n"
        f"🎯 Winrate: {win_rate}%\n"
        f"📊 Average odds: {avg_odds}\n\n"
        "A few more bets will show whether this is a system or just variance.\n\n"
        "👇 Keep going or unlock full access"
    )


def _trial_pitch_after_3(lang: str, stats: dict) -> str:
    roi = stats.get("roi", 0)
    winrate = stats.get("win_rate", 0)
    profit = stats.get("net_profit", 0)

    if lang == "ua":
        trend = "в плюсі 📈" if profit > 0 else "в мінусі 📉"
        return (
            f"📊 Вже є перша картина\n\n"
            f"ROI: {roi}% | Winrate: {winrate}%\n"
            f"Результат: {trend}\n\n"
            f"Але 3 ставки - це ще не дистанція.\n"
            f"Реальна статистика формується від 20+ ставок.\n\n"
            f"У тебе залишилось ще 2 скріни сьогодні.\n"
            f"Використай їх - картина стане чіткішою 👇"
        )
    if lang == "ru":
        trend = "в плюсе 📈" if profit > 0 else "в минусе 📉"
        return (
            f"📊 Уже есть первая картина\n\n"
            f"ROI: {roi}% | Winrate: {winrate}%\n"
            f"Результат: {trend}\n\n"
            f"Но 3 ставки - это ещё не дистанция.\n"
            f"Реальная статистика формируется от 20+ ставок.\n\n"
            f"У тебя осталось ещё 2 скрина сегодня.\n"
            f"Используй их - картина станет чётче 👇"
        )
    trend = "in profit 📈" if profit > 0 else "in loss 📉"
    return (
        f"📊 First picture is forming\n\n"
        f"ROI: {roi}% | Winrate: {winrate}%\n"
        f"Result: {trend}\n\n"
        f"But 3 bets is not a real distance yet.\n"
        f"Real stats form from 20+ bets.\n\n"
        f"You have 2 screenshots left today.\n"
        f"Use them - the picture will get clearer 👇"
    )


def _trial_pitch_after_5(lang: str, stats: dict, days_left: int) -> str:
    roi = stats.get("roi", 0)
    winrate = stats.get("win_rate", 0)
    profit = stats.get("net_profit", 0)
    _ = days_left

    if lang == "ua":
        if profit > 0:
            return (
                f"🔥 Денний ліміт вичерпано\n\n"
                f"Твоя статистика сьогодні:\n"
                f"💰 Прибуток: +{profit}\n"
                f"📈 ROI: +{roi}%\n"
                f"🎯 Winrate: {winrate}%\n\n"
                f"Ти в плюсі - і це тільки початок.\n\n"
                f"Проблема:\n"
                f"Без системи цей плюс легко втратити.\n"
                f"Більшість беттерів зливають прибуток\n"
                f"через 2-3 тижні через відсутність контролю.\n\n"
                f"Basic план вирішує це:\n"
                f"Аналіз 15 ставок на день\n"
                f"Повна статистика і аналітика\n"
                f"Контроль емоцій і тілту\n\n"
                f"💡 $5 на місяць - менше ніж одна\n"
                f"програшна ставка через емоції.\n\n"
                f"👇 Зафіксуй результат - купи доступ"
            )
        return (
            f"📊 Денний ліміт вичерпано\n\n"
            f"Твоя статистика сьогодні:\n"
            f"💰 Результат: {profit}\n"
            f"📈 ROI: {roi}%\n"
            f"🎯 Winrate: {winrate}%\n\n"
            f"Поки в мінусі - але це нормально\n"
            f"для початку без системи.\n\n"
            f"Важливо знати:\n"
            f"73% беттерів в мінусі саме через\n"
            f"відсутність аналізу своїх ставок.\n\n"
            f"Basic план показує де ти зливаєш:\n"
            f"Які типи ставок збиткові\n"
            f"Коли ставиш на емоціях\n"
            f"Патерни програшів\n\n"
            f"💡 Одна виправлена помилка окупить\n"
            f"підписку за перший тиждень.\n\n"
            f"👇 Почни виправляти зараз"
        )

    if lang == "ru":
        if profit > 0:
            return (
                f"🔥 Дневной лимит исчерпан\n\n"
                f"Твоя статистика сегодня:\n"
                f"💰 Прибыль: +{profit}\n"
                f"📈 ROI: +{roi}%\n"
                f"🎯 Winrate: {winrate}%\n\n"
                f"Ты в плюсе - и это только начало.\n\n"
                f"Проблема:\n"
                f"Без системы этот плюс легко потерять.\n"
                f"Большинство беттеров сливают прибыль\n"
                f"через 2-3 недели без контроля.\n\n"
                f"Basic план решает это:\n"
                f"Анализ 15 ставок в день\n"
                f"Полная статистика и аналитика\n"
                f"Контроль эмоций и тилта\n\n"
                f"💡 $5 в месяц - меньше чем одна\n"
                f"проигрышная ставка на эмоциях.\n\n"
                f"👇 Зафиксируй результат - купи доступ"
            )
        return (
            f"📊 Дневной лимит исчерпан\n\n"
            f"Твоя статистика сегодня:\n"
            f"💰 Результат: {profit}\n"
            f"📈 ROI: {roi}%\n"
            f"🎯 Winrate: {winrate}%\n\n"
            f"Пока в минусе - но это нормально\n"
            f"для начала без системы.\n\n"
            f"Важно знать:\n"
            f"73% беттеров в минусе именно из-за\n"
            f"отсутствия анализа своих ставок.\n\n"
            f"Basic план показывает где ты сливаешь:\n"
            f"Какие типы ставок убыточны\n"
            f"Когда ставишь на эмоциях\n"
            f"Паттерны проигрышей\n\n"
            f"💡 Одна исправленная ошибка окупит\n"
            f"подписку за первую неделю.\n\n"
            f"👇 Начни исправлять сейчас"
        )

    if profit > 0:
        return (
            f"🔥 Daily limit reached\n\n"
            f"Your stats today:\n"
            f"💰 Profit: +{profit}\n"
            f"📈 ROI: +{roi}%\n"
            f"🎯 Winrate: {winrate}%\n\n"
            f"You're in profit - and this is just the start.\n\n"
            f"The problem:\n"
            f"Without a system, this profit is easy to lose.\n"
            f"Most bettors lose their gains within weeks.\n\n"
            f"Basic plan fixes this:\n"
            f"15 screenshots per day\n"
            f"Full stats and analytics\n"
            f"Emotion and tilt control\n\n"
            f"💡 $5/month - less than one emotional loss.\n\n"
            f"👇 Lock in your result - get access"
        )
    return (
        f"📊 Daily limit reached\n\n"
        f"Your stats today:\n"
        f"💰 Result: {profit}\n"
        f"📈 ROI: {roi}%\n"
        f"🎯 Winrate: {winrate}%\n\n"
        f"Currently at a loss - but that's normal\n"
        f"without a system.\n\n"
        f"Key insight:\n"
        f"73% of bettors lose because they never\n"
        f"analyze their own betting patterns.\n\n"
        f"Basic plan shows where you're losing:\n"
        f"Which bet types are draining you\n"
        f"When you bet on emotions\n"
        f"Your losing patterns\n\n"
        f"💡 One fixed mistake pays for the\n"
        f"subscription in the first week.\n\n"
        f"👇 Start fixing it now"
    )


def _build_limit_pitch(lang: str, stats: dict) -> str:
    lang = _normalize_lang(lang)
    profit = float(stats.get("net_profit", 0) or 0)
    roi = float(stats.get("roi", 0) or 0)
    win_rate = float(stats.get("win_rate", 0) or 0)
    avg_odds = float(stats.get("avg_odds", 0) or 0)

    prefixes = {
        "ua": "⛔ Твій 7-денний пробний доступ завершено.\n\n",
        "ru": "⛔ Твой 7-дневный пробный доступ завершён.\n\n",
        "en": "⛔ Your 7-day free trial has ended.\n\n",
    }
    prefix = prefixes.get(lang, prefixes["en"])

    if lang == "ua":
        return prefix + (
            "📊 За цей час:\n"
            f"💰 Прибуток: {profit}\n"
            f"📈 ROI: {roi}%\n"
            f"🎯 Winrate: {win_rate}%\n"
            f"📊 Середній коефіцієнт: {avg_odds}\n\n"
            "Щоб побачити повну картину та продовжити аналіз, відкрий доступ."
        )
    if lang == "ru":
        return prefix + (
            "📊 За это время:\n"
            f"💰 Прибыль: {profit}\n"
            f"📈 ROI: {roi}%\n"
            f"🎯 Winrate: {win_rate}%\n"
            f"📊 Средний коэффициент: {avg_odds}\n\n"
            "Чтобы увидеть полную картину и продолжить анализ, открой доступ."
        )
    return prefix + (
        "📊 So far:\n"
        f"💰 Profit: {profit}\n"
        f"📈 ROI: {roi}%\n"
        f"🎯 Winrate: {win_rate}%\n"
        f"📊 Average odds: {avg_odds}\n\n"
        "Unlock full access to continue the analysis."
    )


def _emotion_prompt_text(lang: str) -> str:
    if lang == "ua":
        return "Як ти себе почував перед цією ставкою?"
    if lang == "ru":
        return "Как ты себя чувствовал перед этой ставкой?"
    return "How did you feel before this bet?"


def _emotion_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("😤 Тільт", callback_data="emotion_tilt")],
        [InlineKeyboardButton("😰 Тривога", callback_data="emotion_anxiety")],
        [InlineKeyboardButton("😎 Впевнений", callback_data="emotion_confident")],
        [InlineKeyboardButton("🤔 Нейтрально", callback_data="emotion_neutral")],
    ])


def _emotion_keyboard(lang: str = "ua") -> InlineKeyboardMarkup:
    if lang == "ru":
        buttons = [
            "😤 Тилт",
            "😰 Тревога",
            "😎 Уверен",
            "🤔 Нейтрально",
        ]
    elif lang == "en":
        buttons = [
            "😤 Tilt",
            "😰 Anxious",
            "😎 Confident",
            "🤔 Neutral",
        ]
    else:
        buttons = [
            "😤 Тільт",
            "😰 Тривога",
            "😎 Впевнений",
            "🤔 Нейтрально",
        ]

    callback_codes = [
        "emotion_tilt",
        "emotion_anxiety",
        "emotion_confident",
        "emotion_neutral",
    ]
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(label, callback_data=code)]
        for label, code in zip(buttons, callback_codes)
    ])


def _bet_saved_confirmation_text(lang: str, result: dict, remaining: int, daily_limit: int) -> str:
    if result["bet_result"] == "pending":
        return get_text(lang, "bet_pending_saved").format(
            stake_amount=result["stake_amount"],
            odds=result["odds"],
            bet_type=_bet_type_label(lang, result.get("bet_type"), result.get("bet_market")),
            remaining=remaining,
            limit=daily_limit,
        )

    return get_text(lang, "bet_saved").format(
        bet_result=_result_label(lang, result["bet_result"]),
        stake_amount=result["stake_amount"],
        odds=result["odds"],
        bet_type=_bet_type_label(lang, result.get("bet_type"), result.get("bet_market")),
        remaining=remaining,
        limit=daily_limit,
    )

def _trial_bet_result_text(lang: str, result: dict) -> str:
    if result["bet_result"] == "pending":
        if lang == "ua":
            return (
                f"🕒 Ставку збережено як нерозраховану\n\n"
                f"📌 Тип ставки: {_bet_type_label(lang, result.get('bet_type'), result.get('bet_market'))}\n"
                f"💰 Сума ставки: {result['stake_amount']}\n"
                f"📊 Коефіцієнт: {result['odds']}"
            )
        if lang == "ru":
            return (
                f"🕒 Ставка сохранена как нерассчитанная\n\n"
                f"📌 Тип ставки: {_bet_type_label(lang, result.get('bet_type'), result.get('bet_market'))}\n"
                f"💰 Сумма ставки: {result['stake_amount']}\n"
                f"📊 Коэффициент: {result['odds']}"
            )
        return (
            f"🕒 Bet saved as unsettled\n\n"
            f"📌 Bet type: {_bet_type_label(lang, result.get('bet_type'), result.get('bet_market'))}\n"
            f"💰 Stake amount: {result['stake_amount']}\n"
            f"📊 Odds: {result['odds']}"
        )

    if lang == "ua":
        return (
            f"✅ Ставку розпізнано і збережено\n\n"
            f"🎯 Результат: {_result_label(lang, result['bet_result'])}\n"
            f"📌 Тип ставки: {_bet_type_label(lang, result.get('bet_type'), result.get('bet_market'))}\n"
            f"💰 Сума ставки: {result['stake_amount']}\n"
            f"📊 Коефіцієнт: {result['odds']}"
        )
    if lang == "ru":
        return (
            f"✅ Ставка распознана и сохранена\n\n"
            f"🎯 Результат: {_result_label(lang, result['bet_result'])}\n"
            f"📌 Тип ставки: {_bet_type_label(lang, result.get('bet_type'), result.get('bet_market'))}\n"
            f"💰 Сумма ставки: {result['stake_amount']}\n"
            f"📊 Коэффициент: {result['odds']}"
        )
    return (
        f"✅ Bet recognized and saved\n\n"
        f"🎯 Result: {_result_label(lang, result['bet_result'])}\n"
        f"📌 Bet type: {_bet_type_label(lang, result.get('bet_type'), result.get('bet_market'))}\n"
        f"💰 Stake amount: {result['stake_amount']}\n"
        f"📊 Odds: {result['odds']}"
    )


async def emotion_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    user = get_user(user_id)
    lang = _normalize_lang(user["lang"] if user and user.get("lang") else "en")
    lang = context.user_data.get("bet_lang", lang)
    sub_type = get_subscription_type(user_id)
    has_access = sub_type in ("basic", "vip")
    in_trial = sub_type == "trial"

    bet_id = context.user_data.get("last_bet_id")
    result = context.user_data.get("last_bet_result")
    daily_limit = context.user_data.get("last_bet_daily_limit")
    just_reached_limit = context.user_data.get("last_bet_just_reached_limit", False)

    if not bet_id or not result or daily_limit is None:
        await query.message.reply_text(get_text(lang, "bet_parse_failed"))
        return

    emotion = query.data.removeprefix("emotion_")
    update_bet_emotion(bet_id, emotion)
    add_xp(user_id, XP_TABLE["fill_emotion"])

    context.user_data.pop("last_bet_id", None)
    context.user_data.pop("last_bet_result", None)
    context.user_data.pop("last_bet_daily_limit", None)
    context.user_data.pop("last_bet_just_reached_limit", None)
    context.user_data.pop("bet_lang", None)

    remaining = get_user_remaining_photos_today(user_id)

    await query.message.edit_reply_markup(None)
    if not in_trial:
        await query.message.reply_text(
            _bet_saved_confirmation_text(lang, result, remaining, daily_limit)
        )
        return

    total_used = get_trial_used_count(user_id)
    used_today = count_user_photos_today(user_id)
    daily_limit = get_user_daily_limit(user_id)

    await query.message.reply_text(
        _trial_bet_result_text(lang, result)
    )

    if just_reached_limit or used_today >= daily_limit:
        trial_start = get_trial_start(user_id)
        start_dt = trial_start or datetime.now()
        stats = get_basic_stats_between(
            user_id, start_dt, datetime.now(),
            include_trial=in_trial
        )
        days_left = get_trial_remaining(user_id)
        await query.message.reply_text(
            _trial_pitch_after_5(lang, stats, days_left),
            reply_markup=access_keyboard(lang)
        )
        return

    if total_used >= 2:
        remaining_today = daily_limit - used_today
        days_left = get_trial_remaining(user_id)
        await query.message.reply_text(
            _trial_progress_text(
                lang, used_today,
                remaining_today, days_left
            )
        )

    if total_used == 3:
        trial_start = get_trial_start(user_id)
        start_dt = trial_start or datetime.now()
        stats = get_basic_stats_between(
            user_id, start_dt, datetime.now(),
            include_trial=in_trial
        )
        await query.message.reply_text(
            _trial_pitch_after_3(lang, stats)
        )


def _tilt_warning_keyboard(lang: str) -> InlineKeyboardMarkup:
    labels = {
        "ua": ("✅ Зрозумів, продовжую", "🛑 Зробити паузу"),
        "ru": ("✅ Понял, продолжаю", "🛑 Сделать паузу"),
        "en": ("✅ Got it, continue", "🛑 Take a break"),
    }
    continue_label, pause_label = labels.get(lang, labels["en"])
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(continue_label, callback_data="tilt_warning_ack")],
        [InlineKeyboardButton(pause_label, callback_data="tilt_warning_pause")],
    ])


def _tilt_warning_text(lang: str, signal_code: str, signal_context: dict) -> str:
    count = signal_context.get("count_last_60m", 0)
    hour = signal_context.get("hour", datetime.now().hour)

    if signal_code == "chasing_losses":
        if lang == "ua":
            return (
                "🚨 Стоп-сигнал!\n\n"
                "Останні 3 ставки були мінусовими. Це схоже на спробу відігратися.\n"
                "У таких ситуаціях більшість беттерів втрачають ще більше.\n\n"
                "Рекомендую зробити паузу на 30 хвилин."
            )
        if lang == "ru":
            return (
                "🚨 Стоп-сигнал!\n\n"
                "Последние 3 ставки были минусовыми. Это похоже на попытку отыграться.\n"
                "В таких ситуациях большинство беттеров теряют ещё больше.\n\n"
                "Рекомендую сделать паузу на 30 минут."
            )
        return (
            "🚨 Stop signal!\n\n"
            "Your last 3 bets were losses. This looks like chasing losses.\n"
            "In this situation most bettors lose even more.\n\n"
            "I recommend taking a 30-minute break."
        )

    if signal_code == "rapid_betting":
        if lang == "ua":
            return (
                "⚠️ Увага!\n\n"
                f"Ти зробив {count} ставок за останню годину.\n"
                "Швидкий betting знижує якість рішень.\n\n"
                "Сповільнись."
            )
        if lang == "ru":
            return (
                "⚠️ Внимание!\n\n"
                f"Ты сделал {count} ставок за последний час.\n"
                "Быстрый betting снижает качество решений.\n\n"
                "Притормози."
            )
        return (
            "⚠️ Warning!\n\n"
            f"You placed {count} bets in the last hour.\n"
            "Rapid betting lowers decision quality.\n\n"
            "Slow down."
        )

    if lang == "ua":
        return (
            "🌙 Пізній час.\n\n"
            f"Вже {hour}:00. Твій winrate після 23:00 зазвичай нижчий.\n"
            "Подумай двічі перед наступною ставкою."
        )
    if lang == "ru":
        return (
            "🌙 Позднее время.\n\n"
            f"Уже {hour}:00. Твой winrate после 23:00 обычно ниже.\n"
            "Подумай дважды перед следующей ставкой."
        )
    return (
        "🌙 Late hour.\n\n"
        f"It is already {hour}:00. Your win rate after 23:00 is usually lower.\n"
        "Think twice before the next bet."
    )


def _tilt_break_text(lang: str) -> str:
    if lang == "ua":
        return "Гарне рішення! Побачимось через 30 хвилин 💪"
    if lang == "ru":
        return "Хорошее решение! Увидимся через 30 минут 💪"
    return "Good call! See you in 30 minutes 💪"


async def tilt_warning_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    user = get_user(user_id)
    lang = _normalize_lang(user["lang"] if user and user.get("lang") else "en")

    await query.message.edit_reply_markup(None)

    if query.data == "tilt_warning_pause":
        await query.message.reply_text(_tilt_break_text(lang))


async def process_bet_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("awaiting_ai_match_analysis"):
        await handle_ai_analysis_input(update, context)
        return

    if not update.message or not update.message.photo:
        return

    user_id = update.effective_user.id
    user = get_user(user_id)
    lang = _normalize_lang(user["lang"] if user and user.get("lang") else "en")
    context.user_data["bet_lang"] = lang
    plan = ((user.get("plan") if user else None) or "basic").lower()

    sub_type = get_subscription_type(user_id)
    has_access = sub_type in ("basic", "vip")
    in_trial = sub_type == "trial"
    trial_started = get_trial_start(user_id) is not None
    is_trial_exhausted = (sub_type == "none") and trial_started and not has_access

    if is_trial_exhausted:
        await update.message.reply_text(
            _daily_limit_reached_text(lang, "trial", TRIAL_SCREEN_LIMIT),
            reply_markup=access_keyboard(lang)
        )
        return

    if not has_access and not in_trial:
        no_access_text = (
            "⛔ У тебе немає активного доступу.\n\nСпочатку натисни «Спробувати» або оформи підписку."
            if lang == "ua" else
            "⛔ У тебя нет активного доступа.\n\nСначала нажми «Попробовать» или оформи подписку."
            if lang == "ru" else
            "⛔ You do not have active access.\n\nPress \"Try\" first or buy a subscription."
        )
        await update.message.reply_text(no_access_text, reply_markup=welcome_offer_keyboard(lang))
        return

    if has_access or in_trial:
        daily_limit = get_user_daily_limit(user_id)
        used_today = count_user_photos_today(user_id)

        if used_today >= daily_limit:
            if in_trial:
                await update.message.reply_text(
                    _daily_limit_reached_text(lang, "trial", TRIAL_SCREEN_LIMIT),
                    reply_markup=access_keyboard(lang)
                )
            else:
                await update.message.reply_text(
                    _daily_limit_reached_text(lang, plan, daily_limit),
                    reply_markup=access_keyboard(lang) if plan == "basic" else None
                )
            return

    photo = update.message.photo[-1]
    file_id = photo.file_id

    if has_access:
        log_user_photo(user_id, file_id)
    elif in_trial:
        log_user_photo(user_id, file_id)
        increment_trial_usage(user_id)

    if in_trial:
        used_after = count_user_photos_today(user_id)
        daily_limit_check = get_user_daily_limit(user_id)
        just_reached_limit = (used_after >= daily_limit_check)
    else:
        just_reached_limit = False

    await update.message.reply_text(get_text(lang, "bet_analysis_started"))

    tg_file = await photo.get_file()
    image_bytes = await tg_file.download_as_bytearray()

    result = analyze_basic_bet_screenshot(bytes(image_bytes))

    if result["ok"]:
        bet_id = create_bet(
            user_id=user_id,
            photo_file_id=file_id,
            stake_amount=result["stake_amount"],
            odds=result["odds"],
            bet_result=result["bet_result"],
            currency=result["currency"],
            parse_status="parsed",
            raw_json=result.get("raw_json"),
            bet_type=result.get("bet_type"),
            bet_subtype=result.get("bet_subtype"),
            bet_market=result.get("bet_market"),
            is_trial=not has_access,
        )

        xp_result = add_xp(user_id, XP_TABLE["add_bet"])
        level_up_result = xp_result
        if result["bet_result"] == "win":
            bonus_xp_result = add_xp(user_id, XP_TABLE["win_bet"])
            if bonus_xp_result["leveled_up"]:
                level_up_result = bonus_xp_result

        if level_up_result["leveled_up"]:
            level_name = LEVEL_NAMES.get(lang, LEVEL_NAMES["en"]).get(level_up_result["new_level"], "")
            await update.message.reply_text(
                f"🎉 Новий рівень!\n\n"
                f"Ти досяг рівня {level_up_result['new_level']} - {level_name}\n\n"
                f"Продовжуй - наступний рівень відкриє нові можливості!"
                if lang == "ua" else
                f"🎉 Новый уровень!\n\n"
                f"Ты достиг уровня {level_up_result['new_level']} - {level_name}\n\n"
                f"Продолжай - следующий уровень откроет новые возможности!"
                if lang == "ru" else
                f"🎉 New level!\n\n"
                f"You reached level {level_up_result['new_level']} - {level_name}\n\n"
                f"Keep going - the next level unlocks new possibilities!"
            )

        if has_access or in_trial:
            signal_context = get_tilt_signal_context(user_id)
            signals = signal_context["signals"]

            context.user_data["last_bet_id"] = bet_id
            context.user_data["last_bet_result"] = result
            context.user_data["last_bet_daily_limit"] = daily_limit
            context.user_data["last_bet_just_reached_limit"] = just_reached_limit

            for signal_code in signals:
                await update.message.reply_text(
                    _tilt_warning_text(lang, signal_code, signal_context),
                    reply_markup=_tilt_warning_keyboard(lang),
                )

            await update.message.reply_text(
                _emotion_prompt_text(lang),
                reply_markup=_emotion_keyboard(lang),
            )
            return

        total_used = get_trial_used_count(user_id)
        used_today = count_user_photos_today(user_id)
        daily_limit = get_user_daily_limit(user_id)

        await update.message.reply_text(_trial_bet_result_text(lang, result))

        if total_used >= 2:
            remaining_today = daily_limit - used_today
            days_left = get_trial_remaining(user_id)

            await update.message.reply_text(
                _trial_progress_text(lang, used_today, remaining_today, days_left)
            )

        if total_used == 3:
            trial_start = get_trial_start(user_id)
            start_dt = trial_start or datetime.now()
            stats = get_basic_stats_between(
                user_id, start_dt, datetime.now(), include_trial=in_trial
            )
            await update.message.reply_text(
                _trial_pitch_after_3(lang, stats)
            )
        elif used_today >= daily_limit:
            trial_start = get_trial_start(user_id)
            start_dt = trial_start or datetime.now()
            stats = get_basic_stats_between(
                user_id, start_dt, datetime.now(), include_trial=in_trial
            )
            days_left = get_trial_remaining(user_id)
            await update.message.reply_text(
                _trial_pitch_after_5(lang, stats, days_left),
                reply_markup=access_keyboard(lang)
            )

    else:
        create_bet(
            user_id=user_id,
            photo_file_id=file_id,
            stake_amount=None,
            odds=None,
            bet_result=None,
            currency="UAH",
            parse_status="failed",
            raw_json={"raw_text": result.get("raw_text")} if result.get("raw_text") else None,
            extraction_error=result.get("error"),
            is_trial=not has_access,
        )

        if has_access:
            debug_error = result.get("error", "unknown error")
            await update.message.reply_text(
                f"{get_text(lang, 'bet_parse_failed')}\n\nDEBUG: {debug_error}"
            )
            return

        remaining_trial = get_trial_remaining(user_id)
        total_used = get_trial_used_count(user_id)
        used_today = count_user_photos_today(user_id)
        daily_limit = get_user_daily_limit(user_id)

        await update.message.reply_text(_trial_fail_text(lang, total_used, remaining_trial))

        if total_used >= 2:
            remaining_today = daily_limit - used_today
            days_left = get_trial_remaining(user_id)

            await update.message.reply_text(
                _trial_progress_text(lang, used_today, remaining_today, days_left)
            )

        if total_used == 3:
            trial_start = get_trial_start(user_id)
            start_dt = trial_start or datetime.now()
            stats = get_basic_stats_between(
                user_id, start_dt, datetime.now(), include_trial=in_trial
            )
            await update.message.reply_text(
                _trial_pitch_after_3(lang, stats)
            )
        elif used_today >= daily_limit:
            trial_start = get_trial_start(user_id)
            start_dt = trial_start or datetime.now()
            stats = get_basic_stats_between(
                user_id, start_dt, datetime.now(), include_trial=in_trial
            )
            days_left = get_trial_remaining(user_id)
            await update.message.reply_text(
                _trial_pitch_after_5(lang, stats, days_left),
                reply_markup=access_keyboard(lang)
            )

    if not has_access and get_trial_remaining(user_id) == 0:
        trial_start = get_trial_start(user_id)
        start_dt = trial_start or datetime.now()
        end_dt = datetime.now()

        in_trial = should_include_trial(user_id)
        stats = get_basic_stats_between(
            user_id, start_dt, end_dt,
            include_trial=in_trial
        )

        await update.message.reply_text(
            _build_limit_pitch(lang, stats),
            reply_markup=access_keyboard(lang)
        )



