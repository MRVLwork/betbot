# -*- coding: utf-8 -*-
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, ConversationHandler

from keyboards import (
    course_modules_keyboard,
    course_offer_keyboard,
    course_payment_keyboard,
    main_inline_menu_keyboard,
    tracker_menu_keyboard,
    tracker_offer_keyboard,
    welcome_offer_keyboard,
    access_keyboard,
)
from db import (
    create_user_if_not_exists,
    get_coldmind_remaining,
    get_subscription_type,
    get_user,
    has_course_access,
    is_onboarding_completed,
    user_has_access,
    is_trial_available,
    is_eligible_for_first_payment_promo,
)
from handlers.onboarding import activate_trial_after_onboarding, start_onboarding


def _normalize_lang(lang: str) -> str:
    lang = (lang or "en").lower()
    if lang.startswith("uk") or lang.startswith("ua"):
        return "ua"
    if lang.startswith("ru"):
        return "ru"
    return "en"

def _welcome_text(lang: str, promo_available: bool) -> str:
    lang = _normalize_lang(lang)
    texts = {
        "ua": (
            "🎯 Більшість зливають банк не через погані ставки, а через відсутність системи.\n\n"
            "Bet Tracker  це AI-сигнали + повний облік твоєї гри в одному боті:\n\n"
            "🔥 1 сигнал щодня  відібраний AI, з обґрунтуванням\n"
            "📊 Трекер включено  ROI, Win Rate та історія рахуються автоматично\n"
            "🧊 ColdMind  тренер, який тримає тебе в дисципліні проти тільту\n\n"
            "Перший тиждень  безкоштовно. Без карти, без зобов'язань.\n\n"
            "👇 Обери дію:"
        ),
        "ru": (
            "🎯 Большинство сливают банк не из-за плохих ставок, а из-за отсутствия системы.\n\n"
            "Bet Tracker  это AI-сигналы + полный учёт твоей игры в одном боте:\n\n"
            "🔥 1 сигнал каждый день  отобран AI, с обоснованием\n"
            "📊 Трекер включён  ROI, Win Rate и история считаются автоматически\n"
            "🧊 ColdMind  тренер, который держит тебя в дисциплине против тильта\n\n"
            "Первая неделя  бесплатно. Без карты, без обязательств.\n\n"
            "👇 Выбери действие:"
        ),
        "en": (
            "🎯 Most bettors don't lose because of bad picks  they lose because they have no system.\n\n"
            "Bet Tracker = AI signals + full tracking of your game in one bot:\n\n"
            "🔥 1 signal daily  picked by AI, with reasoning\n"
            "📊 Tracker included  ROI, Win Rate and history counted automatically\n"
            "🧊 ColdMind  a discipline coach that keeps you off tilt\n\n"
            "First week is free. No card, no strings attached.\n\n"
            "👇 Choose an action:"
        ),
    }
    return texts[lang]


def _activate_trial_keyboard(lang: str) -> InlineKeyboardMarkup:
    labels = {
        "ua": "🎁 Активувати Trial",
        "ru": "🎁 Активировать Trial",
        "en": "🎁 Activate Trial",
    }
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(labels.get(_normalize_lang(lang), labels["en"]), callback_data="try_trial")
    ]])


def _bet_tracker_intro_text(lang: str) -> str:
    lang = _normalize_lang(lang)
    texts = {
        "ua": (
            "📊 Bet Tracker  твій журнал ставок на автопілоті\n\n"
            "📸 Надішли скрін купона  бот сам розпізнає і запише ставку\n"
            "📈 ROI, Win Rate, прибуток і серії рахуються автоматично\n"
            "🎯 Бот показує, які типи ставок зливають твій банк\n"
            "🧊 ColdMind  емоційний трекер і тренер дисципліни\n\n"
            "💵 Підписка:\n"
            "🔹 1 місяць  $7 або 500⭐\n"
            "🔥 6 місяців  $30 або 2100⭐ (-30%, економія $12)\n\n"
            "👇 Обери варіант:"
        ),
        "ru": (
            "📊 Bet Tracker  твой журнал ставок на автопилоте\n\n"
            "📸 Пришли скрин купона  бот сам распознает и запишет ставку\n"
            "📈 ROI, Win Rate, прибыль и серии считаются автоматически\n"
            "🎯 Бот показывает, какие типы ставок сливают твой банк\n"
            "🧊 ColdMind  эмоциональный трекер и тренер дисциплины\n\n"
            "💵 Подписка:\n"
            "🔹 1 месяц  $7 или 500⭐\n"
            "🔥 6 месяцев  $30 или 2100⭐ (-30%, экономия $12)\n\n"
            "👇 Выбери вариант:"
        ),
        "en": (
            "📊 Bet Tracker  your bet journal on autopilot\n\n"
            "📸 Send a bet slip screenshot  the bot reads and logs the bet\n"
            "📈 ROI, Win Rate, profit and streaks are counted automatically\n"
            "🎯 The bot shows which bet types drain your bankroll\n"
            "🧊 ColdMind  emotion tracker and discipline coach\n\n"
            "💵 Subscription:\n"
            "🔹 1 month  $7 or 500⭐\n"
            "🔥 6 months  $30 or 2100⭐ (-30%, save $12)\n\n"
            "👇 Choose an option:"
        ),
    }
    return texts[lang]


def _tracker_menu_text(lang: str) -> str:
    lang = _normalize_lang(lang)
    if lang == "ru":
        return "📊 Bet Tracker активен.\n\nВыбери действие:"
    if lang == "en":
        return "📊 Bet Tracker is active.\n\nChoose an action:"
    return "📊 Bet Tracker активний.\n\nОбери дію:"


def _education_intro_text(lang: str) -> str:
    return (
        "􀀀 <b>Курс ColdMind</b>\n"
        "<b>Як перестати зливати і почати заробляти на ставках.</b>\n"
        "Основні поняття беттингу, база знань, психологія, патерни і найпопулярніші стратегії, інструменти та\n"
        "багато іншого, що дозволить створити власну систему і перетворити беттинг із хобі в прибуткову\n"
        "справу.\n"
        "􀀀 <b>Більше 7 модулів + бонус для всіх учасників.</b>\n\n"
        "􀀀 <b>Частинка одного з модулів:</b>\n"
        " <b>Хочеш результат швидко? Ось найшвидше, що існує в беттингу.</b>\n"
        "Найшвидший спосіб змінити свій баланс  не знайти виграшну ставку. А <b>перестати робити одну\n"
        "програшну.</b>\n"
        "У твоїй історії ставок прямо зараз є категорія, яка стабільно з'їдає гроші: певний тип ставок, діапазон\n"
        "кефів або улюблена ліга. Ти її не бачиш, бо дивишся на окремі матчі, а не на цифри.\n"
        "Модуль 4 знаходить її за один вечір. Відрізав  і з наступного тижня ці гроші залишаються в банку.\n"
        "Це не плюс колись на дистанції. Це <b>мінус, який зупиняється одразу.</b>\n"
        "Далі  протокол проти догону (одна зупинена сесія = <code>$50500</code> збережених) і\n"
        "<b>CLV</b>: метрика, яка показує, чи є в тебе перевага, не чекаючи місяців результатів.\n\n"
        "􀀀 <b>$20  назавжди.</b> Швидше за це в беттингу не працює нічого, а хто каже інакше  продає\n"
        "тобі догон у красивій обгортці.\n"
        "􀀀 <b>Акція на старті:</b>\n"
        "􀀀 Курс + Трекер (30 днів): <s>$25</s>  <b>$21</b> (16%)\n"
        "􀀀 Курс + VIP Сигнали (30 днів): <s>$40</s>  <b>$25</b> (37%)"
    )


def _clear_awaiting_states(context: ContextTypes.DEFAULT_TYPE):
    for key in list(context.user_data.keys()):
        if key.startswith("awaiting_"):
            context.user_data.pop(key, None)


def _course_active_text() -> str:
    return "􀀀 Курс ColdMind  доступ активний. Обери модуль:"


def _course_module_placeholder_text() -> str:
    return "􀀀 Модуль 1 скоро буде доступний."


def _course_plan_text(plan: str) -> str:
    texts = {
        "solo": (
            "􀀀 <b>Курс ColdMind  $20</b>\n"
            "Доступ до всіх модулів курсу назавжди (7+ модулів + бонус)."
        ),
        "tracker": (
            "􀀀 <b>Курс + Трекер  $21</b>\n"
            "􀀀 Акційна ціна: <s>$25</s>  <b>$21</b>\n"
            "Курс назавжди + 30 днів підписки Basic (повний трекер: ROI, Win Rate, історія, Підсумки тижня)."
        ),
        "vip": (
            "􀀀 <b>Курс + VIP Сигнали  $25</b>\n"
            "􀀀 Акційна ціна: <s>$40</s>  <b>$25</b>\n"
            "Курс назавжди + 30 днів VIP (AI-сигнали + всі функції трекера)."
        ),
    }
    return texts[plan]


async def send_course_entry(message, context: ContextTypes.DEFAULT_TYPE, user_id: int, lang: str = "ua", force_offer: bool = False):
    _clear_awaiting_states(context)
    if not force_offer and has_course_access(user_id):
        await message.reply_text(
            _course_active_text(),
            reply_markup=course_modules_keyboard(),
        )
        return

    await message.reply_text(
        _education_intro_text(lang),
        parse_mode="HTML",
        reply_markup=course_offer_keyboard(),
    )

def _access_status_banner(lang: str, user_id: int) -> str:
    sub_type = get_subscription_type(user_id)
    if sub_type == "trial":
        remaining, limit, _ = get_coldmind_remaining(user_id, "trial")
        used = max(0, limit - remaining)
        if lang == "ru":
            return f"🎁 Пробный доступ: {used}/{limit} запрос сегодня\nПолный доступ в Basic и VIP"
        if lang == "en":
            return f"🎁 Trial access: {used}/{limit} request today\nFull access in Basic and VIP"
        return f"🎁 Пробний доступ: {used}/{limit} запит сьогодні\nПовний доступ у Basic та VIP"

    if sub_type == "vip":
        return {"ua": "💎 VIP активний", "ru": "💎 VIP активен", "en": "💎 VIP active"}.get(lang, "💎 VIP active")
    if sub_type == "tracker":
        return {"ua": "📊 Bet Tracker активний", "ru": "📊 Bet Tracker активен", "en": "📊 Bet Tracker active"}.get(lang, "📊 Bet Tracker active")
    if sub_type == "basic":
        return {"ua": "🔹 Basic активний", "ru": "🔹 Basic активен", "en": "🔹 Basic active"}.get(lang, "🔹 Basic active")
    return {"ua": "⛔ Доступ не активний", "ru": "⛔ Доступ не активен", "en": "⛔ Access is not active"}.get(lang, "⛔ Access is not active")


def _main_menu_text(lang: str, user_id: int) -> str:
    status = _access_status_banner(lang, user_id)
    if lang == "ru":
        return (
            f"{status}\n\n"
            "Главное меню\n\n"
            "🔥 AI-сигналы дня - готовые ставки и история\n"
            "📊 Моя статистика - ROI, прибыль, серии\n"
            "🤖 AI-анализ PRO - разбор матча по фото или тексту\n"
            "📸 Добавить ставку - пришли скрин купона\n"
            "💎 VIP - полный доступ и ColdMind"
        )
    if lang == "en":
        return (
            f"{status}\n\n"
            "Main menu\n\n"
            "🔥 AI signals today - ready picks and history\n"
            "📊 My stats - ROI, profit, streaks\n"
            "🤖 AI analysis PRO - match analysis from photo or text\n"
            "📸 Add bet - send a bet slip screenshot\n"
            "💎 VIP - full access and ColdMind"
        )
    return (
        f"{status}\n\n"
        "Головне меню\n\n"
        "🔥 AI-сигнали дня - готові ставки та історія\n"
        "📊 Моя статистика - ROI, прибуток, серії\n"
        "🤖 AI-аналіз PRO - розбір матчу з фото або тексту\n"
        "📸 Додати ставку - надішли скрін купона\n"
        "💎 VIP - повний доступ і ColdMind"
    )


async def send_main_menu(message, user_id: int, lang: str | None = None):
    user = get_user(user_id) or {}
    normalized_lang = _normalize_lang(lang or user.get("lang", "en"))
    if get_subscription_type(user_id) == "tracker":
        await message.reply_text(
            _tracker_menu_text(normalized_lang),
            reply_markup=tracker_menu_keyboard(normalized_lang),
        )
        return
    await message.reply_text(
        _main_menu_text(normalized_lang, user_id),
        reply_markup=main_inline_menu_keyboard(normalized_lang),
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    existing_user = get_user(user.id)
    create_user_if_not_exists(user)

    if context.args:
        payload = context.args[0]
        if payload.startswith("ref_") and len(payload) > 4:
            source_key = payload[4:].lower()
            if source_key.isdigit():
                referrer_id = int(source_key)
                if not existing_user and referrer_id != user.id:
                    from db import register_user_referral

                    register_user_referral(referrer_id, user.id)
            else:
                clean_key = source_key.replace("_", "").replace("-", "")
                if clean_key.isascii() and clean_key.isalnum():
                    from db import increment_referral_clicks, set_user_ref_source

                    increment_referral_clicks(source_key)
                    set_user_ref_source(user.id, source_key)

    db_user = get_user(user.id)
    lang = _normalize_lang((db_user or {}).get("lang", "en"))

    await send_standard_start(update, lang)
    return ConversationHandler.END


async def send_standard_start(update: Update, lang: str):
    user = update.effective_user
    if user_has_access(user.id):
        await send_main_menu(update.message, user.id, lang)
        return

    if user_has_access(user.id):
        db_user = get_user(user.id) or {}
        active_text = {
            "ua": "✔ Доступ активний.",
            "ru": "✔ Доступ активен.",
            "en": "✔ Access is active.",
        }[lang]

        await update.message.reply_text(
            active_text,
            reply_markup=main_menu_keyboard(lang, (db_user or {}).get("plan", "basic"))
        )
        return

    promo_available = is_eligible_for_first_payment_promo(user.id)

    await update.message.reply_text(
        _welcome_text(lang, promo_available),
        reply_markup=welcome_offer_keyboard(lang),
    )


async def start_offer_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    tg_user = update.effective_user
    create_user_if_not_exists(tg_user)

    user = get_user(tg_user.id)
    lang = _normalize_lang((user or {}).get("lang", "en"))

    if query.data == "ai_signals_intro":
        from keyboards import ai_signals_plans_keyboard

        if lang == "ru":
            ai_signals_text = (
                "􀀀 *AI Сигналы*\n\n"
                "Готовые ставки от AI-агента в закрытом канале.\n\n"
                "􀀀 *VIP*  ежедневные сигналы с обоснованием\n"
                "􀀀 *ELITE*  премиум-сигналы + приоритетный разбор\n\n"
                "После оплаты ты получишь доступ в закрытый канал.\n\n"
                "􀀀 Выбери план:"
            )
        elif lang == "en":
            ai_signals_text = (
                "􀀀 *AI Signals*\n\n"
                "Ready-to-bet picks from AI agent in a private channel.\n\n"
                "􀀀 *VIP*  daily signals with reasoning\n"
                "􀀀 *ELITE*  premium signals + priority analysis\n\n"
                "After payment you'll get access to the private channel.\n\n"
                "􀀀 Choose your plan:"
            )
        else:
            ai_signals_text = (
                "􀀀 *AI Сигнали*\n\n"
                "Готові ставки від AI-агента у закритому каналі.\n\n"
                "􀀀 *VIP*  щоденні сигнали з обґрунтуванням\n"
                "􀀀 *ELITE*  преміум-сигнали + пріоритетний розбір\n\n"
                "Після оплати ти отримаєш доступ у закритий канал.\n\n"
                "􀀀 Обери план:"
            )
        await query.message.reply_text(
            ai_signals_text,
            parse_mode="Markdown",
            reply_markup=ai_signals_plans_keyboard(lang),
        )
        return ConversationHandler.END

    if query.data == "bet_tracker_intro":
        if get_subscription_type(tg_user.id) in {"tracker", "basic", "vip"}:
            await query.message.reply_text(
                _tracker_menu_text(lang),
                reply_markup=tracker_menu_keyboard(lang),
            )
            return ConversationHandler.END

        await query.message.reply_text(
            _bet_tracker_intro_text(lang),
            reply_markup=tracker_offer_keyboard(lang),
        )
        return ConversationHandler.END

    if query.data in {"education_intro", "course_offer_back"}:
        await send_course_entry(
            query.message,
            context,
            tg_user.id,
            lang,
            force_offer=query.data == "course_offer_back",
        )
        return ConversationHandler.END

    if query.data in {"course_buy_solo", "course_buy_tracker", "course_buy_vip"}:
        plan = query.data.replace("course_buy_", "")
        await query.message.reply_text(
            _course_plan_text(plan),
            parse_mode="HTML",
            reply_markup=course_payment_keyboard(plan),
        )
        return ConversationHandler.END

    if query.data == "course_module_1":
        if not has_course_access(tg_user.id):
            await send_course_entry(query.message, context, tg_user.id, lang, force_offer=True)
            return ConversationHandler.END
        await query.message.reply_text(_course_module_placeholder_text())
        return ConversationHandler.END

    if user_has_access(tg_user.id):
        await send_main_menu(query.message, tg_user.id, lang)
        return ConversationHandler.END

    if user_has_access(tg_user.id):
        active_text = {
            "ua": "✔ Доступ активний.",
            "ru": "✔ Доступ активен.",
            "en": "✔ Access is active.",
        }[lang]

        await query.message.reply_text(
            active_text,
            reply_markup=main_menu_keyboard(lang, (user or {}).get("plan", "basic"))
        )
        return ConversationHandler.END

    if query.data == "try_trial":
        if is_trial_available(tg_user.id):
            if is_onboarding_completed(tg_user.id):
                return await activate_trial_after_onboarding(update, context, lang)
            return await start_onboarding(update, context)
        else:
            limit_text = {
                "ua": "❌ Пробний доступ вже використано.",
                "ru": "❌ Пробный доступ уже использован.",
                "en": "❌ Trial access has already been used.",
            }[lang]

            await query.message.reply_text(limit_text)
            return ConversationHandler.END

    elif query.data == "pay_now":
        buy_text = {
            "ua": (
                "💰 Заробляй на ставках розумніше\n\n"
                "Обери тариф:\n\n"
                "🔹 Basic 1 місяць  $7\n"
                "🔥 AI Прогнози дня\n"
                "Аналіз 15 ставок на день\n"
                " Повна статистика і аналітика\n\n"
                " VIP 1 місяць  $19.99\n"
                "🔥 AI Прогнози Basic + VIP\n"
                " 30 скрінів на день\n"
                " 🧊 ColdMind AI Agent\n"
                " Всі функції без обмежень"
            ),
            "ru": (
                "💰 Зарабатывай на ставках умнее\n\n"
                "Выбери тариф:\n\n"
                "🔹 Basic 1 месяц  $7\n"
                "🔥 AI Прогнозы дня\n"
                "Анализ 15 ставок в день\n"
                " Полная статистика и аналитика\n\n"
                " VIP 1 месяц  $19.99\n"
                "🔥 AI Прогнозы Basic + VIP\n"
                " 30 скринов в день\n"
                " 🧊 ColdMind AI Agent\n"
                " Все функции без ограничений"
            ),
            "en": (
                "💰 Bet smarter, earn more\n\n"
                "Choose your plan:\n\n"
                "🔹 Basic 1 month  $7\n"
                "🔥 AI Predictions of the day\n"
                " 15 screenshots per day\n"
                " Full statistics and analytics\n\n"
                " VIP 1 month  $19.99\n"
                "🔥 Basic + VIP AI Predictions\n"
                " 30 screenshots per day\n"
                " 🧊 ColdMind AI Agent\n"
                " All features unlimited"
            ),
        }[lang]

        await query.message.reply_text(
            buy_text,
            reply_markup=access_keyboard(lang)
        )
        return ConversationHandler.END
