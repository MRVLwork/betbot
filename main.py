# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
import asyncio
import sys
import io
import threading
from zoneinfo import ZoneInfo

# Примусове UTF-8 для stdout
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiohttp import web
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    PreCheckoutQueryHandler,
    ContextTypes,
    filters,
)

from config import BOT_TOKEN, ADMIN_ID
from db import (
    init_db,
    user_has_access,
    get_user_daily_limit,
    count_user_photos_today,
    get_user_remaining_photos_today,
    get_user,
    set_user_language,
    is_trial_available,
)
from bets_db import (
    init_bets_table,
    get_basic_stats_between,
    get_full_stats_between,
    get_analytics_between,
)
from keyboards import (
    stats_periods_keyboard,
    stats_submenu_keyboard,
    language_keyboard,
    main_menu_keyboard,
    access_keyboard,
)
from languages import get_text
from handlers.start import start, start_offer_buttons
from handlers.onboarding import (
    onboarding_deposit,
    onboarding_experience,
    onboarding_goal,
    onboarding_sport,
)
from handlers.promo import access_buttons, promo_input, cancel_promo
from handlers.payment import (
    admin_payment_reply_handler,
    check_payment_status_handler,
    cryptobot_payment_handler,
    handle_payment_screenshot,
    payment_buttons,
    payment_sent,
)
from handlers.stars_payment import (
    open_stars_menu,
    precheckout_handler,
    successful_payment_handler,
)
from handlers.admin import (
    addpromo,
    genbasicweek,
    genbasicmonth,
    genvipweek,
    genvipmonth,
    promos,
    users_list,
    promo_stats,
    delete_user,
    stars_revenue,
    send_basic_bet_day,
    send_vip_bet_day,
    senddaybet,
    sendposthelp,
    sendpost,
    update_menu_all,
    admin_broadcast_photo_handler,
    admin_basic_bet_day_photo_handler,
    admin_vip_bet_day_photo_handler,
)
from handlers.bets import process_bet_photo, emotion_callback_handler, tilt_warning_callback_handler
from handlers.coach import coach_end_callback, handle_coach_message, open_coach
from handlers.discipline import show_streak
from handlers.profile import profile_callback_handler, show_profile
from handlers.tools import open_tools_menu, tools_callback_handler, handle_ai_analysis_input
from handlers.weekly_wrap import send_weekly_wrap, send_weekly_wrap_broadcast
from webhook_server import create_webhook_app, set_bot
from states import (
    ONBOARDING_DEPOSIT,
    ONBOARDING_EXPERIENCE,
    ONBOARDING_GOAL,
    ONBOARDING_SPORT,
    WAITING_PAYMENT_SCREEN,
    WAITING_PROMO,
)

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')


def get_user_lang(user_id: int) -> str:
    user = get_user(user_id)
    if not user:
        return "en"
    return (user.get("lang") or "en").lower()


def get_user_plan(user_id: int) -> str:
    user = get_user(user_id)
    if not user:
        return "basic"
    return (user.get("plan") or "basic").strip().lower()


def _is_trial_user(user_id: int) -> bool:
    user = get_user(user_id)
    if not user:
        return False

    return (
        user.get("trial_started_at") is not None
        and is_trial_available(user_id)
        and not user_has_access(user_id)
    )


def _trial_stats_upsell_text(lang: str) -> str:
    lang = (lang or "en").lower()
    if lang.startswith("uk"):
        lang = "ua"

    texts = {
        "ua": (
            "\U0001F512 \u041f\u043e\u0432\u043d\u0430 \u0441\u0442\u0430\u0442\u0438\u0441\u0442\u0438\u043a\u0430 \u0434\u043e\u0441\u0442\u0443\u043f\u043d\u0430 \u0432 \u043f\u043b\u0430\u0442\u043d\u0438\u0445 \u043f\u043b\u0430\u043d\u0430\u0445\n\n"
            "\u0429\u043e \u0442\u0438 \u0431\u0430\u0447\u0438\u0448 \u0417\u0410\u0420\u0410\u0417 (Trial):\n"
            "\u2022 \u0411\u0430\u0437\u043e\u0432\u0430 \u0441\u0442\u0430\u0442\u0438\u0441\u0442\u0438\u043a\u0430 (ROI, winrate)\n"
            "\u2022 5 \u0441\u043a\u0440\u0456\u043d\u0456\u0432 \u043d\u0430 \u0434\u0435\u043d\u044c  7 \u0434\u043d\u0456\u0432\n"
            "\u2022 \u0415\u043c\u043e\u0446\u0456\u0439\u043d\u0438\u0439 \u0442\u0440\u0435\u043a\u0435\u0440\n\n"
            "\u0429\u043e \u043e\u0442\u0440\u0438\u043c\u0430\u0454\u0448 \u0432 Basic - $5/\u043c\u0456\u0441:\n"
            "\U0001F4CA \u041f\u043e\u0432\u043d\u0430 \u0441\u0442\u0430\u0442\u0438\u0441\u0442\u0438\u043a\u0430 \u043f\u043e \u0442\u0438\u043f\u0430\u0445 \u0441\u0442\u0430\u0432\u043e\u043a\n"
            "\U0001F4CA \u0421\u0442\u0430\u0442\u0438\u0441\u0442\u0438\u043a\u0430 \u043f\u043e \u043a\u043e\u0435\u0444\u0456\u0446\u0456\u0454\u043d\u0442\u0430\u0445 (\u0434\u043e 2.0 / 2.0-2.5 / 2.5+)\n"
            "\U0001F4CA \u0410\u043d\u0430\u043b\u0456\u0442\u0438\u043a\u0430 \u0442\u0440\u0435\u043d\u0434\u0456\u0432 \u0456 \u0441\u043b\u0430\u0431\u043a\u0438\u0445 \u043c\u0456\u0441\u0446\u044c\n"
            "\U0001F4CA 15 \u0441\u043a\u0440\u0456\u043d\u0456\u0432 \u043d\u0430 \u0434\u0435\u043d\u044c\n"
            "\U0001F4C8 \u041f\u0440\u043e\u0444\u0456\u043b\u044c \u0431\u0435\u0442\u0442\u0435\u0440\u0430\n\n"
            "\u0429\u043e \u043e\u0442\u0440\u0438\u043c\u0430\u0454\u0448 \u0443 VIP - $20/\u043c\u0456\u0441:\n"
            "\U0001F9E0 AI \u0422\u0440\u0435\u043d\u0435\u0440 (\u043f\u0435\u0440\u0441\u043e\u043d\u0430\u043b\u044c\u043d\u0438\u0439 \u0440\u043e\u0437\u0431\u0456\u0440)\n"
            "\U0001F4CA \u041f\u043e\u0433\u043b\u0438\u0431\u043b\u0435\u043d\u0430 \u0430\u043d\u0430\u043b\u0456\u0442\u0438\u043a\u0430 \u043f\u043e \u0440\u0438\u043d\u043a\u0430\u0445\n"
            "\U0001F4CA 30 \u0441\u043a\u0440\u0456\u043d\u0456\u0432 \u043d\u0430 \u0434\u0435\u043d\u044c\n"
            "\U0001F3C6 \u0412\u0441\u0456 \u0444\u0443\u043d\u043a\u0446\u0456\u0457 \u0431\u0435\u0437 \u043e\u0431\u043c\u0435\u0436\u0435\u043d\u044c\n\n"
            "\U0001F4A1 Basic \u043e\u043a\u0443\u043f\u0430\u0454\u0442\u044c\u0441\u044f \u044f\u043a\u0449\u043e \u0437\u0430\u0432\u0434\u044f\u043a\u0438 \u0441\u0442\u0430\u0442\u0438\u0441\u0442\u0438\u0446\u0456\n"
            "\u0442\u0438 \u0443\u043d\u0438\u043a\u043d\u0435\u0448 \u0445\u043e\u0447\u0430 \u0431 1 \u0437\u0431\u0438\u0442\u043a\u043e\u0432\u043e\u0457 \u0441\u0442\u0430\u0432\u043a\u0438 \u043d\u0430 \u043c\u0456\u0441\u044f\u0446\u044c"
        ),
        "ru": (
            "\U0001F512 \u041f\u043e\u043b\u043d\u0430\u044f \u0441\u0442\u0430\u0442\u0438\u0441\u0442\u0438\u043a\u0430 \u0434\u043e\u0441\u0442\u0443\u043f\u043d\u0430 \u0432 \u043f\u043b\u0430\u0442\u043d\u044b\u0445 \u043f\u043b\u0430\u043d\u0430\u0445\n\n"
            "\u0427\u0442\u043e \u0442\u044b \u0432\u0438\u0434\u0438\u0448\u044c \u0421\u0415\u0419\u0427\u0410\u0421 (Trial):\n"
            "\u2022 \u0411\u0430\u0437\u043e\u0432\u0430\u044f \u0441\u0442\u0430\u0442\u0438\u0441\u0442\u0438\u043a\u0430 (ROI, winrate)\n"
            "\u2022 5 \u0441\u043a\u0440\u0438\u043d\u043e\u0432 \u0432 \u0434\u0435\u043d\u044c  7 \u0434\u043d\u0435\u0439\n"
            "\u2022 \u042d\u043c\u043e\u0446\u0438\u043e\u043d\u0430\u043b\u044c\u043d\u044b\u0439 \u0442\u0440\u0435\u043a\u0435\u0440\n\n"
            "\u0427\u0442\u043e \u043f\u043e\u043b\u0443\u0447\u0438\u0448\u044c \u0432 Basic - $5/\u043c\u0435\u0441:\n"
            "\U0001F4CA \u041f\u043e\u043b\u043d\u0430\u044f \u0441\u0442\u0430\u0442\u0438\u0441\u0442\u0438\u043a\u0430 \u043f\u043e \u0442\u0438\u043f\u0430\u043c \u0441\u0442\u0430\u0432\u043e\u043a\n"
            "\U0001F4CA \u0421\u0442\u0430\u0442\u0438\u0441\u0442\u0438\u043a\u0430 \u043f\u043e \u043a\u043e\u044d\u0444\u0444\u0438\u0446\u0438\u0435\u043d\u0442\u0430\u043c\n"
            "\U0001F4CA \u0410\u043d\u0430\u043b\u0438\u0442\u0438\u043a\u0430 \u0442\u0440\u0435\u043d\u0434\u043e\u0432 \u0438 \u0441\u043b\u0430\u0431\u044b\u0445 \u043c\u0435\u0441\u0442\n"
            "\U0001F4CA 15 \u0441\u043a\u0440\u0438\u043d\u043e\u0432 \u0432 \u0434\u0435\u043d\u044c\n"
            "\U0001F4C8 \u041f\u0440\u043e\u0444\u0438\u043b\u044c \u0431\u0435\u0442\u0442\u0435\u0440\u0430\n\n"
            "\u0427\u0442\u043e \u043f\u043e\u043b\u0443\u0447\u0438\u0448\u044c \u0432 VIP - $20/\u043c\u0435\u0441:\n"
            "\U0001F9E0 AI \u0422\u0440\u0435\u043d\u0435\u0440 (\u043f\u0435\u0440\u0441\u043e\u043d\u0430\u043b\u044c\u043d\u044b\u0439 \u0440\u0430\u0437\u0431\u043e\u0440)\n"
            "\U0001F4CA \u0423\u0433\u043b\u0443\u0431\u043b\u0451\u043d\u043d\u0430\u044f \u0430\u043d\u0430\u043b\u0438\u0442\u0438\u043a\u0430 \u043f\u043e \u0440\u044b\u043d\u043a\u0430\u043c\n"
            "\U0001F4CA 30 \u0441\u043a\u0440\u0438\u043d\u043e\u0432 \u0432 \u0434\u0435\u043d\u044c\n"
            "\U0001F3C6 \u0412\u0441\u0435 \u0444\u0443\u043d\u043a\u0446\u0438\u0438 \u0431\u0435\u0437 \u043e\u0433\u0440\u0430\u043d\u0438\u0447\u0435\u043d\u0438\u0439\n\n"
            "\U0001F4A1 Basic \u043e\u043a\u0443\u043f\u0430\u0435\u0442\u0441\u044f \u0435\u0441\u043b\u0438 \u0431\u043b\u0430\u0433\u043e\u0434\u0430\u0440\u044f \u0441\u0442\u0430\u0442\u0438\u0441\u0442\u0438\u043a\u0435\n"
            "\u0442\u044b \u0438\u0437\u0431\u0435\u0436\u0438\u0448\u044c \u0445\u043e\u0442\u044f \u0431\u044b 1 \u0443\u0431\u044b\u0442\u043e\u0447\u043d\u043e\u0439 \u0441\u0442\u0430\u0432\u043a\u0438 \u0432 \u043c\u0435\u0441\u044f\u0446"
        ),
        "en": (
            "\U0001F512 Full stats available in paid plans\n\n"
            "What you see NOW (Trial):\n"
            "\u2022 Basic stats (ROI, winrate)\n"
            "\u2022 5 screenshots per day  7 days\n"
            "\u2022 Emotion tracker\n\n"
            "What you get in Basic - $5/mo:\n"
            "\U0001F4CA Full stats by bet type\n"
            "\U0001F4CA Stats by odds range\n"
            "\U0001F4CA Trend & weak spot analytics\n"
            "\U0001F4CA 15 screenshots per day\n"
            "\U0001F4C8 Bettor profile\n\n"
            "What you get in VIP - $20/mo:\n"
            "\U0001F9E0 AI Coach (personal analysis)\n"
            "\U0001F4CA Deep market analytics\n"
            "\U0001F4CA 30 screenshots per day\n"
            "\U0001F3C6 All features unlimited\n\n"
            "\U0001F4A1 Basic pays off if stats help you avoid\n"
            "even 1 losing bet per month"
        ),
    }
    return texts.get(lang, texts["en"])

def is_user_vip(user_id: int) -> bool:
    return get_user_plan(user_id) == "vip" and user_has_access(user_id)


async def run_weekly_wrap_broadcast(application):
    await send_weekly_wrap_broadcast(application.bot)


async def post_init(application):
    scheduler = AsyncIOScheduler(timezone=ZoneInfo("Europe/Kiev"))
    scheduler.add_job(
        run_weekly_wrap_broadcast,
        "cron",
        day_of_week="mon",
        hour=9,
        minute=0,
        kwargs={"application": application},
        id="weekly_wrap_broadcast",
        replace_existing=True,
    )
    scheduler.start()
    application.bot_data["scheduler"] = scheduler


async def post_shutdown(application):
    scheduler = application.bot_data.get("scheduler")
    if scheduler:
        scheduler.shutdown(wait=False)


async def run_webhook_server(bot):
    """Start aiohttp webhook server for CryptoBot callbacks."""
    set_bot(bot)
    webhook_app = create_webhook_app()
    runner = web.AppRunner(webhook_app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8080)
    await site.start()
    print("Webhook server started on port 8080")
    return runner


def _start_webhook_server_in_background(bot):
    def _worker():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        runner = loop.run_until_complete(run_webhook_server(bot))
        try:
            loop.run_forever()
        finally:
            loop.run_until_complete(runner.cleanup())
            loop.close()

    thread = threading.Thread(target=_worker, daemon=True, name="cryptobot-webhook")
    thread.start()
    return thread


def format_compare_block(current: dict, previous: dict, lang: str, current_label_key: str, previous_label_key: str) -> str:
    return get_text(lang, "analytics_compare_block").format(
        current_label=get_text(lang, current_label_key),
        current_profit=current["profit"],
        current_roi=current["roi"],
        current_wr=current["win_rate"],
        previous_label=get_text(lang, previous_label_key),
        previous_profit=previous["profit"],
        previous_roi=previous["roi"],
        previous_wr=previous["win_rate"],
    )


def format_type_breakdown(lang: str, label_key: str, bucket: dict) -> str:
    return get_text(lang, "analytics_type_breakdown_line").format(
        label=get_text(lang, label_key),
        count=bucket["count"],
        win_rate=bucket["win_rate"],
        roi=bucket["roi"],
        profit=bucket["profit"],
    )


def format_odds_breakdown(lang: str, bucket_label_key: str, bucket: dict) -> str:
    return get_text(lang, "analytics_odds_breakdown_line").format(
        bucket=get_text(lang, bucket_label_key),
        count=bucket["count"],
        win_rate=bucket["win_rate"],
        roi=bucket["roi"],
        profit=bucket["profit"],
    )


def format_market_breakdown(lang: str, market_key: str, bucket: dict) -> str:
    return get_text(lang, "analytics_type_breakdown_line").format(
        label=get_text(lang, f"bet_market_{market_key}"),
        count=bucket["count"],
        win_rate=bucket["win_rate"],
        roi=bucket["roi"],
        profit=bucket["profit"],
    )


def format_risk_block(lang: str, stats: dict) -> str:
    if not stats["risk_codes"]:
        return get_text(lang, "analytics_no_risks")

    risk_lines = []
    for code in stats["risk_codes"]:
        if code == "losing_streak":
            risk_lines.append(get_text(lang, "analytics_risk_losing_streak").format(streak=stats["worst_lose_streak"]))
        else:
            risk_lines.append(get_text(lang, f"analytics_risk_{code}"))
    return "\n".join(risk_lines)


def resolve_stats_period(query_data: str, lang: str):
    now = datetime.now()

    if query_data.endswith("_today"):
        return (
            now.replace(hour=0, minute=0, second=0, microsecond=0),
            now,
            get_text(lang, "period_today"),
        )
    if query_data.endswith("_yesterday"):
        return (
            (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0),
            now.replace(hour=0, minute=0, second=0, microsecond=0),
            get_text(lang, "period_yesterday"),
        )
    if query_data.endswith("_3days"):
        return (now - timedelta(days=3), now, get_text(lang, "period_3days"))
    if query_data.endswith("_7days"):
        return (now - timedelta(days=7), now, get_text(lang, "period_7days"))
    if query_data.endswith("_30days"):
        return (now - timedelta(days=30), now, get_text(lang, "period_30days"))
    if query_data.endswith("_current_week"):
        return (
            (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0),
            now,
            get_text(lang, "period_current_week"),
        )
    if query_data.endswith("_current_month"):
        return (
            now.replace(day=1, hour=0, minute=0, second=0, microsecond=0),
            now,
            get_text(lang, "period_current_month"),
        )

    return None, None, None


async def stats_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    lang = get_user_lang(user_id)

    if not user_has_access(user_id) and not _is_trial_user(user_id):
        await query.message.reply_text(get_text(lang, "no_access"))
        return

    start_dt, end_dt, period_name = resolve_stats_period(query.data, lang)
    if not start_dt:
        return

    stats = get_basic_stats_between(user_id, start_dt, end_dt)

    await query.message.reply_text(
        get_text(lang, "stats_result").format(
            period=period_name,
            net_profit=stats["net_profit"],
            roi=stats["roi"],
            win_rate=stats["win_rate"],
            avg_odds=stats["avg_odds"],
            win_streak=stats["win_streak"],
        )
    )


async def full_stats_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    lang = get_user_lang(user_id)
    plan = (get_user_plan(user_id) or "basic").strip().lower()

    if _is_trial_user(user_id):
        await query.message.reply_text(
            _trial_stats_upsell_text(lang),
            reply_markup=access_keyboard(lang)
        )
        return

    if not user_has_access(user_id):
        await query.message.reply_text(get_text(lang, "no_access"))
        return

    start_dt, end_dt, period_name = resolve_stats_period(query.data, lang)
    if not start_dt:
        return

    stats = get_full_stats_between(user_id, start_dt, end_dt)
    template_key = "full_stats_result_vip" if plan == "vip" else "full_stats_result_basic"

    await query.message.reply_text(
        get_text(lang, template_key).format(
            period=period_name,
            net_profit=stats["net_profit"],
            roi=stats["roi"],
            win_rate=stats["win_rate"],
            avg_odds=stats["avg_odds"],
            total_bets=stats["total_bets"],
            settled_bets=stats["settled_bets"],
            pending_bets=stats["pending_bets"],
            wins=stats["wins"],
            losses=stats["losses"],
            refunds=stats["refunds"],
            total_stake=stats["total_stake"],
            settled_stake=stats["settled_stake"],
            current_win_streak=stats["current_win_streak"],
            best_win_streak=stats["best_win_streak"],
            worst_lose_streak=stats["worst_lose_streak"],
            total_type_count=stats["types"]["total"]["count"],
            total_type_profit=stats["types"]["total"]["profit"],
            total_type_roi=stats["types"]["total"]["roi"],
            result_type_count=stats["types"]["result"]["count"],
            result_type_profit=stats["types"]["result"]["profit"],
            result_type_roi=stats["types"]["result"]["roi"],
            odds_lt2_count=stats["odds_lt2"]["count"],
            odds_lt2_profit=stats["odds_lt2"]["profit"],
            odds_lt2_roi=stats["odds_lt2"]["roi"],
            odds_mid_count=stats["odds_mid"]["count"],
            odds_mid_profit=stats["odds_mid"]["profit"],
            odds_mid_roi=stats["odds_mid"]["roi"],
            odds_high_count=stats["odds_high"]["count"],
            odds_high_profit=stats["odds_high"]["profit"],
            odds_high_roi=stats["odds_high"]["roi"],
            last_results=stats["last_results"],
        )
    )


async def analytics_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    lang = get_user_lang(user_id)
    plan = (get_user_plan(user_id) or "basic").strip().lower()

    if _is_trial_user(user_id):
        await query.message.reply_text(
            _trial_stats_upsell_text(lang),
            reply_markup=access_keyboard(lang)
        )
        return

    if not user_has_access(user_id):
        await query.message.reply_text(get_text(lang, "no_access"))
        return

    start_dt, end_dt, period_name = resolve_stats_period(query.data, lang)
    if not start_dt:
        return

    stats = get_analytics_between(user_id, start_dt, end_dt, plan=plan)

    overall_title = get_text(lang, f"analytics_status_{stats['overall_status_code']}_title")
    overall_desc = get_text(lang, f"analytics_status_{stats['overall_status_code']}_desc")

    best_type_label = get_text(lang, f"bet_type_{stats['best_type']}") if stats["best_type"] in ("total", "result") else get_text(lang, "bet_type_none")
    best_odds_label = get_text(lang, f"analytics_odds_bucket_{stats['best_odds_bucket']}") if stats["best_odds_bucket"] in ("lt2", "mid", "high") else get_text(lang, "analytics_odds_bucket_none")

    weak_parts = []
    if plan == "vip":
        if stats.get("weak_market") in stats.get("markets", {}) and stats["markets"][stats["weak_market"]]["count"] > 0:
            weak_parts.append(
                get_text(lang, "analytics_weak_market_line").format(
                    label=get_text(lang, f"bet_market_{stats['weak_market']}"),
                    roi=stats["markets"][stats["weak_market"]]["roi"],
                    profit=stats["markets"][stats["weak_market"]]["profit"],
                )
            )
    else:
        if stats["weak_type"] in ("total", "result") and stats["types"][stats["weak_type"]]["count"] > 0:
            weak_parts.append(
                get_text(lang, "analytics_weak_type_line").format(
                    label=get_text(lang, f"bet_type_{stats['weak_type']}"),
                    roi=stats["types"][stats["weak_type"]]["roi"],
                    profit=stats["types"][stats["weak_type"]]["profit"],
                )
            )
    if stats["weak_odds_bucket"] in ("lt2", "mid", "high") and stats[f"odds_{stats['weak_odds_bucket']}"]["count"] > 0:
        weak_parts.append(
            get_text(lang, "analytics_weak_odds_line").format(
                label=get_text(lang, f"analytics_odds_bucket_{stats['weak_odds_bucket']}"),
                roi=stats[f"odds_{stats['weak_odds_bucket']}"]["roi"],
                profit=stats[f"odds_{stats['weak_odds_bucket']}"]["profit"],
            )
        )
    weak_spot_text = "\n".join(weak_parts) if weak_parts else get_text(lang, "analytics_no_weak_spot")

    dynamics_text = format_compare_block(stats["recent"], stats["previous"], lang, "period_recent_3days", "period_previous_3days")
    trend_text = get_text(lang, f"analytics_trend_{stats['trend_code']}")
    risk_block = format_risk_block(lang, stats)
    profile_title = get_text(lang, f"profile_{stats['profile_code']}_title")
    profile_desc = get_text(lang, f"profile_{stats['profile_code']}_desc")

    recommendation_code = stats.get("recommendation_code", "keep_discipline")
    recommendation_text = get_text(lang, f"analytics_recommendation_{recommendation_code}")
    if plan == "vip":
        best_market = stats.get("best_market")
        if recommendation_code in {"focus_total", "focus_result"} and best_market in stats.get("markets", {}):
            recommendation_text = get_text(lang, "analytics_recommendation_focus_market").format(
                market=get_text(lang, f"bet_market_{best_market}")
            )

    if plan == "vip":
        strengths_lines = []
        for item in stats["strengths"]:
            kind, value = item.split(":", 1)
            if kind == "type":
                strengths_lines.append(get_text(lang, "analytics_strength_type").format(label=get_text(lang, f"bet_type_{value}")))
            elif kind == "market":
                strengths_lines.append(get_text(lang, "analytics_strength_market").format(label=get_text(lang, f"bet_market_{value}")))
            elif kind == "odds":
                strengths_lines.append(get_text(lang, "analytics_strength_odds").format(label=get_text(lang, f"analytics_odds_bucket_{value}")))
        strengths_block = "\n".join(strengths_lines) if strengths_lines else get_text(lang, "analytics_no_strengths")

        market_lines = []
        for market_key in ("1x2", "total", "btts", "handicap", "double_chance", "corners", "cards", "other"):
            bucket = stats.get("markets", {}).get(market_key)
            if bucket and bucket["count"] > 0:
                market_lines.append(format_market_breakdown(lang, market_key, bucket))
        markets_block = "\n".join(market_lines) if market_lines else get_text(lang, "analytics_no_market_data")

        await query.message.reply_text(
            get_text(lang, "analytics_result_vip").format(
                period=period_name,
                overall_title=overall_title,
                overall_desc=overall_desc,
                net_profit=stats["net_profit"],
                roi=stats["roi"],
                win_rate=stats["win_rate"],
                settled_bets=stats["settled_bets"],
                markets_block=markets_block,
                odds_lt2_breakdown=format_odds_breakdown(lang, "analytics_odds_bucket_lt2", stats["odds_lt2"]),
                odds_mid_breakdown=format_odds_breakdown(lang, "analytics_odds_bucket_mid", stats["odds_mid"]),
                odds_high_breakdown=format_odds_breakdown(lang, "analytics_odds_bucket_high", stats["odds_high"]),
                stability_block=get_text(lang, "analytics_stability_block").format(
                    current_win_streak=stats["current_win_streak"],
                    best_win_streak=stats["best_win_streak"],
                    worst_lose_streak=stats["worst_lose_streak"],
                ),
                dynamics_text=(
                    format_compare_block(stats["recent"], stats["previous"], lang, "period_recent_3days", "period_previous_3days")
                    + "\n\n" +
                    format_compare_block(stats["week_current"], stats["week_previous"], lang, "period_current_week", "period_previous_week")
                    + "\n\n" +
                    format_compare_block(stats["month_current"], stats["month_previous"], lang, "period_current_month", "period_previous_month")
                ),
                profile_title=profile_title,
                profile_desc=profile_desc,
                strengths_block=strengths_block,
                weak_spot_text=weak_spot_text,
                recommendation_text=recommendation_text,
                risk_block=risk_block,
            )
        )
        return

    await query.message.reply_text(
        get_text(lang, "analytics_result_basic").format(
            period=period_name,
            overall_title=overall_title,
            overall_desc=overall_desc,
            net_profit=stats["net_profit"],
            roi=stats["roi"],
            win_rate=stats["win_rate"],
            best_type=best_type_label,
            best_type_roi=stats["types"][stats["best_type"]]["roi"] if stats["best_type"] in ("total", "result") else 0,
            best_odds_bucket=best_odds_label,
            best_odds_win_rate=stats[f"odds_{stats['best_odds_bucket']}"]["win_rate"] if stats["best_odds_bucket"] in ("lt2", "mid", "high") else 0,
            best_odds_roi=stats[f"odds_{stats['best_odds_bucket']}"]["roi"] if stats["best_odds_bucket"] in ("lt2", "mid", "high") else 0,
            weak_spot_text=weak_spot_text,
            dynamics_text=dynamics_text,
            trend_text=trend_text,
            profile_title=profile_title,
            profile_desc=profile_desc,
            risk_block=risk_block,
            vip_teaser=get_text(lang, "analytics_vip_teaser"),
        )
    )


async def language_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id

    if query.data == "lang_ua":
        lang = "ua"
    elif query.data == "lang_ru":
        lang = "ru"
    elif query.data == "lang_en":
        lang = "en"
    else:
        lang = "en"

    set_user_language(user_id, lang)

    await query.message.reply_text(
        get_text(lang, "language_changed"),
        reply_markup=main_menu_keyboard(lang, get_user_plan(user_id))
    )


async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return ConversationHandler.END

    user_id = update.effective_user.id
    lang = get_user_lang(user_id)
    text = update.message.text

    ai_menu_labels = {
        "\U0001F464 \u041f\u0440\u043e\u0444\u0456\u043b\u044c", "\U0001F464 \u041f\u0440\u043e\u0444\u0438\u043b\u044c", "\U0001F464 Profile",
        "\U0001F4CA \u0421\u0442\u0430\u0442\u0438\u0441\u0442\u0438\u043a\u0430", "\U0001F4CA Statistics",
        "\U0001F4CA \u041c\u043e\u044f \u0441\u0442\u0430\u0442\u0438\u0441\u0442\u0438\u043a\u0430", "\U0001F4CA My stats",
        "\U0001F4C8 \u041f\u043e\u0432\u043d\u0430 \u0441\u0442\u0430\u0442\u0438\u0441\u0442\u0438\u043a\u0430", "\U0001F4C8 \u041f\u043e\u043b\u043d\u0430\u044f \u0441\u0442\u0430\u0442\u0438\u0441\u0442\u0438\u043a\u0430", "\U0001F4C8 Full stats",
        "\U0001F512 \u041f\u043e\u0432\u043d\u0430 \u0441\u0442\u0430\u0442\u0438\u0441\u0442\u0438\u043a\u0430  \u0442\u0456\u043b\u044c\u043a\u0438 Basic/VIP",
        "\U0001F512 \u041f\u043e\u043b\u043d\u0430\u044f \u0441\u0442\u0430\u0442\u0438\u0441\u0442\u0438\u043a\u0430  \u0442\u043e\u043b\u044c\u043a\u043e Basic/VIP",
        "\U0001F512 Full stats  Basic/VIP only",
        "\U0001F4CA Wrapped",
        "\U0001F9E0 AI \u0422\u0440\u0435\u043d\u0435\u0440", "\U0001F9E0 AI Coach", "\U0001F512 AI \u0422\u0440\u0435\u043d\u0435\u0440 VIP", "\U0001F512 AI Coach VIP",
        "\U0001F9E0 \u0410\u043d\u0430\u043b\u0456\u0442\u0438\u043a\u0430", "\U0001F9E0 \u0410\u043d\u0430\u043b\u0438\u0442\u0438\u043a\u0430", "\U0001F9E0 Analytics",
        "\U0001F6E0 \u0423\u0441\u0456 \u0456\u043d\u0441\u0442\u0440\u0443\u043c\u0435\u043d\u0442\u0438", "\U0001F6E0 \u0412\u0441\u0435 \u0438\u043d\u0441\u0442\u0440\u0443\u043c\u0435\u043d\u0442\u044b", "\U0001F6E0 All tools",
        "\U0001F4B3 \u041a\u0443\u043f\u0438\u0442\u0438 \u0434\u043e\u0441\u0442\u0443\u043f", "\U0001F4B3 \u041a\u0443\u043f\u0438\u0442\u044c \u0434\u043e\u0441\u0442\u0443\u043f", "\U0001F4B3 Buy access",
        "\U0001F310 \u041c\u043e\u0432\u0430", "\U0001F310 \u042f\u0437\u044b\u043a", "\U0001F310 Language",
        "\U0001F511 \u0412\u0432\u0435\u0441\u0442\u0438 \u043f\u0440\u043e\u043c\u043e\u043a\u043e\u0434", "\U0001F511 Enter promo code",
        "\U0001F525 Streak",
        " \u041d\u0430\u0437\u0430\u0434", " Back",
    }

    if context.user_data.get("awaiting_ai_match_analysis") and text not in ai_menu_labels:
        await handle_ai_analysis_input(update, context)
        return ConversationHandler.END

    if context.user_data.get("awaiting_coach_reply") and text not in ai_menu_labels:
        await handle_coach_message(update, context)
        return ConversationHandler.END

    if text in ("\U0001F464 \u041f\u0440\u043e\u0444\u0456\u043b\u044c", "\U0001F464 \u041f\u0440\u043e\u0444\u0438\u043b\u044c", "\U0001F464 Profile"):
        await show_profile(update, context)
    elif text in ("\U0001F4CA \u0421\u0442\u0430\u0442\u0438\u0441\u0442\u0438\u043a\u0430", "\U0001F4CA Statistics"):
        is_trial_user = _is_trial_user(user_id)
        has_access = user_has_access(user_id)
        show_lock = is_trial_user and not has_access

        await update.message.reply_text(
            get_text(lang, "choose_stats_type")
            if not show_lock
            else (
                "\U0001F4CA \u0421\u0442\u0430\u0442\u0438\u0441\u0442\u0438\u043a\u0430  \u043e\u0431\u0435\u0440\u0456\u0442\u044c \u0440\u043e\u0437\u0434\u0456\u043b:"
                if lang == "ua"
                else "\U0001F4CA \u0421\u0442\u0430\u0442\u0438\u0441\u0442\u0438\u043a\u0430  \u0432\u044b\u0431\u0435\u0440\u0438\u0442\u0435 \u0440\u0430\u0437\u0434\u0435\u043b:"
                if lang == "ru"
                else "\U0001F4CA Statistics  choose section:"
            ),
            reply_markup=stats_submenu_keyboard(lang, is_trial=show_lock)
        )
    elif text in (" \u041d\u0430\u0437\u0430\u0434", " Back"):
        plan = get_user_plan(user_id)
        await update.message.reply_text(
            "\U0001F447",
            reply_markup=main_menu_keyboard(lang, plan)
        )
    elif text in ("\U0001F4CA \u041c\u043e\u044f \u0441\u0442\u0430\u0442\u0438\u0441\u0442\u0438\u043a\u0430", "\U0001F4CA My stats"):
        if not user_has_access(user_id) and not _is_trial_user(user_id):
            await update.message.reply_text(get_text(lang, "no_active_access_start"))
            return ConversationHandler.END

        is_vip = is_user_vip(user_id)
        await update.message.reply_text(
            get_text(lang, "choose_period"),
            reply_markup=stats_periods_keyboard(is_vip, lang, prefix="stats"),
        )
    elif text in (
        "\U0001F4C8 \u041f\u043e\u0432\u043d\u0430 \u0441\u0442\u0430\u0442\u0438\u0441\u0442\u0438\u043a\u0430",
        "\U0001F4C8 Full stats",
        "\U0001F512 \u041f\u043e\u0432\u043d\u0430 \u0441\u0442\u0430\u0442\u0438\u0441\u0442\u0438\u043a\u0430  \u0442\u0456\u043b\u044c\u043a\u0438 Basic/VIP",
        "\U0001F512 \u041f\u043e\u043b\u043d\u0430\u044f \u0441\u0442\u0430\u0442\u0438\u0441\u0442\u0438\u043a\u0430  \u0442\u043e\u043b\u044c\u043a\u043e Basic/VIP",
        "\U0001F512 Full stats  Basic/VIP only",
    ):
        has_access = user_has_access(user_id)
        is_trial = _is_trial_user(user_id)

        if is_trial and not has_access:
            from keyboards import _stats_trial_upsell_text
            await update.message.reply_text(
                _stats_trial_upsell_text(lang),
                reply_markup=access_keyboard(lang)
            )
            return ConversationHandler.END

        if not has_access:
            await update.message.reply_text(get_text(lang, "no_active_access_start"))
            return ConversationHandler.END

        is_vip = is_user_vip(user_id)
        await update.message.reply_text(
            get_text(lang, "choose_full_stats_period"),
            reply_markup=stats_periods_keyboard(is_vip, lang, prefix="fullstats"),
        )
    elif text == "\U0001F4CA Wrapped":
        await send_weekly_wrap(update, context)
    elif text in ("\U0001F9E0 AI \u0422\u0440\u0435\u043d\u0435\u0440", "\U0001F9E0 AI Coach", "\U0001F512 AI \u0422\u0440\u0435\u043d\u0435\u0440 VIP", "\U0001F512 AI Coach VIP"):
        await open_coach(update, context)
    elif text in ("\U0001F9E0 \u0410\u043d\u0430\u043b\u0456\u0442\u0438\u043a\u0430", "\U0001F9E0 \u0410\u043d\u0430\u043b\u0438\u0442\u0438\u043a\u0430", "\U0001F9E0 Analytics"):
        if not user_has_access(user_id) and not _is_trial_user(user_id):
            await update.message.reply_text(get_text(lang, "no_active_access_start"))
            return ConversationHandler.END

        is_vip = is_user_vip(user_id)
        await update.message.reply_text(
            get_text(lang, "choose_analytics_period"),
            reply_markup=stats_periods_keyboard(is_vip, lang, prefix="analytics"),
        )
    elif text in ("\U0001F6E0 \u0423\u0441\u0456 \u0456\u043d\u0441\u0442\u0440\u0443\u043c\u0435\u043d\u0442\u0438", "\U0001F6E0 \u0412\u0441\u0435 \u0438\u043d\u0441\u0442\u0440\u0443\u043c\u0435\u043d\u0442\u044b", "\U0001F6E0 All tools"):
        await open_tools_menu(update, context)
    elif text in ("\U0001F4B3 \u041a\u0443\u043f\u0438\u0442\u0438 \u0434\u043e\u0441\u0442\u0443\u043f", "\U0001F4B3 \u041a\u0443\u043f\u0438\u0442\u044c \u0434\u043e\u0441\u0442\u0443\u043f", "\U0001F4B3 Buy access"):
        await update.message.reply_text(
            get_text(lang, "choose_access_option"),
            reply_markup=access_keyboard(lang),
        )
    elif text in ("\U0001F310 \u041c\u043e\u0432\u0430", "\U0001F310 \u042f\u0437\u044b\u043a", "\U0001F310 Language"):
        await update.message.reply_text(
            get_text(lang, "choose_lang"),
            reply_markup=language_keyboard(),
        )
    elif text in ("\U0001F511 \u0412\u0432\u0435\u0441\u0442\u0438 \u043f\u0440\u043e\u043c\u043e\u043a\u043e\u0434", "\U0001F511 Enter promo code"):
        await update.message.reply_text(get_text(lang, "enter_promo_hint"))
        return WAITING_PROMO

    return ConversationHandler.END

def main():
    if not BOT_TOKEN:        raise RuntimeError("\u041d\u0435 \u0437\u043d\u0430\u0439\u0434\u0435\u043d\u043e TELEGRAM_BOT_TOKEN \u0443 .env")

    init_db()
    init_bets_table()

    app = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .post_init(post_init)
        .post_shutdown(post_shutdown)
        .build()
    )

    onboarding_conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ONBOARDING_SPORT: [MessageHandler(filters.TEXT & ~filters.COMMAND, onboarding_sport)],
            ONBOARDING_EXPERIENCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, onboarding_experience)],
            ONBOARDING_DEPOSIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, onboarding_deposit)],
            ONBOARDING_GOAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, onboarding_goal)],
        },
        fallbacks=[CommandHandler("start", start)],
        per_message=False,
    )
    app.add_handler(onboarding_conv)

    app.add_handler(CommandHandler("addpromo", addpromo))
    app.add_handler(CommandHandler("genbasicweek", genbasicweek))
    app.add_handler(CommandHandler("genbasicmonth", genbasicmonth))
    app.add_handler(CommandHandler("genvipweek", genvipweek))
    app.add_handler(CommandHandler("genvipmonth", genvipmonth))
    app.add_handler(CommandHandler("promos", promos))
    app.add_handler(CommandHandler("users", users_list))
    app.add_handler(CommandHandler("statspromo", promo_stats))
    app.add_handler(CommandHandler("deluser", delete_user))
    app.add_handler(CommandHandler("stars", stars_revenue))
    app.add_handler(CommandHandler("sendbasicday", send_basic_bet_day))
    app.add_handler(CommandHandler("sendvipday", send_vip_bet_day))
    app.add_handler(CommandHandler("senddaybet", senddaybet))
    app.add_handler(CommandHandler("sendposthelp", sendposthelp))
    app.add_handler(CommandHandler("sendpost", sendpost))
    app.add_handler(CommandHandler("updatemenu", update_menu_all))

    promo_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(access_buttons, pattern="^(enter_promo|back_to_access)$")],
        states={WAITING_PROMO: [MessageHandler(filters.TEXT & ~filters.COMMAND, promo_input)]},
        fallbacks=[CommandHandler("cancel", cancel_promo)],
        per_message=False,
    )
    app.add_handler(promo_conv)

    payment_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(payment_buttons, pattern="^(buy_usdt|buy_usdt_manual|usdt_.*|cancel_payment)$")],
        states={WAITING_PAYMENT_SCREEN: [MessageHandler(filters.PHOTO, handle_payment_screenshot)]},
        fallbacks=[CallbackQueryHandler(payment_buttons, pattern="^cancel_payment$")],
        per_message=False,
    )
    app.add_handler(payment_conv)

    app.add_handler(CallbackQueryHandler(start_offer_buttons, pattern="^(try_trial|pay_now)$"))
    app.add_handler(CallbackQueryHandler(open_stars_menu, pattern="^(buy_stars|stars_.*)$"))
    app.add_handler(CallbackQueryHandler(cryptobot_payment_handler, pattern="^cb_pay_"))
    app.add_handler(CallbackQueryHandler(check_payment_status_handler, pattern="^check_payment_"))
    app.add_handler(PreCheckoutQueryHandler(precheckout_handler))
    app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_handler))

    app.add_handler(CallbackQueryHandler(payment_sent, pattern="^payment_sent$"))
    app.add_handler(CallbackQueryHandler(stats_callback_handler, pattern="^stats_"))
    app.add_handler(CallbackQueryHandler(full_stats_callback_handler, pattern="^fullstats_"))
    app.add_handler(CallbackQueryHandler(analytics_callback_handler, pattern="^analytics_"))
    app.add_handler(CallbackQueryHandler(language_handler, pattern="^lang_"))
    app.add_handler(CallbackQueryHandler(profile_callback_handler, pattern="^profile_"))
    app.add_handler(CallbackQueryHandler(coach_end_callback, pattern="^coach_end$"))
    app.add_handler(CallbackQueryHandler(tilt_warning_callback_handler, pattern="^tilt_warning_"))
    app.add_handler(CallbackQueryHandler(emotion_callback_handler, pattern="^emotion_"))
    app.add_handler(CallbackQueryHandler(tools_callback_handler, pattern="^(tool_|betday_|tools_back|usdt_vip_bet_day_month|stars_vip_bet_day_month)"))

    app.add_handler(MessageHandler(filters.REPLY & filters.TEXT & ~filters.COMMAND, admin_payment_reply_handler))
    app.add_handler(
        MessageHandler(filters.PHOTO & filters.CaptionRegex(r"^/sendbasicday(?:@\w+)?(?:\s|$)"), admin_basic_bet_day_photo_handler)
    )
    app.add_handler(
        MessageHandler(filters.PHOTO & filters.CaptionRegex(r"^/sendvipday(?:@\w+)?(?:\s|$)"), admin_vip_bet_day_photo_handler)
    )
    app.add_handler(
        MessageHandler(filters.PHOTO & filters.CaptionRegex(r"^/sendpost(?:@\w+)?(?:\s|$)"), admin_broadcast_photo_handler)
    )
    app.add_handler(MessageHandler(filters.Regex(r"^(\U0001F525 Streak|\U0001F525 \u0421\u0435\u0440\u0456\u044f)$"), show_streak))
    app.add_handler(MessageHandler(filters.PHOTO, process_bet_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, menu_handler))

    _start_webhook_server_in_background(app.bot)
    print("Bot started...")
    app.run_polling()


if __name__ == "__main__":
    main()



