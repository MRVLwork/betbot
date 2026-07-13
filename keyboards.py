# -*- coding: utf-8 -*-
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup


def welcome_offer_keyboard(lang: str):
    keyboard = [
        [InlineKeyboardButton("🎁 Почати безкоштовно", callback_data="try_trial")],
        [InlineKeyboardButton("🔥 AI-сигнали", callback_data="ai_signals_intro")],
        [InlineKeyboardButton("💎 Купити підписку", callback_data="pay_now")],
    ]
    return InlineKeyboardMarkup(keyboard)


def main_menu_keyboard(lang: str = "ua", plan: str = "basic"):
    if lang == "ru":
        keyboard = [
            [KeyboardButton("🔥 AI-сигналы")],
            [KeyboardButton("💎 Получить VIP")],
            [KeyboardButton("🧊 ColdMind AI Agent"), KeyboardButton("📸 Добавить ставку")],
            [KeyboardButton("📊 Моя статистика"), KeyboardButton("Ещё")],
        ]
    elif lang == "en":
        keyboard = [
            [KeyboardButton("🔥 AI Signals")],
            [KeyboardButton("💎 Get VIP")],
            [KeyboardButton("🧊 ColdMind AI Agent"), KeyboardButton("📸 Add bet")],
            [KeyboardButton("📊 My stats"), KeyboardButton("More")],
        ]
    else:
        keyboard = [
            [KeyboardButton("🔥 AI-сигнали")],
            [KeyboardButton("💎 Отримати VIP")],
            [KeyboardButton("🧊 ColdMind AI Agent"), KeyboardButton("📸 Додати ставку")],
            [KeyboardButton("📊 Моя статистика"), KeyboardButton("Ще")],
        ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, is_persistent=True)


def extra_menu_keyboard(lang: str = "ua"):
    if lang == "ru":
        keyboard = [
            [KeyboardButton("🧠 AI-разбор")],
            [KeyboardButton("📅 Итоги недели")],
            [KeyboardButton("🎯 Мой профиль")],
            [KeyboardButton("🧊 Мои лимиты")],
            [KeyboardButton("🛠 Инструменты")],
            [KeyboardButton(" Настройки")],
            [KeyboardButton(" Назад")],
        ]
    elif lang == "en":
        keyboard = [
            [KeyboardButton("🧠 AI analysis")],
            [KeyboardButton("📅 Weekly recap")],
            [KeyboardButton("🎯 My profile")],
            [KeyboardButton("🧊 My limits")],
            [KeyboardButton("🛠 Tools")],
            [KeyboardButton(" Settings")],
            [KeyboardButton(" Back")],
        ]
    else:
        keyboard = [
            [KeyboardButton("🧠 AI-розбір")],
            [KeyboardButton("📅 Підсумки тижня")],
            [KeyboardButton("🎯 Мій профіль")],
            [KeyboardButton("🧊 Мої ліміти")],
            [KeyboardButton("🛠 Інструменти")],
            [KeyboardButton(" Налаштування")],
            [KeyboardButton(" Назад")],
        ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, is_persistent=True)


def stats_submenu_keyboard(lang: str, is_trial: bool = False):
    """
    Підменю після натискання "Статистика".
    Для trial  повна статистика із замочком.
    """
    if lang == "ru":
        if is_trial:
            keyboard = [
                ["📊 Краткая статистика"],
                ["🔒 Полная статистика  только Basic/VIP"],
                [" Назад"],
            ]
        else:
            keyboard = [
                ["📊 Краткая статистика"],
                ["📈 Полная статистика"],
                [" Назад"],
            ]
    elif lang == "en":
        if is_trial:
            keyboard = [
                ["📊 Quick stats"],
                ["🔒 Full stats  Basic/VIP only"],
                [" Back"],
            ]
        else:
            keyboard = [
                ["📊 Quick stats"],
                ["📈 Full stats"],
                [" Back"],
            ]
    else:
        if is_trial:
            keyboard = [
                ["📊 Скорочена статистика"],
                ["🔒 Повна статистика  тільки Basic/VIP"],
                [" Назад"],
            ]
        else:
            keyboard = [
                ["📊 Скорочена статистика"],
                ["📈 Повна статистика"],
                [" Назад"],
            ]

    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def _stats_trial_upsell_text(lang: str) -> str:
    """Текст який спонукає trial юзера купити підписку"""
    if lang == "ru":
        return (
            "💰 Зарабатывай на ставках умнее\n\n"
            "В Basic и VIP ты получишь:\n"
            "🔥 AI Прогнозы дня - готовые ставки\n"
            "📊 Разбивка по типам ставок\n"
            "📊 Статистика по коэффициентам\n"
            "📊 Твои слабые места\n"
            "📊 Сравнение периодов\n"
            "📈 Профиль беттера\n\n"
            "💡 AI прогнозы + твоя статистика\n"
            "показывают, где есть шанс на плюс.\n\n"
            "🔹 Basic  $7/мес\n"
            " VIP  $19.99/мес\n\n"
            "👇 Открой доступ"
        )
    elif lang == "en":
        return (
            "💰 Bet smarter, earn more\n\n"
            "With Basic and VIP you get:\n"
            "🔥 AI Predictions - ready picks\n"
            "📊 Breakdown by bet type\n"
            "📊 Stats by odds range\n"
            "📊 Your weak spots\n"
            "📊 Period comparison\n"
            "📈 Bettor profile\n\n"
            "💡 AI predictions + your stats\n"
            "show where you have a better shot at profit.\n\n"
            "🔹 Basic  $7/mo\n"
            " VIP  $19.99/mo\n\n"
            "👇 Unlock access"
        )
    else:
        return (
            "💰 Заробляй на ставках розумніше\n\n"
            "У Basic і VIP ти отримаєш:\n"
            "🔥 AI Прогнози дня - готові ставки\n"
            "📊 Розбивка по типах ставок\n"
            "📊 Статистика по коефіцієнтах\n"
            "📊 Твої слабкі місця\n"
            "📊 Порівняння періодів\n"
            "📈 Профіль беттера\n\n"
            "💡 AI прогнози + твоя статистика\n"
            "показують, де є шанс на плюс.\n\n"
            "🔹 Basic  $7/міс\n"
            " VIP  $19.99/міс\n\n"
            "👇 Відкрий доступ"
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
    if lang == "ru":
        keyboard = [
            [InlineKeyboardButton("Basic 1 месяц  525⭐", callback_data="stars_basic_month")],
            [InlineKeyboardButton("VIP 1 месяц  1500⭐", callback_data="stars_vip_1m")],
            [InlineKeyboardButton("VIP Прогнозы 10 дней  399⭐", callback_data="stars_vip_signals_10d")],
            [InlineKeyboardButton(" Назад", callback_data="back_to_access")],
        ]
        if promo_available:
            keyboard.insert(1, [InlineKeyboardButton("Basic 6 месяцев (-29%)  2250⭐", callback_data="stars_basic_6m_promo")])
            keyboard.insert(3, [InlineKeyboardButton("VIP 3 месяца (-17%)  3750⭐", callback_data="stars_vip_3m_promo")])
            keyboard.insert(4, [InlineKeyboardButton("VIP 6 месяцев (-25%)  6750⭐", callback_data="stars_vip_6m_promo")])
    elif lang == "en":
        keyboard = [
            [InlineKeyboardButton("Basic 1 month  525⭐", callback_data="stars_basic_month")],
            [InlineKeyboardButton("VIP 1 month  1500⭐", callback_data="stars_vip_1m")],
            [InlineKeyboardButton("VIP Predictions 10 days  399⭐", callback_data="stars_vip_signals_10d")],
            [InlineKeyboardButton(" Back", callback_data="back_to_access")],
        ]
        if promo_available:
            keyboard.insert(1, [InlineKeyboardButton("Basic 6 months (-29%)  2250⭐", callback_data="stars_basic_6m_promo")])
            keyboard.insert(3, [InlineKeyboardButton("VIP 3 months (-17%)  3750⭐", callback_data="stars_vip_3m_promo")])
            keyboard.insert(4, [InlineKeyboardButton("VIP 6 months (-25%)  6750⭐", callback_data="stars_vip_6m_promo")])
    else:  # ua
        keyboard = [
            [InlineKeyboardButton("Basic 1 місяць  525⭐", callback_data="stars_basic_month")],
            [InlineKeyboardButton("VIP 1 місяць  1500⭐", callback_data="stars_vip_1m")],
            [InlineKeyboardButton("VIP Прогнози 10 днів  399⭐", callback_data="stars_vip_signals_10d")],
            [InlineKeyboardButton(" Назад", callback_data="back_to_access")],
        ]
        if promo_available:
            keyboard.insert(1, [InlineKeyboardButton("Basic 6 місяців (-29%)  2250⭐", callback_data="stars_basic_6m_promo")])
            keyboard.insert(3, [InlineKeyboardButton("VIP 3 місяці (-17%)  3750⭐", callback_data="stars_vip_3m_promo")])
            keyboard.insert(4, [InlineKeyboardButton("VIP 6 місяців (-25%)  6750⭐", callback_data="stars_vip_6m_promo")])
    return InlineKeyboardMarkup(keyboard)


def ai_signals_keyboard(lang: str, vip_access: bool = False):
    if lang == "ru":
        rows = [
            [InlineKeyboardButton("🔥 Trial прогнозы", callback_data="signal_trial")],
            [InlineKeyboardButton("🔥 Basic прогнозы", callback_data="signal_basic")],
        ]
        if vip_access:
            rows.append([InlineKeyboardButton("💎 VIP прогнозы", callback_data="signal_vip")])
        else:
            rows.append([InlineKeyboardButton("💎 Купить VIP прогнозы 399⭐ / 10 дней", callback_data="stars_vip_signals_10d")])
        return InlineKeyboardMarkup(rows)
    if lang == "en":
        rows = [
            [InlineKeyboardButton("🔥 Trial predictions", callback_data="signal_trial")],
            [InlineKeyboardButton("🔥 Basic predictions", callback_data="signal_basic")],
        ]
        if vip_access:
            rows.append([InlineKeyboardButton("💎 VIP predictions", callback_data="signal_vip")])
        else:
            rows.append([InlineKeyboardButton("💎 Buy VIP predictions 399⭐ / 10 days", callback_data="stars_vip_signals_10d")])
        return InlineKeyboardMarkup(rows)

    rows = [
        [InlineKeyboardButton("🔥 Trial прогнози", callback_data="signal_trial")],
        [InlineKeyboardButton("🔥 Basic прогнози", callback_data="signal_basic")],
    ]
    if vip_access:
        rows.append([InlineKeyboardButton("💎 VIP прогнози", callback_data="signal_vip")])
    else:
        rows.append([InlineKeyboardButton("💎 Купити VIP прогнози 399⭐ / 10 днів", callback_data="stars_vip_signals_10d")])
    return InlineKeyboardMarkup(rows)


def vip_subscription_keyboard(lang: str = "ua", show_promo: bool = False):
    """
    show_promo=True shows first-payment promo plans.
    show_promo=False shows only regular VIP 1 month.
    """
    if show_promo:
        if lang == "ru":
            keyboard = [
                [InlineKeyboardButton("💎 1 месяц  $19.99 / 1500⭐", callback_data="vip_buy_1m")],
                [InlineKeyboardButton("💎 3 месяца  $50 / 3750⭐ · -17%", callback_data="vip_buy_3m_promo")],
                [InlineKeyboardButton("💎 6 месяцев  $89.99 / 6750⭐ · -25%", callback_data="vip_buy_6m_promo")],
            ]
        elif lang == "en":
            keyboard = [
                [InlineKeyboardButton("💎 1 month  $19.99 / 1500⭐", callback_data="vip_buy_1m")],
                [InlineKeyboardButton("💎 3 months  $50 / 3750⭐ · -17%", callback_data="vip_buy_3m_promo")],
                [InlineKeyboardButton("💎 6 months  $89.99 / 6750⭐ · -25%", callback_data="vip_buy_6m_promo")],
            ]
        else:
            keyboard = [
                [InlineKeyboardButton("💎 1 місяць  $19.99 / 1500⭐", callback_data="vip_buy_1m")],
                [InlineKeyboardButton("💎 3 місяці  $50 / 3750⭐ · -17%", callback_data="vip_buy_3m_promo")],
                [InlineKeyboardButton("💎 6 місяців  $89.99 / 6750⭐ · -25%", callback_data="vip_buy_6m_promo")],
            ]
    else:
        if lang == "ru":
            keyboard = [[InlineKeyboardButton("💎 VIP 1 месяц  $19.99 / 1500⭐", callback_data="vip_buy_1m")]]
        elif lang == "en":
            keyboard = [[InlineKeyboardButton("💎 VIP 1 month  $19.99 / 1500⭐", callback_data="vip_buy_1m")]]
        else:
            keyboard = [[InlineKeyboardButton("💎 VIP 1 місяць  $19.99 / 1500⭐", callback_data="vip_buy_1m")]]
    return InlineKeyboardMarkup(keyboard)


def basic_subscription_keyboard(lang: str = "ua", show_promo: bool = False):
    """Basic plans. show_promo displays first-payment 6-month promo."""
    if show_promo:
        if lang == "ru":
            keyboard = [
                [InlineKeyboardButton("⭐ Basic 1 месяц  $7 / 525⭐", callback_data="basic_buy_1m")],
                [InlineKeyboardButton("⭐ Basic 6 месяцев  $30 (-29%)", callback_data="basic_buy_6m_promo")],
            ]
        elif lang == "en":
            keyboard = [
                [InlineKeyboardButton("⭐ Basic 1 month  $7 / 525⭐", callback_data="basic_buy_1m")],
                [InlineKeyboardButton("⭐ Basic 6 months  $30 (-29%)", callback_data="basic_buy_6m_promo")],
            ]
        else:
            keyboard = [
                [InlineKeyboardButton("⭐ Basic 1 місяць  $7 / 525⭐", callback_data="basic_buy_1m")],
                [InlineKeyboardButton("⭐ Basic 6 місяців  $30 (-29%)", callback_data="basic_buy_6m_promo")],
            ]
    else:
        if lang == "ru":
            keyboard = [[InlineKeyboardButton("⭐ Basic 1 месяц  $7 / 525⭐", callback_data="basic_buy_1m")]]
        elif lang == "en":
            keyboard = [[InlineKeyboardButton("⭐ Basic 1 month  $7 / 525⭐", callback_data="basic_buy_1m")]]
        else:
            keyboard = [[InlineKeyboardButton("⭐ Basic 1 місяць  $7 / 525⭐", callback_data="basic_buy_1m")]]
    return InlineKeyboardMarkup(keyboard)


def vip_signals_payment_keyboard(lang: str = "ua"):
    """Buy VIP signals for $5 / 10 days."""
    if lang == "ru":
        keyboard = [
            [InlineKeyboardButton(" Купить через Stars  399⭐", callback_data="stars_vip_signals_10d")],
            [InlineKeyboardButton(" USDT  $5", callback_data="usdt_vip_signals_10d")],
        ]
    elif lang == "en":
        keyboard = [
            [InlineKeyboardButton(" Pay with Stars  399⭐", callback_data="stars_vip_signals_10d")],
            [InlineKeyboardButton(" USDT  $5", callback_data="usdt_vip_signals_10d")],
        ]
    else:
        keyboard = [
            [InlineKeyboardButton(" Купити через Stars  399⭐", callback_data="stars_vip_signals_10d")],
            [InlineKeyboardButton(" USDT  $5", callback_data="usdt_vip_signals_10d")],
        ]
    return InlineKeyboardMarkup(keyboard)


def settings_keyboard(lang: str = "ua"):
    """Settings menu."""
    if lang == "ru":
        keyboard = [
            [InlineKeyboardButton("🌐 Язык", callback_data="settings_lang")],
            [InlineKeyboardButton("🎟️ Промокод", callback_data="settings_promo")],
            [InlineKeyboardButton("👥 Рефералы", callback_data="settings_referrals")],
            [InlineKeyboardButton("🆘 Поддержка", url="https://t.me/bettracker_support")],
            [InlineKeyboardButton("􀀀􀀀 Инфо", callback_data="settings_info")],
        ]
    elif lang == "en":
        keyboard = [
            [InlineKeyboardButton("🌐 Language", callback_data="settings_lang")],
            [InlineKeyboardButton("🎟️ Promo code", callback_data="settings_promo")],
            [InlineKeyboardButton("👥 Referrals", callback_data="settings_referrals")],
            [InlineKeyboardButton("🆘 Support", url="https://t.me/bettracker_support")],
            [InlineKeyboardButton("􀀀􀀀 Info", callback_data="settings_info")],
        ]
    else:
        keyboard = [
            [InlineKeyboardButton("🌐 Мова", callback_data="settings_lang")],
            [InlineKeyboardButton("🎟️ Промокод", callback_data="settings_promo")],
            [InlineKeyboardButton("👥 Реферали", callback_data="settings_referrals")],
            [InlineKeyboardButton("🆘 Підтримка", url="https://t.me/bettracker_support")],
            [InlineKeyboardButton("􀀀􀀀 Інфо", callback_data="settings_info")],
        ]
    return InlineKeyboardMarkup(keyboard)

def usdt_plans_keyboard(lang: str, promo_available: bool = True):
    if promo_available:
        if lang == "ru":
            keyboard = [
                [InlineKeyboardButton("Basic 1 месяц — $7", callback_data="usdt_basic_month")],
                [InlineKeyboardButton("Basic 6 месяцев — $30 (-29%)", callback_data="usdt_basic_6m_promo")],
                [InlineKeyboardButton("VIP 1 месяц — $19.99", callback_data="usdt_vip_month")],
                [InlineKeyboardButton("VIP 3 месяца — $50 (-17%)", callback_data="usdt_vip_3m_promo")],
                [InlineKeyboardButton("VIP 6 месяцев — $89.99 (-25%)", callback_data="usdt_vip_6m_promo")],
            ]
        elif lang == "en":
            keyboard = [
                [InlineKeyboardButton("Basic 1 month — $7", callback_data="usdt_basic_month")],
                [InlineKeyboardButton("Basic 6 months — $30 (-29%)", callback_data="usdt_basic_6m_promo")],
                [InlineKeyboardButton("VIP 1 month — $19.99", callback_data="usdt_vip_month")],
                [InlineKeyboardButton("VIP 3 months — $50 (-17%)", callback_data="usdt_vip_3m_promo")],
                [InlineKeyboardButton("VIP 6 months — $89.99 (-25%)", callback_data="usdt_vip_6m_promo")],
            ]
        else:
            keyboard = [
                [InlineKeyboardButton("Basic 1 місяць — $7", callback_data="usdt_basic_month")],
                [InlineKeyboardButton("Basic 6 місяців — $30 (-29%)", callback_data="usdt_basic_6m_promo")],
                [InlineKeyboardButton("VIP 1 місяць — $19.99", callback_data="usdt_vip_month")],
                [InlineKeyboardButton("VIP 3 місяці — $50 (-17%)", callback_data="usdt_vip_3m_promo")],
                [InlineKeyboardButton("VIP 6 місяців — $89.99 (-25%)", callback_data="usdt_vip_6m_promo")],
            ]
    else:
        if lang == "ru":
            keyboard = [
                [InlineKeyboardButton("Basic 1 месяц — $7", callback_data="usdt_basic_month")],
                [InlineKeyboardButton("VIP 1 месяц — $19.99", callback_data="usdt_vip_month")],
            ]
        elif lang == "en":
            keyboard = [
                [InlineKeyboardButton("Basic 1 month — $7", callback_data="usdt_basic_month")],
                [InlineKeyboardButton("VIP 1 month — $19.99", callback_data="usdt_vip_month")],
            ]
        else:
            keyboard = [
                [InlineKeyboardButton("Basic 1 місяць — $7", callback_data="usdt_basic_month")],
                [InlineKeyboardButton("VIP 1 місяць — $19.99", callback_data="usdt_vip_month")],
            ]
    return InlineKeyboardMarkup(keyboard)


def cryptobot_plans_keyboard(lang: str, promo_available: bool = True):
    """Keyboard for CryptoBot auto-payment plans."""
    if promo_available:
        if lang == "ru":
            keyboard = [
                [InlineKeyboardButton("Basic 1 месяц - $7 USDT", callback_data="cb_pay_usdt_basic_month")],
                [InlineKeyboardButton("Basic 6 месяцев - $30 USDT (-29%)", callback_data="cb_pay_usdt_basic_6m_promo")],
                [InlineKeyboardButton("VIP 1 месяц - $19.99 USDT", callback_data="cb_pay_usdt_vip_month")],
                [InlineKeyboardButton("VIP 3 месяца - $50 USDT (-17%)", callback_data="cb_pay_usdt_vip_3m_promo")],
                [InlineKeyboardButton("VIP 6 месяцев - $89.99 USDT (-25%)", callback_data="cb_pay_usdt_vip_6m_promo")],
                [InlineKeyboardButton("🧾 Ручная оплата", callback_data="buy_usdt_manual")],
            ]
        elif lang == "en":
            keyboard = [
                [InlineKeyboardButton("Basic 1 month - $7 USDT", callback_data="cb_pay_usdt_basic_month")],
                [InlineKeyboardButton("Basic 6 months - $30 USDT (-29%)", callback_data="cb_pay_usdt_basic_6m_promo")],
                [InlineKeyboardButton("VIP 1 month - $19.99 USDT", callback_data="cb_pay_usdt_vip_month")],
                [InlineKeyboardButton("VIP 3 months - $50 USDT (-17%)", callback_data="cb_pay_usdt_vip_3m_promo")],
                [InlineKeyboardButton("VIP 6 months - $89.99 USDT (-25%)", callback_data="cb_pay_usdt_vip_6m_promo")],
                [InlineKeyboardButton("🧾 Manual payment", callback_data="buy_usdt_manual")],
            ]
        else:
            keyboard = [
                [InlineKeyboardButton("Basic 1 місяць - $7 USDT", callback_data="cb_pay_usdt_basic_month")],
                [InlineKeyboardButton("Basic 6 місяців - $30 USDT (-29%)", callback_data="cb_pay_usdt_basic_6m_promo")],
                [InlineKeyboardButton("VIP 1 місяць - $19.99 USDT", callback_data="cb_pay_usdt_vip_month")],
                [InlineKeyboardButton("VIP 3 місяці - $50 USDT (-17%)", callback_data="cb_pay_usdt_vip_3m_promo")],
                [InlineKeyboardButton("VIP 6 місяців - $89.99 USDT (-25%)", callback_data="cb_pay_usdt_vip_6m_promo")],
                [InlineKeyboardButton("🧾 Ручна оплата", callback_data="buy_usdt_manual")],
            ]
    else:
        if lang == "ru":
            keyboard = [
                [InlineKeyboardButton("Basic 1 месяц - $7 USDT", callback_data="cb_pay_usdt_basic_month")],
                [InlineKeyboardButton("VIP 1 месяц - $19.99 USDT", callback_data="cb_pay_usdt_vip_month")],
                [InlineKeyboardButton("🧾 Ручная оплата", callback_data="buy_usdt_manual")],
            ]
        elif lang == "en":
            keyboard = [
                [InlineKeyboardButton("Basic 1 month - $7 USDT", callback_data="cb_pay_usdt_basic_month")],
                [InlineKeyboardButton("VIP 1 month - $19.99 USDT", callback_data="cb_pay_usdt_vip_month")],
                [InlineKeyboardButton("🧾 Manual payment", callback_data="buy_usdt_manual")],
            ]
        else:
            keyboard = [
                [InlineKeyboardButton("Basic 1 місяць - $7 USDT", callback_data="cb_pay_usdt_basic_month")],
                [InlineKeyboardButton("VIP 1 місяць - $19.99 USDT", callback_data="cb_pay_usdt_vip_month")],
                [InlineKeyboardButton("🧾 Ручна оплата", callback_data="buy_usdt_manual")],
            ]
    return InlineKeyboardMarkup(keyboard)


def tools_keyboard(lang: str):
    if lang == "ru":
        keyboard = [
            [InlineKeyboardButton("🧮 Калькулятор Келли", callback_data="tool_kelly")],
            [InlineKeyboardButton("📊 Лимит банка", callback_data="tool_bank_limit")],
            [InlineKeyboardButton("🧊 ColdMind AI Agent VIP", callback_data="tool_coach")],
            [InlineKeyboardButton("🔥 Streak дисциплины", callback_data="tool_streak")],
        ]
    elif lang == "en":
        keyboard = [
            [InlineKeyboardButton("🧮 Kelly Calculator", callback_data="tool_kelly")],
            [InlineKeyboardButton("📊 Bank limit", callback_data="tool_bank_limit")],
            [InlineKeyboardButton("🧊 ColdMind AI Agent VIP", callback_data="tool_coach")],
            [InlineKeyboardButton("🔥 Discipline streak", callback_data="tool_streak")],
        ]
    else:
        keyboard = [
            [InlineKeyboardButton("🧮 Калькулятор Келлі", callback_data="tool_kelly")],
            [InlineKeyboardButton("📊 Ліміт банку", callback_data="tool_bank_limit")],
            [InlineKeyboardButton("🧊 ColdMind AI Agent VIP", callback_data="tool_coach")],
            [InlineKeyboardButton("🔥 Streak дисципліни", callback_data="tool_streak")],
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
