# -*- coding: utf-8 -*-
from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from db import (
    get_user,
    get_subscription_type,
    subscribe_to_signal,
    is_subscribed_to_signal,
    is_eligible_for_first_payment_promo,
)


def _normalize_lang(lang):
    lang = (lang or "ua").lower()
    if lang.startswith("uk") or lang.startswith("ua"):
        return "ua"
    if lang.startswith("ru"):
        return "ru"
    if lang.startswith("en"):
        return "en"
    return "ua"


def _get_vip_signals_active(user_id: int) -> bool:
    """VIP signals are active for VIP users or Basic users with separate access."""
    sub_type = get_subscription_type(user_id)
    if sub_type == "vip":
        return True

    user = get_user(user_id) or {}
    expires = user.get("vip_signals_expires_at")
    if not expires:
        return False

    try:
        return datetime.fromisoformat(expires) > datetime.now()
    except Exception:
        return False


async def open_signals_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show AI signal subscription menu."""
    if not update.message:
        return

    user_id = update.effective_user.id
    user = get_user(user_id) or {}
    lang = _normalize_lang(user.get("lang"))
    sub_type = get_subscription_type(user_id)

    if sub_type == "trial" and not is_subscribed_to_signal(user_id, "trial"):
        subscribe_to_signal(user_id, "trial")

    if sub_type in ("basic", "vip") and not is_subscribed_to_signal(user_id, "basic"):
        subscribe_to_signal(user_id, "basic")

    if sub_type == "vip" and not is_subscribed_to_signal(user_id, "vip"):
        subscribe_to_signal(user_id, "vip")

    if lang == "ru":
        title = (
            "🔥 *AI Прогнозы дня*\n\n"
            "Готовые ставки от AI-агента -\n"
            "бери и зарабатывай умнее.\n\n"
            "Выбери уровень прогнозов:"
        )
    elif lang == "en":
        title = (
            "🔥 *AI Predictions of the day*\n\n"
            "Ready-to-bet picks from AI agent -\n"
            "take and earn smarter.\n\n"
            "Choose prediction level:"
        )
    else:
        title = (
            "🔥 *AI Прогнози дня*\n\n"
            "Готові ставки від AI-агента -\n"
            "бери і заробляй розумніше.\n\n"
            "Обери рівень прогнозів:"
        )

    vip_signals_active = _get_vip_signals_active(user_id)

    if sub_type == "trial":
        labels = {
            "ua": [
                "🔥 Trial Прогнози (активні)",
                "🔥 Basic Прогнози - купити підписку",
                "💎 VIP Прогнози - купити підписку",
            ],
            "ru": [
                "🔥 Trial Прогнозы (активны)",
                "🔥 Basic Прогнозы - купить подписку",
                "💎 VIP Прогнозы - купить подписку",
            ],
            "en": [
                "🔥 Trial Predictions (active)",
                "🔥 Basic Predictions - buy subscription",
                "💎 VIP Predictions - buy subscription",
            ],
        }
        label = labels.get(lang, labels["ua"])
        buttons = [
            [InlineKeyboardButton(label[0], callback_data="signals_trial_info")],
            [InlineKeyboardButton(label[1], callback_data="signals_buy_basic")],
            [InlineKeyboardButton(label[2], callback_data="signals_buy_vip")],
        ]
    elif sub_type == "basic":
        vip_label_active = {
            "ua": "💎 VIP Прогнози (активні)",
            "ru": "💎 VIP Прогнозы (активны)",
            "en": "💎 VIP Predictions (active)",
        }
        vip_label_buy = {
            "ua": "💎 VIP Прогнози  $5 / 10 днів",
            "ru": "💎 VIP Прогнозы  $5 / 10 дней",
            "en": "💎 VIP Predictions  $5 / 10 days",
        }
        basic_label = {
            "ua": "🔥 Basic Прогнози (активні)",
            "ru": "🔥 Basic Прогнозы (активны)",
            "en": "🔥 Basic Predictions (active)",
        }
        buttons = [
            [InlineKeyboardButton(basic_label.get(lang, basic_label["ua"]), callback_data="signals_basic_info")],
        ]
        if vip_signals_active:
            buttons.append([InlineKeyboardButton(vip_label_active.get(lang, vip_label_active["ua"]), callback_data="signals_vip_info")])
        else:
            buttons.append([InlineKeyboardButton(vip_label_buy.get(lang, vip_label_buy["ua"]), callback_data="signals_buy_vip_for_basic")])
    elif sub_type == "vip":
        labels = {
            "ua": ["🔥 Basic Прогнози (активні)", "💎 VIP Прогнози (активні)"],
            "ru": ["🔥 Basic Прогнозы (активны)", "💎 VIP Прогнозы (активны)"],
            "en": ["🔥 Basic Predictions (active)", "💎 VIP Predictions (active)"],
        }
        label = labels.get(lang, labels["ua"])
        buttons = [
            [InlineKeyboardButton(label[0], callback_data="signals_basic_info")],
            [InlineKeyboardButton(label[1], callback_data="signals_vip_info")],
        ]
    else:
        no_access = {
            "ua": "Для AI Прогнозів потрібна активна підписка.",
            "ru": "Для AI Прогнозов нужна активная подписка.",
            "en": "Active subscription required for AI Predictions.",
        }
        await update.message.reply_text(no_access.get(lang, no_access["ua"]))
        return

    await update.message.reply_text(
        title,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode="Markdown",
    )


async def signals_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle AI signals menu callbacks."""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    user = get_user(user_id) or {}
    lang = _normalize_lang(user.get("lang"))
    data = query.data

    if data in ("signals_trial_info", "signals_basic_info", "signals_vip_info"):
        info = {
            "ua": "✅ Підписка активна. Очікуй AI Прогнози від AI-агента - вони приходитимуть автоматично, коли є цінні події.",
            "ru": "✅ Подписка активна. Ожидай AI Прогнозы от AI-агента - они будут приходить автоматически, когда есть ценные события.",
            "en": "✅ Subscription active. Wait for AI Predictions from the AI agent - they will arrive automatically when valuable events appear.",
        }
        await query.message.reply_text(info.get(lang, info["ua"]))
        return

    if data == "signals_buy_basic":
        from keyboards import access_keyboard

        promo = {
            "ua": (
                "💰 *Basic підписка  $7/міс*\n\n"
                "Заробляй на ставках розумніше:\n\n"
                "Що отримуєш:\n"
                " 🔥 AI Прогнози Basic щодня\n"
                " 15 скрінів/день\n"
                " Повна статистика з інсайтами\n"
                " Калькулятор Келлі\n"
                " Ліміт банку\n\n"
                " Обери спосіб оплати:"
            ),
            "ru": (
                "💰 *Basic подписка  $7/мес*\n\n"
                "Зарабатывай на ставках умнее:\n\n"
                "Что получаешь:\n"
                " 🔥 AI Прогнозы Basic каждый день\n"
                " 15 скринов/день\n"
                " Полная статистика с инсайтами\n"
                " Калькулятор Келли\n"
                " Лимит банка\n\n"
                " Выбери способ оплаты:"
            ),
            "en": (
                "💰 *Basic  $7/mo*\n\n"
                "Bet smarter, earn more:\n\n"
                "Includes:\n"
                " 🔥 Basic AI Predictions daily\n"
                " 15 screens/day\n"
                " Full stats with insights\n"
                " Kelly Calculator\n"
                " Bank limit\n\n"
                " Choose payment:"
            ),
        }
        await query.message.reply_text(
            promo.get(lang, promo["ua"]),
            parse_mode="Markdown",
            reply_markup=access_keyboard(lang),
        )
        return

    if data == "signals_buy_vip":
        from keyboards import vip_subscription_keyboard

        promo = {
            "ua": (
                "💎 *VIP підписка*\n\n"
                "Заробляй на ставках розумніше:\n\n"
                "Що отримуєш:\n"
                " 🔥 AI Прогнози Basic + VIP\n"
                " 30 скрінів/день\n"
                " AI Тренер з персональним аналізом\n"
                " Повна статистика з емоціями\n"
                " Бенчмарк серед топ беттерів\n"
                " Калькулятор Келлі + Ліміт банку\n\n"
                " Обери план:"
            ),
            "ru": (
                "💎 *VIP подписка*\n\n"
                "Зарабатывай на ставках умнее:\n\n"
                "Что получаешь:\n"
                " 🔥 AI Прогнозы Basic + VIP\n"
                " 30 скринов/день\n"
                " AI Тренер с персональным анализом\n"
                " Полная статистика с эмоциями\n"
                " Бенчмарк среди топ беттеров\n"
                " Калькулятор Келли + Лимит банка\n\n"
                " Выбери план:"
            ),
            "en": (
                "💎 *VIP*\n\n"
                "Bet smarter, earn more:\n\n"
                "Includes:\n"
                " 🔥 Basic + VIP AI Predictions\n"
                " 30 screens/day\n"
                " AI Coach with personal analysis\n"
                " Full emotional stats\n"
                " Ranking among top bettors\n"
                " Kelly Calculator + Bank Limit\n\n"
                " Choose plan:"
            ),
        }
        await query.message.reply_text(
            promo.get(lang, promo["ua"]),
            parse_mode="Markdown",
            reply_markup=vip_subscription_keyboard(
                lang,
                show_promo=is_eligible_for_first_payment_promo(user_id),
            ),
        )
        return

    if data == "signals_buy_vip_for_basic":
        from keyboards import vip_signals_payment_keyboard

        promo = {
            "ua": (
                "💎 *VIP Прогнози  $5 / 10 днів*\n\n"
                "Окрема підписка на VIP прогнози\n"
                "без апгрейду на повний VIP план.\n\n"
                "Отримуй готові ставки від AI-агента\n"
                "і заробляй розумніше 10 днів.\n\n"
                " 399⭐ або $5\n\n"
                " Обери спосіб оплати:"
            ),
            "ru": (
                "💎 *VIP Прогнозы  $5 / 10 дней*\n\n"
                "Отдельная подписка на VIP прогнозы\n"
                "без апгрейда на полный VIP план.\n\n"
                "Получай готовые ставки от AI-агента\n"
                "и зарабатывай умнее 10 дней.\n\n"
                " 399⭐ или $5\n\n"
                " Выбери способ оплаты:"
            ),
            "en": (
                "💎 *VIP Predictions  $5 / 10 days*\n\n"
                "Separate VIP predictions subscription\n"
                "without full VIP upgrade.\n\n"
                "Get ready picks from the AI agent\n"
                "and earn smarter for 10 days.\n\n"
                " 399⭐ or $5\n\n"
                " Choose payment:"
            ),
        }
        await query.message.reply_text(
            promo.get(lang, promo["ua"]),
            parse_mode="Markdown",
            reply_markup=vip_signals_payment_keyboard(lang),
        )
