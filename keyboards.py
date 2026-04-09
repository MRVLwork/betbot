from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton


def welcome_offer_keyboard(lang: str):
    if lang == "ru":
        keyboard = [[
            InlineKeyboardButton("🧪 Попробовать", callback_data="try_trial"),
            InlineKeyboardButton("💳 Оплатить сразу", callback_data="pay_now"),
        ]]
    elif lang == "en":
        keyboard = [[
            InlineKeyboardButton("🧪 Try", callback_data="try_trial"),
            InlineKeyboardButton("💳 Pay now", callback_data="pay_now"),
        ]]
    else:
        keyboard = [[
            InlineKeyboardButton("🧪 Спробувати", callback_data="try_trial"),
            InlineKeyboardButton("💳 Оплатити одразу", callback_data="pay_now"),
        ]]
    return InlineKeyboardMarkup(keyboard)


def main_menu_keyboard(lang: str):
    if lang == "ru":
        keyboard = [
            ["📤 Отправить результат"],
            ["📊 Моя статистика"],
            ["📈 Полная статистика"],
            ["🧠 Аналитика"],
            ["🛠 Все инструменты"],
            ["💳 Купить доступ"],
            ["🌐 Язык"],
        ]
    elif lang == "en":
        keyboard = [
            ["📤 Send result"],
            ["📊 My stats"],
            ["📈 Full stats"],
            ["🧠 Analytics"],
            ["🛠 All tools"],
            ["💳 Buy access"],
            ["🌐 Language"],
        ]
    else:
        keyboard = [
            ["📤 Надіслати результат"],
            ["📊 Моя статистика"],
            ["📈 Повна статистика"],
            ["🧠 Аналітика"],
            ["🛠 Усі інструменти"],
            ["💳 Купити доступ"],
            ["🌐 Мова"],
        ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


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
                [InlineKeyboardButton("🧪 Попробовать — 99 ⭐", callback_data="stars_basic_trial")],
                [InlineKeyboardButton("🔥 Basic 1 месяц: 499 → 399 ⭐", callback_data="stars_basic_month")],
                [InlineKeyboardButton("VIP 7 дней — 499 ⭐", callback_data="stars_vip_week")],
                [InlineKeyboardButton("🔥 VIP 1 месяц: 1999 → 1499 ⭐", callback_data="stars_vip_month_promo")],
            ]
        elif lang == "en":
            keyboard = [
                [InlineKeyboardButton("🧪 Try — 99 ⭐", callback_data="stars_basic_trial")],
                [InlineKeyboardButton("🔥 Basic 1 month: 499 → 399 ⭐", callback_data="stars_basic_month")],
                [InlineKeyboardButton("VIP 7 days — 499 ⭐", callback_data="stars_vip_week")],
                [InlineKeyboardButton("🔥 VIP 1 month: 1999 → 1499 ⭐", callback_data="stars_vip_month_promo")],
            ]
        else:
            keyboard = [
                [InlineKeyboardButton("🧪 Спробувати — 99 ⭐", callback_data="stars_basic_trial")],
                [InlineKeyboardButton("🔥 Basic 1 місяць: 499 → 399 ⭐", callback_data="stars_basic_month")],
                [InlineKeyboardButton("VIP 7 днів — 499 ⭐", callback_data="stars_vip_week")],
                [InlineKeyboardButton("🔥 VIP 1 місяць: 1999 → 1499 ⭐", callback_data="stars_vip_month_promo")],
            ]
    else:
        if lang == "ru":
            keyboard = [
                [InlineKeyboardButton("Basic 1 месяц — 499 ⭐", callback_data="stars_basic_month_full")],
                [InlineKeyboardButton("VIP 7 дней — 499 ⭐", callback_data="stars_vip_week")],
                [InlineKeyboardButton("VIP 1 месяц — 1999 ⭐", callback_data="stars_vip_month_full")],
            ]
        elif lang == "en":
            keyboard = [
                [InlineKeyboardButton("Basic 1 month — 499 ⭐", callback_data="stars_basic_month_full")],
                [InlineKeyboardButton("VIP 7 days — 499 ⭐", callback_data="stars_vip_week")],
                [InlineKeyboardButton("VIP 1 month — 1999 ⭐", callback_data="stars_vip_month_full")],
            ]
        else:
            keyboard = [
                [InlineKeyboardButton("Basic 1 місяць — 499 ⭐", callback_data="stars_basic_month_full")],
                [InlineKeyboardButton("VIP 7 днів — 499 ⭐", callback_data="stars_vip_week")],
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
