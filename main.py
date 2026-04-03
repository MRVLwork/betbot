from datetime import datetime, timedelta

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

from config import BOT_TOKEN
from db import (
    init_db,
    user_has_access,
    get_user_daily_limit,
    count_user_photos_today,
    get_user_remaining_photos_today,
    get_user,
    set_user_language,
)
from bets_db import (
    init_bets_table,
    get_basic_stats_between,
    get_full_stats_between,
    get_analytics_between,
)
from keyboards import (
    stats_periods_keyboard,
    language_keyboard,
    main_menu_keyboard,
    access_keyboard,
)
from languages import get_text
from handlers.start import start, start_offer_buttons
from handlers.promo import access_buttons, promo_input, cancel_promo
from handlers.payment import payment_buttons, handle_payment_screenshot, payment_sent, admin_payment_reply_handler
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
)
from handlers.bets import process_bet_photo
from states import WAITING_PROMO, WAITING_PAYMENT_SCREEN


def get_user_lang(user_id: int) -> str:
    user = get_user(user_id)
    if not user:
        return "en"
    return (user.get("lang") or "en").lower()


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

    if not user_has_access(user_id):
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

    if not user_has_access(user_id):
        await query.message.reply_text(get_text(lang, "no_access"))
        return

    start_dt, end_dt, period_name = resolve_stats_period(query.data, lang)
    if not start_dt:
        return

    stats = get_full_stats_between(user_id, start_dt, end_dt)

    await query.message.reply_text(
        get_text(lang, "full_stats_result").format(
            period=period_name,
            net_profit=stats["net_profit"],
            roi=stats["roi"],
            win_rate=stats["win_rate"],
            avg_odds=stats["avg_odds"],
            total_bets=stats["total_bets"],
            wins=stats["wins"],
            losses=stats["losses"],
            refunds=stats["refunds"],
            total_stake=stats["total_stake"],
            win_streak=stats["win_streak"],
            best_win_streak=stats["best_win_streak"],
            total_type_count=stats["total_type_count"],
            result_type_count=stats["result_type_count"],
            total_type_profit=stats["total_type_profit"],
            result_type_profit=stats["result_type_profit"],
            under_2_count=stats["under_2_count"],
            over_2_count=stats["over_2_count"],
            under_2_profit=stats["under_2_profit"],
            over_2_profit=stats["over_2_profit"],
            last_results=stats["last_results"],
        )
    )


async def analytics_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    lang = get_user_lang(user_id)

    if not user_has_access(user_id):
        await query.message.reply_text(get_text(lang, "no_access"))
        return

    start_dt, end_dt, period_name = resolve_stats_period(query.data, lang)
    if not start_dt:
        return

    stats = get_analytics_between(user_id, start_dt, end_dt)

    best_type_text = get_text(lang, f"bet_type_{stats['best_type']}")
    worst_type_text = get_text(lang, f"bet_type_{stats['worst_type']}")
    conclusion_text = get_text(lang, f"conclusion_{stats['conclusion_code']}")
    coeff_text = get_text(lang, stats["coeff_code"])
    final_conclusion = f"{conclusion_text}\n{coeff_text}"

    risk_block = ""
    if stats["risk_code"] == "losing_streak":
        risk_block = get_text(lang, "risk_losing_streak").format(streak=stats["losing_streak"])
    elif stats["risk_code"] == "roi_drop":
        risk_block = get_text(lang, "risk_roi_drop")

    dynamics_block = get_text(lang, "analytics_dynamics").format(
        recent_profit=stats["recent_profit"],
        previous_profit=stats["previous_profit"],
    )

    profile_title = get_text(lang, f"profile_{stats['profile_code']}_title")
    profile_desc = get_text(lang, f"profile_{stats['profile_code']}_desc")

    await query.message.reply_text(
        get_text(lang, "analytics_result").format(
            period=period_name,
            total_type_count=stats["total_type_count"],
            result_type_count=stats["result_type_count"],
            total_type_profit=stats["total_type_profit"],
            result_type_profit=stats["result_type_profit"],
            under_2_count=stats["under_2_count"],
            over_2_count=stats["over_2_count"],
            under_2_profit=stats["under_2_profit"],
            over_2_profit=stats["over_2_profit"],
            win_rate=stats["win_rate"],
            best_type=best_type_text,
            worst_type=worst_type_text,
            conclusion=final_conclusion,
            risk_block=risk_block,
            dynamics_block=dynamics_block,
            profile_title=profile_title,
            profile_desc=profile_desc,
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
        reply_markup=main_menu_keyboard(lang)
    )


async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return ConversationHandler.END

    user_id = update.effective_user.id
    lang = get_user_lang(user_id)
    text = update.message.text

    if text in ("📤 Надіслати результат", "📤 Отправить результат", "📤 Send result"):
        if not user_has_access(user_id):
            await update.message.reply_text(get_text(lang, "activate_access_first"))
            return ConversationHandler.END

        daily_limit = get_user_daily_limit(user_id)
        used_today = count_user_photos_today(user_id)
        remaining = get_user_remaining_photos_today(user_id)

        await update.message.reply_text(
            get_text(lang, "send_screen_with_limit").format(
                limit=daily_limit,
                used=used_today,
                remaining=remaining
            )
        )

    elif text in ("📊 Моя статистика", "📊 My stats"):
        if not user_has_access(user_id):
            await update.message.reply_text(get_text(lang, "no_active_access_start"))
            return ConversationHandler.END

        user = get_user(user_id)
        is_vip = (user["plan"] == "vip")

        await update.message.reply_text(
            get_text(lang, "choose_period"),
            reply_markup=stats_periods_keyboard(is_vip, lang, prefix="stats")
        )

    elif text in ("📈 Повна статистика", "📈 Полная статистика", "📈 Full stats"):
        if not user_has_access(user_id):
            await update.message.reply_text(get_text(lang, "no_active_access_start"))
            return ConversationHandler.END

        user = get_user(user_id)
        is_vip = (user["plan"] == "vip")

        await update.message.reply_text(
            get_text(lang, "choose_full_stats_period"),
            reply_markup=stats_periods_keyboard(is_vip, lang, prefix="fullstats")
        )

    elif text in ("🧠 Аналітика", "🧠 Аналитика", "🧠 Analytics"):
        if not user_has_access(user_id):
            await update.message.reply_text(get_text(lang, "no_active_access_start"))
            return ConversationHandler.END

        user = get_user(user_id)
        is_vip = (user["plan"] == "vip")

        await update.message.reply_text(
            get_text(lang, "choose_analytics_period"),
            reply_markup=stats_periods_keyboard(is_vip, lang, prefix="analytics")
        )

    elif text in ("🛠 Усі інструменти", "🛠 Все инструменты", "🛠 All tools"):
        if lang == "ru":
            tools_text = "Инструменты скоро будут доступны."
        elif lang == "en":
            tools_text = "Tools will be available soon."
        else:
            tools_text = "Інструменти скоро будуть доступні."

        await update.message.reply_text(tools_text)

    elif text in ("💳 Купити доступ", "💳 Купить доступ", "💳 Buy access"):
        await update.message.reply_text(
            get_text(lang, "choose_access_option"),
            reply_markup=access_keyboard(lang)
        )

    elif text in ("🌐 Мова", "🌐 Язык", "🌐 Language"):
        await update.message.reply_text(
            get_text(lang, "choose_lang"),
            reply_markup=language_keyboard()
        )

    elif text in ("🔑 Ввести промокод", "🔑 Enter promo code"):
        await update.message.reply_text(get_text(lang, "enter_promo_hint"))
        return WAITING_PROMO

    return ConversationHandler.END


def main():
    if not BOT_TOKEN:
        raise RuntimeError("Не знайдено TELEGRAM_BOT_TOKEN у .env")

    init_db()
    init_bets_table()

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))

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

    promo_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(access_buttons, pattern="^(enter_promo|back_to_access)$")],
        states={WAITING_PROMO: [MessageHandler(filters.TEXT & ~filters.COMMAND, promo_input)]},
        fallbacks=[CommandHandler("cancel", cancel_promo)],
        per_message=False,
    )
    app.add_handler(promo_conv)

    payment_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(payment_buttons, pattern="^(buy_usdt|usdt_.*|cancel_payment)$")],
        states={WAITING_PAYMENT_SCREEN: [MessageHandler(filters.PHOTO, handle_payment_screenshot)]},
        fallbacks=[CallbackQueryHandler(payment_buttons, pattern="^cancel_payment$")],
        per_message=False,
    )
    app.add_handler(payment_conv)

    app.add_handler(CallbackQueryHandler(start_offer_buttons, pattern="^(try_trial|pay_now)$"))
    app.add_handler(CallbackQueryHandler(open_stars_menu, pattern="^(buy_stars|stars_.*)$"))
    app.add_handler(PreCheckoutQueryHandler(precheckout_handler))
    app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_handler))

    app.add_handler(CallbackQueryHandler(payment_sent, pattern="^payment_sent$"))
    app.add_handler(CallbackQueryHandler(stats_callback_handler, pattern="^stats_"))
    app.add_handler(CallbackQueryHandler(full_stats_callback_handler, pattern="^fullstats_"))
    app.add_handler(CallbackQueryHandler(analytics_callback_handler, pattern="^analytics_"))
    app.add_handler(CallbackQueryHandler(language_handler, pattern="^lang_"))

    app.add_handler(MessageHandler(filters.REPLY & filters.TEXT & ~filters.COMMAND, admin_payment_reply_handler))
    app.add_handler(MessageHandler(filters.PHOTO, process_bet_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, menu_handler))

    print("Bot started...")
    app.run_polling()


if __name__ == "__main__":
    main()
