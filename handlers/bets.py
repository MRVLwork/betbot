from datetime import datetime

from telegram import Update
from telegram.ext import ContextTypes

from bets_db import create_bet, get_basic_stats_between
from db import (
    get_user,
    user_has_access,
    get_user_daily_limit,
    count_user_photos_today,
    get_user_remaining_photos_today,
    log_user_photo,
    is_trial_available,
    get_trial_remaining,
    increment_trial_usage,
    get_trial_start,
)
from keyboards import access_keyboard, welcome_offer_keyboard
from languages import get_text
from services.ai_service import analyze_basic_bet_screenshot


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


def _bet_type_label(lang: str, bet_type: str) -> str:
    if bet_type == "total":
        return get_text(lang, "bet_type_total")
    if bet_type == "result":
        return get_text(lang, "bet_type_result")
    return bet_type


def _trial_progress_text(lang: str, used_trial: int, remaining_trial: int) -> str:
    lang = _normalize_lang(lang)
    if lang == "ua":
        text = f"✅ Скрін зараховано.\nВикористано: {used_trial}/3"
        if remaining_trial > 0:
            text += f"\nЗалишилось: {remaining_trial}/3"
        return text
    if lang == "ru":
        text = f"✅ Скрин засчитан.\nИспользовано: {used_trial}/3"
        if remaining_trial > 0:
            text += f"\nОсталось: {remaining_trial}/3"
        return text
    text = f"✅ Screenshot counted.\nUsed: {used_trial}/3"
    if remaining_trial > 0:
        text += f"\nRemaining: {remaining_trial}/3"
    return text


def _trial_fail_text(lang: str, used_trial: int, remaining_trial: int) -> str:
    lang = _normalize_lang(lang)
    if lang == "ua":
        text = f"⚠️ Цей скрін не вдалося розпізнати, але він зарахований у тест.\nВикористано: {used_trial}/3"
        if remaining_trial > 0:
            text += f"\nЗалишилось: {remaining_trial}/3"
        return text
    if lang == "ru":
        text = f"⚠️ Этот скрин не удалось распознать, но он засчитан в тест.\nИспользовано: {used_trial}/3"
        if remaining_trial > 0:
            text += f"\nОсталось: {remaining_trial}/3"
        return text
    text = f"⚠️ This screenshot could not be recognized, but it was counted in the trial.\nUsed: {used_trial}/3"
    if remaining_trial > 0:
        text += f"\nRemaining: {remaining_trial}/3"
    return text


def _build_trial_pitch(lang: str, stats: dict, used_trial: int) -> str | None:
    if used_trial < 2:
        return None

    lang = _normalize_lang(lang)
    profit = float(stats.get("net_profit", 0) or 0)
    roi = float(stats.get("roi", 0) or 0)
    win_rate = float(stats.get("win_rate", 0) or 0)
    avg_odds = float(stats.get("avg_odds", 0) or 0)

    if lang == "en":
        if profit > 0:
            return (
                "📊 Now the picture is clearer\n\n"
                f"💰 Profit: {profit}\n"
                f"📈 ROI: {roi}%\n"
                f"🎯 Winrate: {win_rate}%\n"
                f"📊 Avg odds: {avg_odds}\n\n"
                "🔥 Solid result.\n\n"
                "But here is the catch:\n\n"
                "You are in profit right now —\n"
                "but without a system it is easy to lose it.\n\n"
                "📊 Only distance shows\n"
                "whether it is luck or a stable edge.\n\n"
                "👇 Keep analyzing or lock in the result"
            )
        if profit < 0:
            return (
                "📊 Now the picture is clearer\n\n"
                f"💰 Profit: {profit}\n"
                f"📈 ROI: {roi}%\n"
                f"🎯 Winrate: {win_rate}%\n"
                f"📊 Avg odds: {avg_odds}\n\n"
                "❗ Important point:\n\n"
                "At this stage most people realize\n"
                "they are not earning — they are losing.\n\n"
                "You are at the same stage right now.\n\n"
                "👇 Keep analyzing or unlock full access"
            )
        return (
            "📊 You already have the first picture\n\n"
            f"💰 Profit: {profit}\n"
            f"📈 ROI: {roi}%\n"
            f"🎯 Winrate: {win_rate}%\n"
            f"📊 Avg odds: {avg_odds}\n\n"
            "For now the result is around zero.\n"
            "The next few bets will show\n"
            "whether you really have a system.\n\n"
            "👇 Continue to see the real picture"
        )

    if profit > 0:
        header = "📊 Тепер вже є картина\n\n" if lang == "ua" else "📊 Теперь уже есть картина\n\n"
        body = (
            f"💰 Прибуток: {profit}\n"
            f"📈 ROI: {roi}%\n"
            f"🎯 Winrate: {win_rate}%\n"
            f"📊 Середній коефіцієнт: {avg_odds}\n\n"
            "🔥 Непоганий результат.\n\n"
            "Але є нюанс:\n\n"
            "Ти зараз в плюсі —\n"
            "але без системи це легко втратити.\n\n"
            "📊 Саме на дистанції стає видно,\n"
            "чи це випадковість чи стабільний плюс.\n\n"
            "👇 Продовжуй аналіз або закріпи результат"
            if lang == "ua" else
            f"💰 Прибыль: {profit}\n"
            f"📈 ROI: {roi}%\n"
            f"🎯 Winrate: {win_rate}%\n"
            f"📊 Средний коэффициент: {avg_odds}\n\n"
            "🔥 Неплохой результат.\n\n"
            "Но есть нюанс:\n\n"
            "Ты сейчас в плюсе —\n"
            "но без системы это легко потерять.\n\n"
            "📊 Именно на дистанции становится видно,\n"
            "случайность это или стабильный плюс.\n\n"
            "👇 Продолжай анализ или закрепи результат"
        )
        return header + body

    if profit < 0:
        header = "📊 Тепер вже є картина\n\n" if lang == "ua" else "📊 Теперь уже есть картина\n\n"
        body = (
            f"💰 Прибуток: {profit}\n"
            f"📈 ROI: {roi}%\n"
            f"🎯 Winrate: {win_rate}%\n"
            f"📊 Середній коефіцієнт: {avg_odds}\n\n"
            "❗️ Важливий момент:\n\n"
            "Зазвичай на цьому етапі люди розуміють,\n"
            "що вони не заробляють, а втрачають.\n\n"
            "Ти зараз на цьому ж етапі.\n\n"
            "👇 Продовжуй аналіз або відкрий повний доступ"
            if lang == "ua" else
            f"💰 Прибыль: {profit}\n"
            f"📈 ROI: {roi}%\n"
            f"🎯 Winrate: {win_rate}%\n"
            f"📊 Средний коэффициент: {avg_odds}\n\n"
            "❗️ Важный момент:\n\n"
            "Обычно на этом этапе люди понимают,\n"
            "что они не зарабатывают, а теряют.\n\n"
            "Ты сейчас на этом же этапе.\n\n"
            "👇 Продолжай анализ или открой полный доступ"
        )
        return header + body

    header = "📊 Уже є перша картина\n\n" if lang == "ua" else "📊 Уже есть первая картина\n\n"
    body = (
        f"💰 Прибуток: {profit}\n"
        f"📈 ROI: {roi}%\n"
        f"🎯 Winrate: {win_rate}%\n"
        f"📊 Середній коефіцієнт: {avg_odds}\n\n"
        "Поки результат біля нуля.\n"
        "Саме кілька наступних ставок покажуть,\n"
        "чи є у тебе система.\n\n"
        "👇 Продовжуй, щоб побачити реальну картину"
        if lang == "ua" else
        f"💰 Прибыль: {profit}\n"
        f"📈 ROI: {roi}%\n"
        f"🎯 Winrate: {win_rate}%\n"
        f"📊 Средний коэффициент: {avg_odds}\n\n"
        "Пока результат около нуля.\n"
        "Именно несколько следующих ставок покажут,\n"
        "есть ли у тебя система.\n\n"
        "👇 Продолжай, чтобы увидеть реальную картину"
    )
    return header + body


def _build_limit_pitch(lang: str, stats: dict) -> str:
    lang = _normalize_lang(lang)
    profit = float(stats.get("net_profit", 0) or 0)
    roi = float(stats.get("roi", 0) or 0)
    win_rate = float(stats.get("win_rate", 0) or 0)
    avg_odds = float(stats.get("avg_odds", 0) or 0)

    if lang == "en":
        if profit > 0:
            return (
                "🚫 Limit reached\n\n"
                "📊 During this time:\n"
                f"💰 Profit: {profit}\n"
                f"📈 ROI: {roi}%\n"
                f"🎯 Winrate: {win_rate}%\n"
                f"📊 Avg odds: {avg_odds}\n\n"
                "🔥 You are already showing a profit.\n\n"
                "But the main question is:\n\n"
                "👉 is this a system or just a short streak?\n\n"
                "❗ This is where most players:\n"
                "— lose their profit\n"
                "— start betting more aggressively\n"
                "— lose the bankroll\n\n"
                "⚡ Full access is needed\n"
                "to lock in and scale the result\n\n"
                "👇 Do not stop here"
            )
        if profit < 0:
            return (
                "🚫 Limit reached\n\n"
                "📊 During this time:\n"
                f"💰 Profit: {profit}\n"
                f"📈 ROI: {roi}%\n"
                f"🎯 Winrate: {win_rate}%\n"
                f"📊 Avg odds: {avg_odds}\n\n"
                "❗ And this is only the beginning.\n\n"
                "Without stats you will keep repeating the same mistakes.\n\n"
                "⚡ Full access unlocks:\n"
                "— full statistics\n"
                "— bet analysis\n"
                "— control over results\n\n"
                "👇 Do not leave it like this"
            )
        return (
            "🚫 Limit reached\n\n"
            "📊 During this time:\n"
            f"💰 Profit: {profit}\n"
            f"📈 ROI: {roi}%\n"
            f"🎯 Winrate: {win_rate}%\n"
            f"📊 Avg odds: {avg_odds}\n\n"
            "Right now the result is almost flat.\n"
            "Only distance will show\n"
            "whether your strategy really works.\n\n"
            "👇 Unlock full access and continue the analysis"
        )

    if profit > 0:
        return (
            "🚫 Ліміт досягнуто\n\n"
            "📊 За цей час:\n"
            f"💰 Прибуток: {profit}\n"
            f"📈 ROI: {roi}%\n"
            f"🎯 Winrate: {win_rate}%\n"
            f"📊 Середній коефіцієнт: {avg_odds}\n\n"
            "🔥 Ти вже показуєш плюс.\n\n"
            "Але головне питання:\n\n"
            "👉 це система чи просто коротка серія?\n\n"
            "❗️ Саме тут більшість гравців:\n"
            "— втрачають прибуток\n"
            "— починають грати агресивніше\n"
            "— зливають банк\n\n"
            "⚡️ Повний доступ потрібен,\n"
            "щоб зафіксувати і масштабувати результат\n\n"
            "👇 Не зупиняйся на цьому"
            if lang == "ua" else
            "🚫 Лимит достигнут\n\n"
            "📊 За это время:\n"
            f"💰 Прибыль: {profit}\n"
            f"📈 ROI: {roi}%\n"
            f"🎯 Winrate: {win_rate}%\n"
            f"📊 Средний коэффициент: {avg_odds}\n\n"
            "🔥 Ты уже показываешь плюс.\n\n"
            "Но главный вопрос:\n\n"
            "👉 это система или просто короткая серия?\n\n"
            "❗️ Именно здесь большинство игроков:\n"
            "— теряют прибыль\n"
            "— начинают играть агрессивнее\n"
            "— сливают банк\n\n"
            "⚡️ Полный доступ нужен,\n"
            "чтобы зафиксировать и масштабировать результат\n\n"
            "👇 Не останавливайся на этом"
        )

    if profit < 0:
        return (
            "🚫 Ліміт досягнуто\n\n"
            "📊 За цей час:\n"
            f"💰 Прибуток: {profit}\n"
            f"📈 ROI: {roi}%\n"
            f"🎯 Winrate: {win_rate}%\n"
            f"📊 Середній коефіцієнт: {avg_odds}\n\n"
            "❗️ І це тільки початок.\n\n"
            "Без статистики ти будеш повторювати ті ж помилки.\n\n"
            "⚡️ Повний доступ відкриє:\n"
            "— всю статистику\n"
            "— аналіз ставок\n"
            "— контроль результатів\n\n"
            "👇 Не залишай це просто так"
            if lang == "ua" else
            "🚫 Лимит достигнут\n\n"
            "📊 За это время:\n"
            f"💰 Прибыль: {profit}\n"
            f"📈 ROI: {roi}%\n"
            f"🎯 Winrate: {win_rate}%\n"
            f"📊 Средний коэффициент: {avg_odds}\n\n"
            "❗️ И это только начало.\n\n"
            "Без статистики ты будешь повторять те же ошибки.\n\n"
            "⚡️ Полный доступ откроет:\n"
            "— всю статистику\n"
            "— анализ ставок\n"
            "— контроль результатов\n\n"
            "👇 Не оставляй это просто так"
        )

    return (
        "🚫 Ліміт досягнуто\n\n"
        "📊 За цей час:\n"
        f"💰 Прибуток: {profit}\n"
        f"📈 ROI: {roi}%\n"
        f"🎯 Winrate: {win_rate}%\n"
        f"📊 Середній коефіцієнт: {avg_odds}\n\n"
        "Зараз результат майже рівний.\n"
        "Саме на дистанції стане видно,\n"
        "чи працює твоя стратегія.\n\n"
        "👇 Відкрий повний доступ і продовжуй аналіз"
        if lang == "ua" else
        "🚫 Лимит достигнут\n\n"
        "📊 За это время:\n"
        f"💰 Прибыль: {profit}\n"
        f"📈 ROI: {roi}%\n"
        f"🎯 Winrate: {win_rate}%\n"
        f"📊 Средний коэффициент: {avg_odds}\n\n"
        "Сейчас результат почти равный.\n"
        "Именно на дистанции станет видно,\n"
        "работает ли твоя стратегия.\n\n"
        "👇 Открой полный доступ и продолжай анализ"
    )


async def process_bet_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.photo:
        return

    user_id = update.effective_user.id
    user = get_user(user_id)
    lang = _normalize_lang(user["lang"] if user and user.get("lang") else "en")

    has_access = user_has_access(user_id)
    in_trial = (not has_access) and is_trial_available(user_id) and get_trial_start(user_id) is not None

    if not has_access and not in_trial:
        if lang == "ua":
            no_access_text = "⛔ У тебе немає активного доступу.\n\nСпочатку натисни «Спробувати» або оформи підписку."
        elif lang == "ru":
            no_access_text = "⛔ У тебя нет активного доступа.\n\nСначала нажми «Попробовать» или оформи подписку."
        else:
            no_access_text = "⛔ You do not have active access.\n\nFirst press ‘Try’ or purchase a subscription."

        await update.message.reply_text(no_access_text, reply_markup=welcome_offer_keyboard(lang))
        return

    if has_access:
        daily_limit = get_user_daily_limit(user_id)
        used_today = count_user_photos_today(user_id)

        if used_today >= daily_limit:
            await update.message.reply_text(get_text(lang, "daily_limit_reached").format(limit=daily_limit))
            return

    photo = update.message.photo[-1]
    file_id = photo.file_id

    if has_access:
        log_user_photo(user_id, file_id)
    else:
        increment_trial_usage(user_id)

    await update.message.reply_text(get_text(lang, "bet_analysis_started"))

    tg_file = await photo.get_file()
    image_bytes = await tg_file.download_as_bytearray()

    result = analyze_basic_bet_screenshot(bytes(image_bytes))

    if result["ok"]:
        create_bet(
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
            is_trial=not has_access,
        )

        if has_access:
            remaining = get_user_remaining_photos_today(user_id)

            if result["bet_result"] == "pending":
                await update.message.reply_text(
                    get_text(lang, "bet_pending_saved").format(
                        stake_amount=result["stake_amount"],
                        odds=result["odds"],
                        bet_type=_bet_type_label(lang, result["bet_type"]),
                        remaining=remaining,
                        limit=daily_limit
                    )
                )
                return

            await update.message.reply_text(
                get_text(lang, "bet_saved").format(
                    bet_result=_result_label(lang, result["bet_result"]),
                    stake_amount=result["stake_amount"],
                    odds=result["odds"],
                    bet_type=_bet_type_label(lang, result["bet_type"]),
                    remaining=remaining,
                    limit=daily_limit
                )
            )
            return

        remaining_trial = get_trial_remaining(user_id)
        used_trial = 3 - remaining_trial

        await update.message.reply_text(_trial_progress_text(lang, used_trial, remaining_trial))

        if used_trial >= 2:
            trial_start = get_trial_start(user_id)
            start_dt = trial_start or datetime.now()
            end_dt = datetime.now()

            stats = get_basic_stats_between(user_id, start_dt, end_dt, include_trial=True)
            trial_pitch = _build_trial_pitch(lang, stats, used_trial)
            if trial_pitch:
                await update.message.reply_text(trial_pitch)

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
            await update.message.reply_text(f"{get_text(lang, 'bet_parse_failed')}\n\nDEBUG: {debug_error}")
            return

        remaining_trial = get_trial_remaining(user_id)
        used_trial = 3 - remaining_trial

        await update.message.reply_text(_trial_fail_text(lang, used_trial, remaining_trial))

        if used_trial >= 2:
            trial_start = get_trial_start(user_id)
            start_dt = trial_start or datetime.now()
            end_dt = datetime.now()

            stats = get_basic_stats_between(user_id, start_dt, end_dt, include_trial=True)
            trial_pitch = _build_trial_pitch(lang, stats, used_trial)
            if trial_pitch:
                await update.message.reply_text(trial_pitch)

    if not has_access and get_trial_remaining(user_id) == 0:
        trial_start = get_trial_start(user_id)
        start_dt = trial_start or datetime.now()
        end_dt = datetime.now()

        stats = get_basic_stats_between(user_id, start_dt, end_dt, include_trial=True)

        await update.message.reply_text(_build_limit_pitch(lang, stats), reply_markup=access_keyboard(lang))
