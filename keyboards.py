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
    if is_vip:
        coach_label = "рџ§  AI РўСЂРµРЅРµСЂ" if lang in ("ua", "ru") else "рџ§  AI Coach"
    else:
        coach_label = "рџ”’ AI РўСЂРµРЅРµСЂ VIP" if lang in ("ua", "ru") else "рџ”’ AI Coach VIP"

    if lang == "ru":
        keyboard = [
            ["рџ‘¤ РџСЂРѕС„РёР»СЊ"],
            ["рџ“Љ РњРѕСЏ СЃС‚Р°С‚РёСЃС‚РёРєР°"],
            ["рџ“€ РџРѕР»РЅР°СЏ СЃС‚Р°С‚РёСЃС‚РёРєР°"],
            ["рџ“Љ Wrapped"],
            [coach_label],
            ["рџ§  РђРЅР°Р»РёС‚РёРєР°"],
            ["рџ”Ґ Streak"],
            ["рџ›  Р’СЃРµ РёРЅСЃС‚СЂСѓРјРµРЅС‚С‹"],
            ["рџ’і РљСѓРїРёС‚СЊ РґРѕСЃС‚СѓРї"],
            ["рџЊђ РЇР·С‹Рє"],
        ]
    elif lang == "en":
        keyboard = [
            ["рџ‘¤ Profile"],
            ["рџ“Љ My stats"],
            ["рџ“€ Full stats"],
            ["рџ“Љ Wrapped"],
            [coach_label],
            ["рџ§  Analytics"],
            ["рџ”Ґ Streak"],
            ["рџ›  All tools"],
            ["рџ’і Buy access"],
            ["рџЊђ Language"],
        ]
    else:
        keyboard = [
            ["рџ‘¤ РџСЂРѕС„С–Р»СЊ"],
            ["рџ“Љ РњРѕСЏ СЃС‚Р°С‚РёСЃС‚РёРєР°"],
            ["рџ“€ РџРѕРІРЅР° СЃС‚Р°С‚РёСЃС‚РёРєР°"],
            ["рџ“Љ Wrapped"],
            [coach_label],
            ["рџ§  РђРЅР°Р»С–С‚РёРєР°"],
            ["рџ”Ґ Streak"],
            ["рџ›  РЈСЃС– С–РЅСЃС‚СЂСѓРјРµРЅС‚Рё"],
            ["рџ’і РљСѓРїРёС‚Рё РґРѕСЃС‚СѓРї"],
            ["рџЊђ РњРѕРІР°"],
        ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def access_keyboard(lang: str):
    if lang == "ru":
        keyboard = [
            [InlineKeyboardButton("рџ”‘ Р’РІРµСЃС‚Рё РїСЂРѕРјРѕРєРѕРґ", callback_data="enter_promo")],
            [InlineKeyboardButton("в­ђ РљСѓРїРёС‚СЊ С‡РµСЂРµР· Stars", callback_data="buy_stars")],
            [InlineKeyboardButton("рџ’ё РћРїР»Р°С‚РёС‚СЊ USDT", callback_data="buy_usdt")],
        ]
    elif lang == "en":
        keyboard = [
            [InlineKeyboardButton("рџ”‘ Enter promo code", callback_data="enter_promo")],
            [InlineKeyboardButton("в­ђ Buy via Stars", callback_data="buy_stars")],
            [InlineKeyboardButton("рџ’ё Pay via USDT", callback_data="buy_usdt")],
        ]
    else:
        keyboard = [
            [InlineKeyboardButton("рџ”‘ Р’РІРµСЃС‚Рё РїСЂРѕРјРѕРєРѕРґ", callback_data="enter_promo")],
            [InlineKeyboardButton("в­ђ РљСѓРїРёС‚Рё С‡РµСЂРµР· Stars", callback_data="buy_stars")],
            [InlineKeyboardButton("рџ’ё РћРїР»Р°С‚РёС‚Рё USDT", callback_data="buy_usdt")],
        ]
    return InlineKeyboardMarkup(keyboard)


def stars_plans_keyboard(lang: str, promo_available: bool = True):
    if promo_available:
        if lang == "ru":
            keyboard = [
                [InlineKeyboardButton("рџ§Є РџРѕРїСЂРѕР±РѕРІР°С‚СЊ вЂ” 99 в­ђ", callback_data="stars_basic_week")],
                [InlineKeyboardButton("рџ”Ґ Basic 1 РјРµСЃСЏС†: 499 в†’ 399 в­ђ", callback_data="stars_basic_month")],
                [InlineKeyboardButton("рџ”Ґ VIP 1 РјРµСЃСЏС†: 1999 в†’ 1499 в­ђ", callback_data="stars_vip_month_promo")],
            ]
        elif lang == "en":
            keyboard = [
                [InlineKeyboardButton("рџ§Є Try вЂ” 99 в­ђ", callback_data="stars_basic_week")],
                [InlineKeyboardButton("рџ”Ґ Basic 1 month: 499 в†’ 399 в­ђ", callback_data="stars_basic_month")],
                [InlineKeyboardButton("рџ”Ґ VIP 1 month: 1999 в†’ 1499 в­ђ", callback_data="stars_vip_month_promo")],
            ]
        else:
            keyboard = [
                [InlineKeyboardButton("рџ§Є РЎРїСЂРѕР±СѓРІР°С‚Рё вЂ” 99 в­ђ", callback_data="stars_basic_week")],
                [InlineKeyboardButton("рџ”Ґ Basic 1 РјС–СЃСЏС†СЊ: 499 в†’ 399 в­ђ", callback_data="stars_basic_month")],
                [InlineKeyboardButton("рџ”Ґ VIP 1 РјС–СЃСЏС†СЊ: 1999 в†’ 1499 в­ђ", callback_data="stars_vip_month_promo")],
            ]
    else:
        if lang == "ru":
            keyboard = [
                [InlineKeyboardButton("рџ§Є РџРѕРїСЂРѕР±РѕРІР°С‚СЊ вЂ” 99 в­ђ", callback_data="stars_basic_week")],
                [InlineKeyboardButton("Basic 1 РјРµСЃСЏС† вЂ” 499 в­ђ", callback_data="stars_basic_month_full")],
                [InlineKeyboardButton("VIP 1 РјРµСЃСЏС† вЂ” 1999 в­ђ", callback_data="stars_vip_month_full")],
            ]
        elif lang == "en":
            keyboard = [
                [InlineKeyboardButton("рџ§Є Try вЂ” 99 в­ђ", callback_data="stars_basic_week")],
                [InlineKeyboardButton("Basic 1 month вЂ” 499 в­ђ", callback_data="stars_basic_month_full")],
                [InlineKeyboardButton("VIP 1 month вЂ” 1999 в­ђ", callback_data="stars_vip_month_full")],
            ]
        else:
            keyboard = [
                [InlineKeyboardButton("рџ§Є РЎРїСЂРѕР±СѓРІР°С‚Рё вЂ” 99 в­ђ", callback_data="stars_basic_week")],
                [InlineKeyboardButton("Basic 1 РјС–СЃСЏС†СЊ вЂ” 499 в­ђ", callback_data="stars_basic_month_full")],
                [InlineKeyboardButton("VIP 1 РјС–СЃСЏС†СЊ вЂ” 1999 в­ђ", callback_data="stars_vip_month_full")],
            ]
    return InlineKeyboardMarkup(keyboard)


def usdt_plans_keyboard(lang: str, promo_available: bool = True):
    if promo_available:
        if lang == "ru":
            keyboard = [
                [InlineKeyboardButton("Basic 1 РјРµСЃСЏС† вЂ” 5$", callback_data="usdt_basic_month")],
                [InlineKeyboardButton("рџ”Ґ VIP 1 РјРµСЃСЏС†: 19.99$ в†’ 14.99$", callback_data="usdt_vip_month_promo")],
            ]
        elif lang == "en":
            keyboard = [
                [InlineKeyboardButton("Basic 1 month вЂ” 5$", callback_data="usdt_basic_month")],
                [InlineKeyboardButton("рџ”Ґ VIP 1 month: 19.99$ в†’ 14.99$", callback_data="usdt_vip_month_promo")],
            ]
        else:
            keyboard = [
                [InlineKeyboardButton("Basic 1 РјС–СЃСЏС†СЊ вЂ” 5$", callback_data="usdt_basic_month")],
                [InlineKeyboardButton("рџ”Ґ VIP 1 РјС–СЃСЏС†СЊ: 19.99$ в†’ 14.99$", callback_data="usdt_vip_month_promo")],
            ]
    else:
        if lang == "ru":
            keyboard = [
                [InlineKeyboardButton("Basic 1 РјРµСЃСЏС† вЂ” 5$", callback_data="usdt_basic_month")],
                [InlineKeyboardButton("VIP 1 РјРµСЃСЏС† вЂ” 19.99$", callback_data="usdt_vip_month_full")],
            ]
        elif lang == "en":
            keyboard = [
                [InlineKeyboardButton("Basic 1 month вЂ” 5$", callback_data="usdt_basic_month")],
                [InlineKeyboardButton("VIP 1 month вЂ” 19.99$", callback_data="usdt_vip_month_full")],
            ]
        else:
            keyboard = [
                [InlineKeyboardButton("Basic 1 РјС–СЃСЏС†СЊ вЂ” 5$", callback_data="usdt_basic_month")],
                [InlineKeyboardButton("VIP 1 РјС–СЃСЏС†СЊ вЂ” 19.99$", callback_data="usdt_vip_month_full")],
            ]
    return InlineKeyboardMarkup(keyboard)


def cryptobot_plans_keyboard(lang: str, promo_available: bool = True):
    """Keyboard for CryptoBot auto-payment plans."""
    if promo_available:
        if lang == "ru":
            keyboard = [
                [InlineKeyboardButton("Basic 1 РјРµСЃСЏС† - $5 USDT", callback_data="cb_pay_usdt_basic_month")],
                [InlineKeyboardButton("рџ”Ґ VIP 1 РјРµСЃСЏС†: $19.99 -> $14.99 USDT", callback_data="cb_pay_usdt_vip_month_promo")],
                [InlineKeyboardButton("рџ§ѕ Р СѓС‡РЅР°СЏ РѕРїР»Р°С‚Р°", callback_data="buy_usdt_manual")],
            ]
        elif lang == "en":
            keyboard = [
                [InlineKeyboardButton("Basic 1 month - $5 USDT", callback_data="cb_pay_usdt_basic_month")],
                [InlineKeyboardButton("рџ”Ґ VIP 1 month: $19.99 -> $14.99 USDT", callback_data="cb_pay_usdt_vip_month_promo")],
                [InlineKeyboardButton("рџ§ѕ Manual payment", callback_data="buy_usdt_manual")],
            ]
        else:
            keyboard = [
                [InlineKeyboardButton("Basic 1 РјС–СЃСЏС†СЊ - $5 USDT", callback_data="cb_pay_usdt_basic_month")],
                [InlineKeyboardButton("рџ”Ґ VIP 1 РјС–СЃСЏС†СЊ: $19.99 -> $14.99 USDT", callback_data="cb_pay_usdt_vip_month_promo")],
                [InlineKeyboardButton("рџ§ѕ Р СѓС‡РЅР° РѕРїР»Р°С‚Р°", callback_data="buy_usdt_manual")],
            ]
    else:
        if lang == "ru":
            keyboard = [
                [InlineKeyboardButton("Basic 1 РјРµСЃСЏС† - $5 USDT", callback_data="cb_pay_usdt_basic_month")],
                [InlineKeyboardButton("VIP 1 РјРµСЃСЏС† - $19.99 USDT", callback_data="cb_pay_usdt_vip_month")],
                [InlineKeyboardButton("рџ§ѕ Р СѓС‡РЅР°СЏ РѕРїР»Р°С‚Р°", callback_data="buy_usdt_manual")],
            ]
        elif lang == "en":
            keyboard = [
                [InlineKeyboardButton("Basic 1 month - $5 USDT", callback_data="cb_pay_usdt_basic_month")],
                [InlineKeyboardButton("VIP 1 month - $19.99 USDT", callback_data="cb_pay_usdt_vip_month")],
                [InlineKeyboardButton("рџ§ѕ Manual payment", callback_data="buy_usdt_manual")],
            ]
        else:
            keyboard = [
                [InlineKeyboardButton("Basic 1 РјС–СЃСЏС†СЊ - $5 USDT", callback_data="cb_pay_usdt_basic_month")],
                [InlineKeyboardButton("VIP 1 РјС–СЃСЏС†СЊ - $19.99 USDT", callback_data="cb_pay_usdt_vip_month")],
                [InlineKeyboardButton("рџ§ѕ Р СѓС‡РЅР° РѕРїР»Р°С‚Р°", callback_data="buy_usdt_manual")],
            ]
    return InlineKeyboardMarkup(keyboard)


def tools_keyboard(lang: str):
    if lang == "ru":
        keyboard = [
            [InlineKeyboardButton("рџЋЇ РЎС‚Р°РІРєР° РґРЅСЏ", callback_data="tool_bet_day")],
            [InlineKeyboardButton("вљЎ Live", callback_data="tool_live")],
            [InlineKeyboardButton("рџ¤– AI-Р°РЅР°Р»РёР·", callback_data="tool_ai")],
            [InlineKeyboardButton("рџљЂ Р§РµР»Р»РµРЅРґР¶", callback_data="tool_challenge")],
        ]
    elif lang == "en":
        keyboard = [
            [InlineKeyboardButton("рџЋЇ Bet of the day", callback_data="tool_bet_day")],
            [InlineKeyboardButton("вљЎ Live", callback_data="tool_live")],
            [InlineKeyboardButton("рџ¤– AI analysis", callback_data="tool_ai")],
            [InlineKeyboardButton("рџљЂ Challenge", callback_data="tool_challenge")],
        ]
    else:
        keyboard = [
            [InlineKeyboardButton("рџЋЇ РЎС‚Р°РІРєР° РґРЅСЏ", callback_data="tool_bet_day")],
            [InlineKeyboardButton("вљЎ Live", callback_data="tool_live")],
            [InlineKeyboardButton("рџ¤– AI-Р°РЅР°Р»С–Р·", callback_data="tool_ai")],
            [InlineKeyboardButton("рџљЂ Р§РµР»РµРЅРґР¶", callback_data="tool_challenge")],
        ]
    return InlineKeyboardMarkup(keyboard)


def bet_day_menu_keyboard(lang: str):
    if lang == "ru":
        keyboard = [
            [InlineKeyboardButton("рџЋЇ РЎС‚Р°РІРєР° РґРЅСЏ (Basic)", callback_data="betday_basic")],
            [InlineKeyboardButton("рџ”Ґ РЎС‚Р°РІРєР° РґРЅСЏ (VIP)", callback_data="betday_vip")],
            [InlineKeyboardButton("в¬…пёЏ РќР°Р·Р°Рґ", callback_data="tools_back")],
        ]
    elif lang == "en":
        keyboard = [
            [InlineKeyboardButton("рџЋЇ Bet of the day (Basic)", callback_data="betday_basic")],
            [InlineKeyboardButton("рџ”Ґ Bet of the day (VIP)", callback_data="betday_vip")],
            [InlineKeyboardButton("в¬…пёЏ Back", callback_data="tools_back")],
        ]
    else:
        keyboard = [
            [InlineKeyboardButton("рџЋЇ РЎС‚Р°РІРєР° РґРЅСЏ (Basic)", callback_data="betday_basic")],
            [InlineKeyboardButton("рџ”Ґ РЎС‚Р°РІРєР° РґРЅСЏ (VIP)", callback_data="betday_vip")],
            [InlineKeyboardButton("в¬…пёЏ РќР°Р·Р°Рґ", callback_data="tools_back")],
        ]
    return InlineKeyboardMarkup(keyboard)


def bet_day_basic_keyboard(lang: str, is_subscribed: bool = False):
    if lang == "ru":
        subscribe = "вњ… РўС‹ РїРѕРґРїРёСЃР°РЅ" if is_subscribed else "рџ”” РџРѕРґРїРёСЃР°С‚СЊСЃСЏ"
        keyboard = [
            [InlineKeyboardButton(subscribe, callback_data="betday_basic_subscribe")],
            [InlineKeyboardButton("в¬…пёЏ РќР°Р·Р°Рґ", callback_data="tool_bet_day")],
        ]
    elif lang == "en":
        subscribe = "вњ… You are subscribed" if is_subscribed else "рџ”” Subscribe"
        keyboard = [
            [InlineKeyboardButton(subscribe, callback_data="betday_basic_subscribe")],
            [InlineKeyboardButton("в¬…пёЏ Back", callback_data="tool_bet_day")],
        ]
    else:
        subscribe = "вњ… РўРё РїС–РґРїРёСЃР°РЅРёР№" if is_subscribed else "рџ”” РџС–РґРїРёСЃР°С‚РёСЃСЏ"
        keyboard = [
            [InlineKeyboardButton(subscribe, callback_data="betday_basic_subscribe")],
            [InlineKeyboardButton("в¬…пёЏ РќР°Р·Р°Рґ", callback_data="tool_bet_day")],
        ]
    return InlineKeyboardMarkup(keyboard)


def bet_day_vip_keyboard(lang: str, has_access: bool = False, is_subscribed: bool = False):
    rows = []
    if has_access:
        if lang == "ru":
            subscribe = "вњ… РўС‹ РїРѕРґРїРёСЃР°РЅ" if is_subscribed else "рџ”” РџРѕРґРїРёСЃР°С‚СЊСЃСЏ"
        elif lang == "en":
            subscribe = "вњ… You are subscribed" if is_subscribed else "рџ”” Subscribe"
        else:
            subscribe = "вњ… РўРё РїС–РґРїРёСЃР°РЅРёР№" if is_subscribed else "рџ”” РџС–РґРїРёСЃР°С‚РёСЃСЏ"
        rows.append([InlineKeyboardButton(subscribe, callback_data="betday_vip_subscribe")])
    else:
        if lang == "ru":
            rows.append([InlineKeyboardButton("рџ’ё РљСѓРїРёС‚СЊ Р·Р° 4.99$", callback_data="usdt_vip_bet_day_month")])
            rows.append([InlineKeyboardButton("в­ђ РљСѓРїРёС‚СЊ Р·Р° 499 Stars", callback_data="stars_vip_bet_day_month")])
        elif lang == "en":
            rows.append([InlineKeyboardButton("рџ’ё Buy for $4.99", callback_data="usdt_vip_bet_day_month")])
            rows.append([InlineKeyboardButton("в­ђ Buy for 499 Stars", callback_data="stars_vip_bet_day_month")])
        else:
            rows.append([InlineKeyboardButton("рџ’ё РљСѓРїРёС‚Рё Р·Р° 4.99$", callback_data="usdt_vip_bet_day_month")])
            rows.append([InlineKeyboardButton("в­ђ РљСѓРїРёС‚Рё Р·Р° 499 Stars", callback_data="stars_vip_bet_day_month")])

    back_text = "в¬…пёЏ РќР°Р·Р°Рґ" if lang in ("ru", "ua") else "в¬…пёЏ Back"
    rows.append([InlineKeyboardButton(back_text, callback_data="tool_bet_day")])
    return InlineKeyboardMarkup(rows)


def payment_check_keyboard(lang: str):
    if lang == "ru":
        confirm_text = "вњ… РЇ РѕРїР»Р°С‚РёР»"
        cancel_text = "вќЊ РћС‚РјРµРЅРёС‚СЊ"
    elif lang == "en":
        confirm_text = "вњ… I paid"
        cancel_text = "вќЊ Cancel"
    else:
        confirm_text = "вњ… РЇ РѕРїР»Р°С‚РёРІ"
        cancel_text = "вќЊ РЎРєР°СЃСѓРІР°С‚Рё"

    return InlineKeyboardMarkup([
        [InlineKeyboardButton(confirm_text, callback_data="payment_sent")],
        [InlineKeyboardButton(cancel_text, callback_data="cancel_payment")],
    ])


def stats_periods_keyboard(is_vip: bool, lang: str, prefix: str = "stats"):
    if lang == "ru":
        keyboard = [
            [InlineKeyboardButton("РЎРµРіРѕРґРЅСЏ", callback_data=f"{prefix}_today")],
            [InlineKeyboardButton("Р’С‡РµСЂР°", callback_data=f"{prefix}_yesterday")],
            [InlineKeyboardButton("3 РґРЅСЏ", callback_data=f"{prefix}_3days")],
            [InlineKeyboardButton("7 РґРЅРµР№", callback_data=f"{prefix}_7days")],
            [InlineKeyboardButton("30 РґРЅРµР№", callback_data=f"{prefix}_30days")],
        ]
        if is_vip:
            keyboard.append([InlineKeyboardButton("РўРµРєСѓС‰Р°СЏ РЅРµРґРµР»СЏ", callback_data=f"{prefix}_current_week")])
            keyboard.append([InlineKeyboardButton("РўРµРєСѓС‰РёР№ РјРµСЃСЏС†", callback_data=f"{prefix}_current_month")])
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
            [InlineKeyboardButton("РЎСЊРѕРіРѕРґРЅС–", callback_data=f"{prefix}_today")],
            [InlineKeyboardButton("Р’С‡РѕСЂР°", callback_data=f"{prefix}_yesterday")],
            [InlineKeyboardButton("3 РґРЅС–", callback_data=f"{prefix}_3days")],
            [InlineKeyboardButton("7 РґРЅС–РІ", callback_data=f"{prefix}_7days")],
            [InlineKeyboardButton("30 РґРЅС–РІ", callback_data=f"{prefix}_30days")],
        ]
        if is_vip:
            keyboard.append([InlineKeyboardButton("РџРѕС‚РѕС‡РЅРёР№ С‚РёР¶РґРµРЅСЊ", callback_data=f"{prefix}_current_week")])
            keyboard.append([InlineKeyboardButton("РџРѕС‚РѕС‡РЅРёР№ РјС–СЃСЏС†СЊ", callback_data=f"{prefix}_current_month")])

    return InlineKeyboardMarkup(keyboard)


def language_keyboard():
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("рџ‡єрџ‡¦ РЈРєСЂР°С—РЅСЃСЊРєР°", callback_data="lang_ua"),
        InlineKeyboardButton("рџ‡·рџ‡є Р СѓСЃСЃРєРёР№", callback_data="lang_ru"),
        InlineKeyboardButton("рџ‡¬рџ‡§ English", callback_data="lang_en"),
    ]])
