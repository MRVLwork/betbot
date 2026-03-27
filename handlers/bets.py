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
    if lang == "ru":
        if bet_type == "total":
            return "тотал"
        if bet_type == "result":
            return "результат"
        return bet_type

    if bet_type == "total":
        return "тотал"
    if bet_type == "result":
        return "результат"

    return bet_type


def _trial_offer_text(lang: str) -> str:
    if lang == "ru":
        return (
            "🔥 Спецпредложение\n\n"
            "⭐ 99 Stars — Basic 7 дней\n"
            "⭐ 399 Stars — Basic 1 месяц\n"
            "⭐ VIP 1 месяц: 1500 → 999 Stars\n"
            "💸 USDT Basic 1 месяц — 4$\n"
            "💸 USDT VIP 1 месяц: 15$ → 9.99$\n\n"
            "После продления и следующих оплат будут действовать полные тарифы.\n\n"
            "Ниже выбери удобный вариант оплаты:"
        )

    return (
        "🔥 Спецпропозиція\n\n"
        "⭐ 99 Stars — Basic 7 днів\n"
        "⭐ 399 Stars — Basic 1 місяць\n"
        "⭐ VIP 1 місяць: 1500 → 999 Stars\n"
        "💸 USDT Basic 1 місяць — 4$\n"
        "💸 USDT VIP 1 місяць: 15$ → 9.99$\n\n"
        "Після продовження та наступних оплат діятимуть повні тарифи.\n\n"
        "Нижче обери зручний варіант оплати:"
    )


async def process_bet_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.photo:
        return

    user_id = update.effective_user.id
    user = get_user(user_id)
    lang = (user["lang"] if user and user["lang"] else "ua")

    has_access = user_has_access(user_id)
    in_trial = (not has_access) and is_trial_available(user_id) and get_trial_start(user_id) is not None

    if not has_access and not in_trial:
        await update.message.reply_text(
            "⛔ У тебе немає активного доступу.\n\nСпочатку натисни «Спробувати» або оформи підписку."
            if lang == "ua" else
            "⛔ У тебя нет активного доступа.\n\nСначала нажми «Попробовать» или оформи подписку.",
            reply_markup=welcome_offer_keyboard(lang)
        )
        return

    if has_access:
        daily_limit = get_user_daily_limit(user_id)
        used_today = count_user_photos_today(user_id)

        if used_today >= daily_limit:
            await update.message.reply_text(
                get_text(lang, "daily_limit_reached").format(limit=daily_limit)
            )
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

        trial_save_text = (
            f"✅ Скрін зараховано.\nВикористано: {used_trial}/3"
            if lang == "ua" else
            f"✅ Скрин засчитан.\nИспользовано: {used_trial}/3"
        )

        if remaining_trial > 0:
            trial_save_text += (
                f"\nЗалишилось: {remaining_trial}/3"
                if lang == "ua" else
                f"\nОсталось: {remaining_trial}/3"
            )

        await update.message.reply_text(trial_save_text)

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
        used_trial = 3 - remaining_trial
        fail_text = (
            f"⚠️ Цей скрін не вдалося розпізнати, але він зарахований у тест.\nВикористано: {used_trial}/3"
            if lang == "ua" else
            f"⚠️ Этот скрин не удалось распознать, но он засчитан в тест.\nИспользовано: {used_trial}/3"
        )

        if remaining_trial > 0:
            fail_text += (
                f"\nЗалишилось: {remaining_trial}/3"
                if lang == "ua" else
                f"\nОсталось: {remaining_trial}/3"
            )

        await update.message.reply_text(fail_text)

    if not has_access and get_trial_remaining(user_id) == 0:
        trial_start = get_trial_start(user_id)
        start_dt = trial_start or datetime.now()
        end_dt = datetime.now()

        stats = get_basic_stats_between(user_id, start_dt, end_dt, include_trial=True)

        stats_text = (
            "📊 Базова статистика по тесту\n\n"
            f"💰 Прибуток: {stats['net_profit']}\n"
            f"📈 ROI: {stats['roi']}%\n"
            f"🎯 Winrate: {stats['win_rate']}%\n"
            f"📊 Середній коефіцієнт: {stats['avg_odds']}\n"
            if lang == "ua" else
            "📊 Базовая статистика по тесту\n\n"
            f"💰 Прибыль: {stats['net_profit']}\n"
            f"📈 ROI: {stats['roi']}%\n"
            f"🎯 Winrate: {stats['win_rate']}%\n"
            f"📊 Средний коэффициент: {stats['avg_odds']}\n"
        )

        await update.message.reply_text(stats_text)
        await update.message.reply_text(_trial_offer_text(lang), reply_markup=access_keyboard(lang))
