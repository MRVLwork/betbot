# -*- coding: utf-8 -*-


def _format_roi(roi: float) -> str:
    return f"+{round(roi, 1)}%" if roi >= 0 else f"{round(roi, 1)}%"


def _format_profit(profit: float) -> str:
    return f"+{round(profit, 1)}" if profit >= 0 else str(round(profit, 1))


def _get_bucket(week: dict, key: str) -> dict:
    type_bucket = (week.get("types") or {}).get(key)
    if type_bucket:
        return type_bucket
    market_bucket = (week.get("markets") or {}).get(key)
    if market_bucket:
        return market_bucket
    return {}


def insight_yesterday_summary(data: dict, lang: str) -> str | None:
    y = data.get("yesterday", {})
    settled = int(y.get("settled_bets") or 0)
    if settled == 0:
        return None

    profit = float(y.get("net_profit") or 0)
    wins = int(y.get("wins") or 0)
    losses = int(y.get("losses") or 0)
    profit_str = _format_profit(profit)
    emoji = "📈" if profit >= 0 else "📉"

    if lang == "ru":
        return (
            f"Доброе утро!\n"
            f"{emoji} Вчера: {profit_str}\n"
            f"🎯 {wins} побед, {losses} проигрышей\n"
            f"Сегодня ориентир: сохраняй тот же ритм\n"
            f"Загляни в бота и не сбивай темп 🚀"
        )
    if lang == "en":
        return (
            f"Good morning!\n"
            f"{emoji} Yesterday: {profit_str}\n"
            f"🎯 {wins} wins, {losses} losses\n"
            f"Today's cue: keep the same pace\n"
            f"Open the bot and stay consistent 🚀"
        )
    return (
        f"Доброго ранку!\n"
        f"{emoji} Вчора: {profit_str}\n"
        f"🎯 {wins} перемог, {losses} програшів\n"
        f"Орієнтир на сьогодні: тримай той самий ритм\n"
        f"Відкрий бота й не збивай темп 🚀"
    )


def insight_avoid_worst_type(data: dict, lang: str) -> str | None:
    week = data.get("week", {})

    worst_key = None
    worst_roi = 0.0
    for key in ["total", "result", "handicap"]:
        bucket = _get_bucket(week, key)
        if int(bucket.get("count") or 0) >= 3:
            roi = float(bucket.get("roi") or 0)
            if roi < worst_roi:
                worst_roi = roi
                worst_key = key

    if not worst_key or worst_roi >= -5:
        return None

    type_names = {
        "ua": {"total": "тоталів", "result": "результату", "handicap": "фори"},
        "ru": {"total": "тоталов", "result": "результата", "handicap": "форы"},
        "en": {"total": "totals", "result": "result", "handicap": "handicap"},
    }
    tn = type_names.get(lang, type_names["ua"]).get(worst_key, worst_key)
    roi_str = f"{round(worst_roi, 1)}%"

    if lang == "ru":
        return (
            f"💡 Совет на сегодня:\n"
            f"Избегай ставок на {tn}\n"
            f"Твой ROI там: {roi_str}\n"
            f"Это слабое место за последние 7 дней\n"
            f"Открой статистику и проверь детали 📊"
        )
    if lang == "en":
        return (
            f"💡 Tip of the day:\n"
            f"Avoid {tn} bets today\n"
            f"Your ROI there: {roi_str}\n"
            f"That's your weakest spot over 7 days\n"
            f"Open stats and review the pattern 📊"
        )
    return (
        f"💡 Порада на сьогодні:\n"
        f"Уникай ставок на {tn}\n"
        f"Твій ROI там: {roi_str}\n"
        f"Це слабке місце за останні 7 днів\n"
        f"Відкрий статистику й перевір деталі 📊"
    )


def insight_focus_best_type(data: dict, lang: str) -> str | None:
    week = data.get("week", {})

    best_key = None
    best_roi = 0.0
    for key in ["total", "result", "handicap"]:
        bucket = _get_bucket(week, key)
        if int(bucket.get("count") or 0) >= 3:
            roi = float(bucket.get("roi") or 0)
            if roi > best_roi:
                best_roi = roi
                best_key = key

    if not best_key or best_roi < 10:
        return None

    type_names = {
        "ua": {"total": "тоталах", "result": "результаті", "handicap": "форі"},
        "ru": {"total": "тоталах", "result": "результате", "handicap": "форе"},
        "en": {"total": "totals", "result": "result", "handicap": "handicap"},
    }
    tn = type_names.get(lang, type_names["ua"]).get(best_key, best_key)
    roi_str = _format_roi(best_roi)

    if lang == "ru":
        return (
            f"🔥 Твоя сильная сторона:\n"
            f"На {tn} ROI {roi_str}\n"
            f"Это лучший сегмент за неделю\n"
            f"Сегодня делай упор именно сюда\n"
            f"Ставь только там, где есть преимущество 💪"
        )
    if lang == "en":
        return (
            f"🔥 Your strong side:\n"
            f"On {tn} ROI {roi_str}\n"
            f"This is your best segment this week\n"
            f"Lean into it today\n"
            f"Bet only where you have an edge 💪"
        )
    return (
        f"🔥 Твоя сильна сторона:\n"
        f"На {tn} ROI {roi_str}\n"
        f"Це твій найкращий сегмент за тиждень\n"
        f"Сьогодні роби акцент саме тут\n"
        f"Став там, де в тебе є перевага 💪"
    )


def insight_streak(data: dict, lang: str) -> str | None:
    week = data.get("week", {})
    streak = int(week.get("current_win_streak") or 0)
    losing_streak = int(week.get("current_lose_streak") or 0)

    if streak >= 3:
        if lang == "ru":
            return (
                f"🔥 Ты в серии!\n"
                f"Побед подряд: {streak}\n"
                f"Импульс хороший, но не повышай риск\n"
                f"Сегодня держи размер ставок под контролем\n"
                f"Дисциплина важнее эйфории 🎯"
            )
        if lang == "en":
            return (
                f"🔥 You're on a streak!\n"
                f"Wins in a row: {streak}\n"
                f"Momentum is good, but don't increase risk\n"
                f"Keep stake sizing controlled today\n"
                f"Discipline beats hype 🎯"
            )
        return (
            f"🔥 Ти в серії!\n"
            f"Перемог поспіль: {streak}\n"
            f"Імпульс хороший, але не підвищуй ризик\n"
            f"Сьогодні тримай розмір ставок під контролем\n"
            f"Дисципліна важливіша за ейфорію 🎯"
        )

    if losing_streak >= 3:
        if lang == "ru":
            return (
                f"⚠️ Внимание!\n"
                f"Серия проигрышей: {losing_streak}\n"
                f"Это момент для паузы, не для погони\n"
                f"Совет дня: 24 часа без импульсивных ставок\n"
                f"Банк чаще всего сливают именно тут 🚨"
            )
        if lang == "en":
            return (
                f"⚠️ Watch out!\n"
                f"Losing streak: {losing_streak}\n"
                f"This is a pause moment, not a chase moment\n"
                f"Tip of the day: 24h without impulsive bets\n"
                f"Bankrolls are usually lost right here 🚨"
            )
        return (
            f"⚠️ Увага!\n"
            f"Серія програшів: {losing_streak}\n"
            f"Це момент для паузи, а не для догону\n"
            f"Порада дня: 24 години без імпульсивних ставок\n"
            f"Банк найчастіше зливають саме тут 🚨"
        )

    return None


def insight_progress(data: dict, lang: str) -> str | None:
    week = data.get("week", {})
    month = data.get("month", {})

    week_roi = float(week.get("roi") or 0)
    month_roi = float(month.get("roi") or 0)
    diff = round(week_roi - month_roi, 1)

    if abs(diff) < 5:
        return None

    week_str = _format_roi(week_roi)
    month_str = _format_roi(month_roi)

    if diff > 0:
        if lang == "ru":
            return (
                f"📈 Прогресс!\n"
                f"ROI за неделю: {week_str}\n"
                f"ROI за месяц: {month_str}\n"
                f"Рост: +{diff} п.п. относительно месяца\n"
                f"Зафиксируй, что именно стало работать 🚀"
            )
        if lang == "en":
            return (
                f"📈 Progress!\n"
                f"ROI this week: {week_str}\n"
                f"ROI this month: {month_str}\n"
                f"Up by +{diff} p.p. versus the month\n"
                f"Lock in what's working 🚀"
            )
        return (
            f"📈 Прогрес!\n"
            f"ROI за тиждень: {week_str}\n"
            f"ROI за місяць: {month_str}\n"
            f"Зростання: +{diff} п.п. відносно місяця\n"
            f"Зафіксуй, що саме почало працювати 🚀"
        )

    if lang == "ru":
        return (
            f"📉 Внимание:\n"
            f"ROI за неделю: {week_str}\n"
            f"ROI за месяц: {month_str}\n"
            f"Просадка: {abs(diff)} п.п.\n"
            f"Открой аналитику и найди, что изменилось 🔍"
        )
    if lang == "en":
        return (
            f"📉 Heads up:\n"
            f"ROI this week: {week_str}\n"
            f"ROI this month: {month_str}\n"
            f"Drop: {abs(diff)} p.p.\n"
            f"Open analytics and find what changed 🔍"
        )
    return (
        f"📉 Увага:\n"
        f"ROI за тиждень: {week_str}\n"
        f"ROI за місяць: {month_str}\n"
        f"Спад: {abs(diff)} п.п.\n"
        f"Відкрий аналітику й знайди, що змінилось 🔍"
    )


def insight_emotion_warning(data: dict, lang: str) -> str | None:
    week = data.get("week", {})
    emotions = week.get("emotions", {})

    tilt = emotions.get("tilt", {})
    tilt_count = int(tilt.get("count") or 0)
    tilt_profit = float(tilt.get("profit") or 0)

    if tilt_count < 2 or tilt_profit >= 0:
        return None

    loss = abs(round(tilt_profit, 1))

    if lang == "ru":
        return (
            f"😤 Эмоциональное напоминание:\n"
            f"На тилте за неделю: {tilt_count} ставок\n"
            f"💸 Потери: -{loss}\n"
            f"Совет дня: пауза перед каждой ставкой\n"
            f"Спроси себя: я уверен или просто зол? 🧠"
        )
    if lang == "en":
        return (
            f"😤 Emotion reminder:\n"
            f"Tilt bets this week: {tilt_count}\n"
            f"💸 Losses: -{loss}\n"
            f"Tip of the day: pause before each bet\n"
            f"Ask yourself: am I confident or just angry? 🧠"
        )
    return (
        f"😤 Емоційне нагадування:\n"
        f"На тілті за тиждень: {tilt_count} ставок\n"
        f"💸 Втрати: -{loss}\n"
        f"Порада дня: пауза перед кожною ставкою\n"
        f"Спитай себе: я впевнений чи просто злий? 🧠"
    )


def insight_motivation(data: dict, lang: str) -> str | None:
    week = data.get("week", {})
    roi = float(week.get("roi") or 0)
    profit = float(week.get("net_profit") or 0)

    if roi < 5 or profit < 0:
        return None

    profit_str = _format_profit(profit)
    roi_str = _format_roi(roi)

    if lang == "ru":
        return (
            f"💎 Ты делаешь правильно!\n"
            f"За неделю: {profit_str}\n"
            f"ROI: {roi_str}\n"
            f"Это уже рабочая дистанция, не случайность\n"
            f"Сегодня главное не ломать дисциплину 🎯"
        )
    if lang == "en":
        return (
            f"💎 You're doing it right!\n"
            f"This week: {profit_str}\n"
            f"ROI: {roi_str}\n"
            f"This is real sample, not luck alone\n"
            f"Today's job is to protect your discipline 🎯"
        )
    return (
        f"💎 Ти робиш правильно!\n"
        f"За тиждень: {profit_str}\n"
        f"ROI: {roi_str}\n"
        f"Це вже робоча дистанція, а не випадковість\n"
        f"Сьогодні головне не ламати дисципліну 🎯"
    )


def insight_check_stats(data: dict, lang: str) -> str | None:
    week = data.get("week", {})
    settled = int(week.get("settled_bets") or 0)
    profit = float(week.get("net_profit") or 0)
    profit_str = _format_profit(profit)
    emoji = "📊" if profit >= 0 else "📉"

    if lang == "ru":
        return (
            f"Доброе утро!\n"
            f"{emoji} За неделю: {settled} ставок\n"
            f"💰 Результат: {profit_str}\n"
            f"Сегодня полезно быстро сверить статистику\n"
            f"Открой бота и посмотри, что менять 👇"
        )
    if lang == "en":
        return (
            f"Good morning!\n"
            f"{emoji} This week: {settled} bets\n"
            f"💰 Result: {profit_str}\n"
            f"Quick stats review can sharpen today\n"
            f"Open the bot and see what to adjust 👇"
        )
    return (
        f"Доброго ранку!\n"
        f"{emoji} За тиждень: {settled} ставок\n"
        f"💰 Результат: {profit_str}\n"
        f"Сьогодні корисно швидко звірити статистику\n"
        f"Відкрий бота й подивись, що підкрутити 👇"
    )


def generate_daily_insight(data: dict, lang: str) -> str | None:
    if not data:
        return None

    day = int(data.get("day_of_year", 0) or 0)
    insight_funcs = [
        insight_yesterday_summary,
        insight_avoid_worst_type,
        insight_focus_best_type,
        insight_streak,
        insight_progress,
        insight_emotion_warning,
        insight_motivation,
        insight_check_stats,
    ]

    primary_idx = day % len(insight_funcs)
    primary = insight_funcs[primary_idx](data, lang)
    if primary:
        return primary

    for i, func in enumerate(insight_funcs):
        if i == primary_idx:
            continue
        result = func(data, lang)
        if result:
            return result

    return None
