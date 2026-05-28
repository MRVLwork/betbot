# -*- coding: utf-8 -*-
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from db import get_user


def _normalize_lang(lang):
    lang = (lang or "ua").lower()
    if lang.startswith("uk") or lang.startswith("ua"):
        return "ua"
    if lang.startswith("ru"):
        return "ru"
    if lang.startswith("en"):
        return "en"
    return "ua"


PLAN_PAYMENT_MAP = {
    "vip_buy_1m": {
        "stars_cb": "stars_vip_1m",
        "usdt_cb": "usdt_vip_month",
        "label_ua": "VIP 1 місяць",
        "label_ru": "VIP 1 месяц",
        "label_en": "VIP 1 month",
        "usd": "19.99",
        "stars": "1500",
    },
    "vip_buy_3m_promo": {
        "stars_cb": "stars_vip_3m_promo",
        "usdt_cb": "usdt_vip_3m_promo",
        "label_ua": "VIP 3 місяці (-17%)",
        "label_ru": "VIP 3 месяца (-17%)",
        "label_en": "VIP 3 months (-17%)",
        "usd": "50",
        "stars": "3750",
    },
    "vip_buy_6m_promo": {
        "stars_cb": "stars_vip_6m_promo",
        "usdt_cb": "usdt_vip_6m_promo",
        "label_ua": "VIP 6 місяців (-25%)",
        "label_ru": "VIP 6 месяцев (-25%)",
        "label_en": "VIP 6 months (-25%)",
        "usd": "89.99",
        "stars": "6750",
    },
    "basic_buy_1m": {
        "stars_cb": "stars_basic_month",
        "usdt_cb": "usdt_basic_month",
        "label_ua": "Basic 1 місяць",
        "label_ru": "Basic 1 месяц",
        "label_en": "Basic 1 month",
        "usd": "7",
        "stars": "525",
    },
    "basic_buy_6m_promo": {
        "stars_cb": "stars_basic_6m_promo",
        "usdt_cb": "usdt_basic_6m_promo",
        "label_ua": "Basic 6 місяців (-29%)",
        "label_ru": "Basic 6 месяцев (-29%)",
        "label_en": "Basic 6 months (-29%)",
        "usd": "30",
        "stars": "2250",
    },
}


async def plan_payment_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show Stars / USDT payment choice after a plan is selected."""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    user = get_user(user_id) or {}
    lang = _normalize_lang(user.get("lang"))

    plan = PLAN_PAYMENT_MAP.get(query.data)
    if not plan:
        return

    label = plan.get(f"label_{lang}") or plan["label_ua"]
    usd = plan["usd"]
    stars = plan["stars"]

    if lang == "ru":
        text = (
            f"💎 *{label}*\n\n"
            f"Выбери способ оплаты:\n\n"
            f"⭐ Stars: {stars}\n"
            f"💵 USDT: ${usd}"
        )
        stars_btn = f"⭐ Оплатить Stars  {stars}"
        usdt_btn = f"💵 Оплатить USDT  ${usd}"
    elif lang == "en":
        text = (
            f"💎 *{label}*\n\n"
            f"Choose payment method:\n\n"
            f"⭐ Stars: {stars}\n"
            f"💵 USDT: ${usd}"
        )
        stars_btn = f"⭐ Pay Stars  {stars}"
        usdt_btn = f"💵 Pay USDT  ${usd}"
    else:
        text = (
            f"💎 *{label}*\n\n"
            f"Обери спосіб оплати:\n\n"
            f"⭐ Stars: {stars}\n"
            f"💵 USDT: ${usd}"
        )
        stars_btn = f"⭐ Оплатити Stars  {stars}"
        usdt_btn = f"💵 Оплатити USDT  ${usd}"

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(stars_btn, callback_data=plan["stars_cb"])],
        [InlineKeyboardButton(usdt_btn, callback_data=f"cb_pay_{plan['usdt_cb']}")],
    ])

    await query.message.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=keyboard,
    )
