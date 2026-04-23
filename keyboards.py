# -*- coding: utf-8 -*-
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup


def welcome_offer_keyboard(lang: str):
    if lang == "ru":
        keyboard = [[
            InlineKeyboardButton("🎁 Попробовать 7 дней", callback_data="try_trial"),
            InlineKeyboardButton("💳 Купить подписку", callback_data="pay_now"),
        ]]
    elif lang == "en":
        keyboard = [[
            InlineKeyboardButton("🎁 Try 7 days free", callback_data="try_trial"),
            InlineKeyboardButton("💳 Buy subscription", callback_data="pay_now"),
        ]]
    else:
        keyboard = [[
            InlineKeyboardButton("🎁 Спробувати 7 днів", callback_data="try_trial"),
            InlineKeyboardButton("💳 Купити підписку", callback_data="pay_now"),
        ]]
    return InlineKeyboardMarkup(keyboard)


def main_menu_keyboard(lang: str, plan: str = "basic"):
    is_vip = (plan or "basic").lower() == "vip"

    if lang == "ru":
        keyboard = [
            ["👤 Профиль"],
            ["📊 Статистика", "🧠 Аналитика"],
            ["📊 Wrapped", "🔥 Streak"],
            ["💳 Купить доступ"],
            ["🌐 Язык", "🛠 Все инструменты"],
        ]
        if is_vip:
            keyboard.insert(3, ["🧠 AI Тренер"])
        else:
            keyboard.insert(3, ["🔒 AI Тренер VIP"])
    elif lang == "en":
        keyboard = [
            ["👤 Profile"],
            ["📊 Statistics", "🧠 Analytics"],
            ["📊 Wrapped", "🔥 Streak"],
            ["💳 Buy access"],
            ["🌐 Language", "🛠 All tools"],
        ]
        if is_vip:
            keyboard.insert(3, ["🧠 AI Coach"])
        else:
            keyboard.insert(3, ["🔒 AI Coach VIP"])
    else:
        keyboard = [
            ["👤 Профіль"],
            ["📊 Статистика", "🧠 Аналітика"],
            ["📊 Wrapped", "🔥 Streak"],
            ["💳 Купити доступ"],
            ["🌐 Мова", "🛠 Усі інструменти"],
        ]
        if is_vip:
            keyboard.insert(3, ["🧠 AI Тренер"])
        else:
            keyboard.insert(3, ["🔒 AI Тренер VIP"])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def stats_submenu_keyboard(lang: str, is_trial: bool = False):
    """
    Підменю після натискання "Статистика".
    Для trial  повна статистика із замочком.
    """
    if lang == "ru":
        if is_trial:
            keyboard = [
                ["📊 Моя статистика"],
                ["🔒 Полная статистика  только Basic/VIP"],
                [" Назад"],
            ]
        else:
            keyboard = [
                ["📊 Моя статистика"],
                ["📈 Повна статистика"],
                [" Назад"],
            ]
    elif lang == "en":
        if is_trial:
            keyboard = [
                ["📊 My stats"],
                ["🔒 Full stats  Basic/VIP only"],
                [" Back"],
            ]
        else:
            keyboard = [
                ["📊 My stats"],
                ["📈 Full stats"],
                [" Back"],
            ]
    else:
        if is_trial:
            keyboard = [
                ["📊 Моя статистика"],
                ["🔒 Повна статистика  тільки Basic/VIP"],
                [" Назад"],
            ]
        else:
            keyboard = [
                ["📊 Моя статистика"],
                ["📈 Повна статистика"],
                [" Назад"],
            ]

    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def _stats_trial_upsell_text(lang: str) -> str:
    """Текст який спонукає trial юзера купити підписку"""
    if lang == "ru":
        return (
            "🔒 Полная статистика доступна в Basic и VIP\n\n"
            "Что ты увидишь в полной статистике:\n"
            "📊 Разбивка по типам ставок\n"
            "📊 Статистика по коэффициентам\n"
            "📊 Твои слабые места\n"
            "📊 Сравнение периодов\n"
            "📈 Профиль беттера\n\n"
            "💡 Именно здесь большинство беттеров\n"
            "понимают где они теряют деньги.\n\n"
            "🔹 Basic  $5/мес\n"
            " VIP  $19.99/мес\n\n"
            "👇 Открой полную картину"
        )
    elif lang == "en":
        return (
            "🔒 Full stats available in Basic and VIP\n\n"
            "What you'll see in full stats:\n"
            "📊 Breakdown by bet type\n"
            "📊 Stats by odds range\n"
            "📊 Your weak spots\n"
            "📊 Period comparison\n"
            "📈 Bettor profile\n\n"
            "💡 This is where most bettors discover\n"
            "exactly where they're losing money.\n\n"
            "🔹 Basic  $5/mo\n"
            " VIP  $19.99/mo\n\n"
            "👇 See the full picture"
        )
    else:
        return (
            "🔒 Повна статистика доступна в Basic і VIP\n\n"
            "Що ти побачиш у повній статистиці:\n"
            "📊 Розбивка по типах ставок\n"
            "📊 Статистика по коефіцієнтах\n"
            "📊 Твої слабкі місця\n"
            "📊 Порівняння періодів\n"
            "📈 Профіль беттера\n\n"
            "💡 Саме тут більшість беттерів розуміють\n"
            "де вони втрачають гроші.\n\n"
            "🔹 Basic  $5/міс\n"
            " VIP  $19.99/міс\n\n"
            "👇 Відкрий повну картину"
        )


def access_keyboard(lang: str):
    if lang == "ru":
        keyboard = [
            [InlineKeyboardButton("🔑 Ввести промокод", callback_data="enter_promo")],
            [InlineKeyboardButton("⭐ Купить через Stars", callback_data="buy_stars")],
            [InlineKeyboardButton("💸 Оплатить USDT", callback_data="buy_usdt")],
        ]
    elif lang == "en":
        keyboard = [
            [InlineKeyboardButton("🔑 Enter promo code", callback_data="enter_promo")],
            [InlineKeyboardButton("⭐ Buy via Stars", callback_data="buy_stars")],
            [InlineKeyboardButton("💸 Pay via USDT", callback_data="buy_usdt")],
        ]
    else:
        keyboard = [
            [InlineKeyboardButton("🔑 Ввести промокод", callback_data="enter_promo")],
            [InlineKeyboardButton("⭐ Купити через Stars", callback_data="buy_stars")],
            [InlineKeyboardButton("💸 Оплатити USDT", callback_data="buy_usdt")],
        ]
    return InlineKeyboardMarkup(keyboard)


def stars_plans_keyboard(lang: str, promo_available: bool = True):
    if promo_available:
        if lang == "ru":
            keyboard = [
                [InlineKeyboardButton("🧪 Попробовать — 99 ⭐", callback_data="stars_basic_week")],
                [InlineKeyboardButton("🔥 Basic 1 месяц: 499 → 399 ⭐", callback_data="stars_basic_month")],
                [InlineKeyboardButton("🔥 VIP 1 месяц: 1999 → 1499 ⭐", callback_data="stars_vip_month_promo")],
            ]
        elif lang == "en":
            keyboard = [
                [InlineKeyboardButton("🧪 Try — 99 ⭐", callback_data="stars_basic_week")],
                [InlineKeyboardButton("🔥 Basic 1 month: 499 → 399 ⭐", callback_data="stars_basic_month")],
                [InlineKeyboardButton("🔥 VIP 1 month: 1999 → 1499 ⭐", callback_data="stars_vip_month_promo")],
            ]
        else:
            keyboard = [
                [InlineKeyboardButton("🧪 Спробувати — 99 ⭐", callback_data="stars_basic_week")],
                [InlineKeyboardButton("🔥 Basic 1 місяць: 499 → 399 ⭐", callback_data="stars_basic_month")],
                [InlineKeyboardButton("🔥 VIP 1 місяць: 1999 → 1499 ⭐", callback_data="stars_vip_month_promo")],
            ]
    else:
        if lang == "ru":
            keyboard = [
                [InlineKeyboardButton("🧪 Попробовать — 99 ⭐", callback_data="stars_basic_week")],
                [InlineKeyboardButton("Basic 1 месяц — 499 ⭐", callback_data="stars_basic_month_full")],
                [InlineKeyboardButton("VIP 1 месяц — 1999 ⭐", callback_data="stars_vip_month_full")],
            ]
        elif lang == "en":
            keyboard = [
                [InlineKeyboardButton("🧪 Try — 99 ⭐", callback_data="stars_basic_week")],
                [InlineKeyboardButton("Basic 1 month — 499 ⭐", callback_data="stars_basic_month_full")],
                [InlineKeyboardButton("VIP 1 month — 1999 ⭐", callback_data="stars_vip_month_full")],
            ]
        else:
            keyboard = [
                [InlineKeyboardButton("🧪 Спробувати — 99 ⭐", callback_data="stars_basic_week")],
                [InlineKeyboardButton("Basic 1 місяць — 499 ⭐", callback_data="stars_basic_month_full")],
                [InlineKeyboardButton("VIP 1 місяць — 1999 ⭐", callback_data="stars_vip_month_full")],
            ]
    return InlineKeyboardMarkup(keyboard)


def usdt_plans_keyboard(lang: str, promo_available: bool = True):
    if promo_available:
        if lang == "ru":
            keyboard = [
                [InlineKeyboardButton("Basic 1 месяц — 5$", callback_data="usdt_basic_month")],
                [InlineKeyboardButton("🔥 VIP 1 месяц: 19.99$ → 14.99$", callback_data="usdt_vip_month_promo")],
            ]
        elif lang == "en":
            keyboard = [
                [InlineKeyboardButton("Basic 1 month — 5$", callback_data="usdt_basic_month")],
                [InlineKeyboardButton("🔥 VIP 1 month: 19.99$ → 14.99$", callback_data="usdt_vip_month_promo")],
            ]
        else:
            keyboard = [
                [InlineKeyboardButton("Basic 1 місяць — 5$", callback_data="usdt_basic_month")],
                [InlineKeyboardButton("🔥 VIP 1 місяць: 19.99$ → 14.99$", callback_data="usdt_vip_month_promo")],
            ]
    else:
        if lang == "ru":
            keyboard = [
                [InlineKeyboardButton("Basic 1 месяц — 5$", callback_data="usdt_basic_month")],
                [InlineKeyboardButton("VIP 1 месяц — 19.99$", callback_data="usdt_vip_month_full")],
            ]
        elif lang == "en":
            keyboard = [
                [InlineKeyboardButton("Basic 1 month — 5$", callback_data="usdt_basic_month")],
                [InlineKeyboardButton("VIP 1 month — 19.99$", callback_data="usdt_vip_month_full")],
            ]
        else:
            keyboard = [
                [InlineKeyboardButton("Basic 1 місяць — 5$", callback_data="usdt_basic_month")],
                [InlineKeyboardButton("VIP 1 місяць — 19.99$", callback_data="usdt_vip_month_full")],
            ]
    return InlineKeyboardMarkup(keyboard)


def cryptobot_plans_keyboard(lang: str, promo_available: bool = True):
    """Keyboard for CryptoBot auto-payment plans."""
    if promo_available:
        if lang == "ru":
            keyboard = [
                [InlineKeyboardButton("Basic 1 месяц - $5 USDT", callback_data="cb_pay_usdt_basic_month")],
                [InlineKeyboardButton("🔥 VIP 1 месяц: $19.99 -> $14.99 USDT", callback_data="cb_pay_usdt_vip_month_promo")],
                [InlineKeyboardButton("🧾 Ручная оплата", callback_data="buy_usdt_manual")],
            ]
        elif lang == "en":
            keyboard = [
                [InlineKeyboardButton("Basic 1 month - $5 USDT", callback_data="cb_pay_usdt_basic_month")],
                [InlineKeyboardButton("🔥 VIP 1 month: $19.99 -> $14.99 USDT", callback_data="cb_pay_usdt_vip_month_promo")],
                [InlineKeyboardButton("🧾 Manual payment", callback_data="buy_usdt_manual")],
            ]
        else:
            keyboard = [
                [InlineKeyboardButton("Basic 1 місяць - $5 USDT", callback_data="cb_pay_usdt_basic_month")],
                [InlineKeyboardButton("🔥 VIP 1 місяць: $19.99 -> $14.99 USDT", callback_data="cb_pay_usdt_vip_month_promo")],
                [InlineKeyboardButton("🧾 Ручна оплата", callback_data="buy_usdt_manual")],
            ]
    else:
        if lang == "ru":
            keyboard = [
                [InlineKeyboardButton("Basic 1 месяц - $5 USDT", callback_data="cb_pay_usdt_basic_month")],
                [InlineKeyboardButton("VIP 1 месяц - $19.99 USDT", callback_data="cb_pay_usdt_vip_month")],
                [InlineKeyboardButton("🧾 Ручная оплата", callback_data="buy_usdt_manual")],
            ]
        elif lang == "en":
            keyboard = [
                [InlineKeyboardButton("Basic 1 month - $5 USDT", callback_data="cb_pay_usdt_basic_month")],
                [InlineKeyboardButton("VIP 1 month - $19.99 USDT", callback_data="cb_pay_usdt_vip_month")],
                [InlineKeyboardButton("🧾 Manual payment", callback_data="buy_usdt_manual")],
            ]
        else:
            keyboard = [
                [InlineKeyboardButton("Basic 1 місяць - $5 USDT", callback_data="cb_pay_usdt_basic_month")],
                [InlineKeyboardButton("VIP 1 місяць - $19.99 USDT", callback_data="cb_pay_usdt_vip_month")],
                [InlineKeyboardButton("🧾 Ручна оплата", callback_data="buy_usdt_manual")],
            ]
    return InlineKeyboardMarkup(keyboard)


def tools_keyboard(lang: str):
    if lang == "ru":
        keyboard = [
            [InlineKeyboardButton("🎯 Ставка дня", callback_data="tool_bet_day")],
            [InlineKeyboardButton("⚡ Live", callback_data="tool_live")],
            [InlineKeyboardButton("🤖 AI-анализ", callback_data="tool_ai")],
            [InlineKeyboardButton("🚀 Челлендж", callback_data="tool_challenge")],
        ]
    elif lang == "en":
        keyboard = [
            [InlineKeyboardButton("🎯 Bet of the day", callback_data="tool_bet_day")],
            [InlineKeyboardButton("⚡ Live", callback_data="tool_live")],
            [InlineKeyboardButton("🤖 AI analysis", callback_data="tool_ai")],
            [InlineKeyboardButton("🚀 Challenge", callback_data="tool_challenge")],
        ]
    else:
        keyboard = [
            [InlineKeyboardButton("🎯 Ставка дня", callback_data="tool_bet_day")],
            [InlineKeyboardButton("⚡ Live", callback_data="tool_live")],
            [InlineKeyboardButton("🤖 AI-аналіз", callback_data="tool_ai")],
            [InlineKeyboardButton("🚀 Челендж", callback_data="tool_challenge")],
        ]
    return InlineKeyboardMarkup(keyboard)


def bet_day_menu_keyboard(lang: str):
    if lang == "ru":
        keyboard = [
            [InlineKeyboardButton("🎯 Ставка дня (Basic)", callback_data="betday_basic")],
            [InlineKeyboardButton("🔥 Ставка дня (VIP)", callback_data="betday_vip")],
            [InlineKeyboardButton("⬅️ Назад", callback_data="tools_back")],
        ]
    elif lang == "en":
        keyboard = [
            [InlineKeyboardButton("🎯 Bet of the day (Basic)", callback_data="betday_basic")],
            [InlineKeyboardButton("🔥 Bet of the day (VIP)", callback_data="betday_vip")],
            [InlineKeyboardButton("⬅️ Back", callback_data="tools_back")],
        ]
    else:
        keyboard = [
            [InlineKeyboardButton("🎯 Ставка дня (Basic)", callback_data="betday_basic")],
            [InlineKeyboardButton("🔥 Ставка дня (VIP)", callback_data="betday_vip")],
            [InlineKeyboardButton("⬅️ Назад", callback_data="tools_back")],
        ]
    return InlineKeyboardMarkup(keyboard)


def bet_day_basic_keyboard(lang: str, is_subscribed: bool = False):
    if lang == "ru":
        subscribe = "✅ Ты подписан" if is_subscribed else "🔔 Подписаться"
        keyboard = [
            [InlineKeyboardButton(subscribe, callback_data="betday_basic_subscribe")],
            [InlineKeyboardButton("⬅️ Назад", callback_data="tool_bet_day")],
        ]
    elif lang == "en":
        subscribe = "✅ You are subscribed" if is_subscribed else "🔔 Subscribe"
        keyboard = [
            [InlineKeyboardButton(subscribe, callback_data="betday_basic_subscribe")],
            [InlineKeyboardButton("⬅️ Back", callback_data="tool_bet_day")],
        ]
    else:
        subscribe = "✅ Ти підписаний" if is_subscribed else "🔔 Підписатися"
        keyboard = [
            [InlineKeyboardButton(subscribe, callback_data="betday_basic_subscribe")],
            [InlineKeyboardButton("⬅️ Назад", callback_data="tool_bet_day")],
        ]
    return InlineKeyboardMarkup(keyboard)


def bet_day_vip_keyboard(lang: str, has_access: bool = False, is_subscribed: bool = False):
    rows = []
    if has_access:
        if lang == "ru":
            subscribe = "✅ Ты подписан" if is_subscribed else "🔔 Подписаться"
        elif lang == "en":
            subscribe = "✅ You are subscribed" if is_subscribed else "🔔 Subscribe"
        else:
            subscribe = "✅ Ти підписаний" if is_subscribed else "🔔 Підписатися"
        rows.append([InlineKeyboardButton(subscribe, callback_data="betday_vip_subscribe")])
    else:
        if lang == "ru":
            rows.append([InlineKeyboardButton("💸 Купить за 4.99$", callback_data="usdt_vip_bet_day_month")])
            rows.append([InlineKeyboardButton("⭐ Купить за 499 Stars", callback_data="stars_vip_bet_day_month")])
        elif lang == "en":
            rows.append([InlineKeyboardButton("💸 Buy for $4.99", callback_data="usdt_vip_bet_day_month")])
            rows.append([InlineKeyboardButton("⭐ Buy for 499 Stars", callback_data="stars_vip_bet_day_month")])
        else:
            rows.append([InlineKeyboardButton("💸 Купити за 4.99$", callback_data="usdt_vip_bet_day_month")])
            rows.append([InlineKeyboardButton("⭐ Купити за 499 Stars", callback_data="stars_vip_bet_day_month")])

    back_text = "⬅️ Назад" if lang in ("ru", "ua") else "⬅️ Back"
    rows.append([InlineKeyboardButton(back_text, callback_data="tool_bet_day")])
    return InlineKeyboardMarkup(rows)


def payment_check_keyboard(lang: str):
    if lang == "ru":
        confirm_text = "✅ Я оплатил"
        cancel_text = "❌ Отменить"
    elif lang == "en":
        confirm_text = "✅ I paid"
        cancel_text = "❌ Cancel"
    else:
        confirm_text = "✅ Я оплатив"
        cancel_text = "❌ Скасувати"

    return InlineKeyboardMarkup([
        [InlineKeyboardButton(confirm_text, callback_data="payment_sent")],
        [InlineKeyboardButton(cancel_text, callback_data="cancel_payment")],
    ])


def stats_periods_keyboard(is_vip: bool, lang: str, prefix: str = "stats"):
    if lang == "ru":
        keyboard = [
            [InlineKeyboardButton("Сегодня", callback_data=f"{prefix}_today")],
            [InlineKeyboardButton("Вчера", callback_data=f"{prefix}_yesterday")],
            [InlineKeyboardButton("3 дня", callback_data=f"{prefix}_3days")],
            [InlineKeyboardButton("7 дней", callback_data=f"{prefix}_7days")],
            [InlineKeyboardButton("30 дней", callback_data=f"{prefix}_30days")],
        ]
        if is_vip:
            keyboard.append([InlineKeyboardButton("Текущая неделя", callback_data=f"{prefix}_current_week")])
            keyboard.append([InlineKeyboardButton("Текущий месяц", callback_data=f"{prefix}_current_month")])
    elif lang == "en":
        keyboard = [
            [InlineKeyboardButton("Today", callback_data=f"{prefix}_today")],
            [InlineKeyboardButton("Yesterday", callback_data=f"{prefix}_yesterday")],
            [InlineKeyboardButton("3 days", callback_data=f"{prefix}_3days")],
            [InlineKeyboardButton("7 days", callback_data=f"{prefix}_7days")],
            [InlineKeyboardButton("30 days", callback_data=f"{prefix}_30days")],
        ]
        if is_vip:
            keyboard.append([InlineKeyboardButton("Current week", callback_data=f"{prefix}_current_week")])
            keyboard.append([InlineKeyboardButton("Current month", callback_data=f"{prefix}_current_month")])
    else:
        keyboard = [
            [InlineKeyboardButton("Сьогодні", callback_data=f"{prefix}_today")],
            [InlineKeyboardButton("Вчора", callback_data=f"{prefix}_yesterday")],
            [InlineKeyboardButton("3 дні", callback_data=f"{prefix}_3days")],
            [InlineKeyboardButton("7 днів", callback_data=f"{prefix}_7days")],
            [InlineKeyboardButton("30 днів", callback_data=f"{prefix}_30days")],
        ]
        if is_vip:
            keyboard.append([InlineKeyboardButton("Поточний тиждень", callback_data=f"{prefix}_current_week")])
            keyboard.append([InlineKeyboardButton("Поточний місяць", callback_data=f"{prefix}_current_month")])

    return InlineKeyboardMarkup(keyboard)


def language_keyboard():
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("🇺🇦 Українська", callback_data="lang_ua"),
        InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
        InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
    ]])
