# -*- coding: utf-8 -*-
from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from db import (
    get_user,
    get_subscription_type,
    subscribe_to_signal,
    is_subscribed_to_signal,
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
            " *AI Сигналы дня*\n\n"
            "Получай готовые ставки от наших AI-аналитиков "
            "прямо в Telegram. Выбери уровень сигналов:\n"
        )
    elif lang == "en":
        title = (
            " *AI Signals of the day*\n\n"
            "Get ready-to-bet picks from our AI analysts "
            "straight to Telegram. Choose your level:\n"
        )
    else:
        title = (
            " *AI Сигнали дня*\n\n"
            "Отримуй готові ставки від наших AI-аналітиків "
            "прямо в Telegram. Обери рівень сигналів:\n"
        )

    vip_signals_active = _get_vip_signals_active(user_id)

    if sub_type == "trial":
        labels = {
            "ua": [
                " Trial Сигнали (активні)",
                " Basic Сигнали  купити підписку",
                " VIP Сигнали  купити підписку",
            ],
            "ru": [
                " Trial Сигналы (активны)",
                " Basic Сигналы  купить подписку",
                " VIP Сигналы  купить подписку",
            ],
            "en": [
                " Trial Signals (active)",
                " Basic Signals  buy subscription",
                " VIP Signals  buy subscription",
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
            "ua": " VIP Сигнали (активні)",
            "ru": " VIP Сигналы (активны)",
            "en": " VIP Signals (active)",
        }
        vip_label_buy = {
            "ua": " VIP Сигнали  $5 / 10 днів",
            "ru": " VIP Сигналы  $5 / 10 дней",
            "en": " VIP Signals  $5 / 10 days",
        }
        basic_label = {
            "ua": " Basic Сигнали (активні)",
            "ru": " Basic Сигналы (активны)",
            "en": " Basic Signals (active)",
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
            "ua": [" Basic Сигнали (активні)", " VIP Сигнали (активні)"],
            "ru": [" Basic Сигналы (активны)", " VIP Сигналы (активны)"],
            "en": [" Basic Signals (active)", " VIP Signals (active)"],
        }
        label = labels.get(lang, labels["ua"])
        buttons = [
            [InlineKeyboardButton(label[0], callback_data="signals_basic_info")],
            [InlineKeyboardButton(label[1], callback_data="signals_vip_info")],
        ]
    else:
        no_access = {
            "ua": "Для AI Сигналів потрібна активна підписка.",
            "ru": "Для AI Сигналов нужна активная подписка.",
            "en": "Active subscription required for AI Signals.",
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
            "ua": " Підписка активна. Очікуй сигнали від адміна  вони приходитимуть автоматично коли є цінні події.",
            "ru": " Подписка активна. Ожидай сигналы от админа  они будут приходить автоматически когда есть ценные события.",
            "en": " Subscription active. Wait for admin signals  they will arrive automatically when valuable events appear.",
        }
        await query.message.reply_text(info.get(lang, info["ua"]))
        return

    if data == "signals_buy_basic":
        from keyboards import access_keyboard

        promo = {
            "ua": (
                " *Basic підписка  $5/міс*\n\n"
                "Що отримуєш:\n"
                " 15 скрінів/день\n"
                " Повна статистика з інсайтами\n"
                " AI Сигнали Basic щодня\n"
                " Калькулятор Келлі\n"
                " Ліміт банку\n\n"
                " Обери спосіб оплати:"
            ),
            "ru": (
                " *Basic подписка  $5/мес*\n\n"
                "Что получаешь:\n"
                " 15 скринов/день\n"
                " Полная статистика с инсайтами\n"
                " AI Сигналы Basic каждый день\n"
                " Калькулятор Келли\n"
                " Лимит банка\n\n"
                " Выбери способ оплаты:"
            ),
            "en": (
                " *Basic  $5/mo*\n\n"
                "Includes:\n"
                " 15 screens/day\n"
                " Full stats with insights\n"
                " Basic AI Signals daily\n"
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
                " *VIP підписка*\n\n"
                "Що отримуєш:\n"
                " 30 скрінів/день\n"
                " AI Тренер з персональним аналізом\n"
                " Повна статистика з емоціями\n"
                " Бенчмарк серед топ беттерів\n"
                " AI Сигнали Basic + VIP\n"
                " Калькулятор Келлі + Ліміт банку\n\n"
                " Обери план:"
            ),
            "ru": (
                " *VIP подписка*\n\n"
                "Что получаешь:\n"
                " 30 скринов/день\n"
                " AI Тренер с персональным анализом\n"
                " Полная статистика с эмоциями\n"
                " Бенчмарк среди топ беттеров\n"
                " AI Сигналы Basic + VIP\n"
                " Калькулятор Келли + Лимит банка\n\n"
                " Выбери план:"
            ),
            "en": (
                " *VIP*\n\n"
                "Includes:\n"
                " 30 screens/day\n"
                " AI Coach with personal analysis\n"
                " Full emotional stats\n"
                " Ranking among top bettors\n"
                " Basic + VIP AI Signals\n"
                " Kelly Calculator + Bank Limit\n\n"
                " Choose plan:"
            ),
        }
        await query.message.reply_text(
            promo.get(lang, promo["ua"]),
            parse_mode="Markdown",
            reply_markup=vip_subscription_keyboard(lang),
        )
        return

    if data == "signals_buy_vip_for_basic":
        from keyboards import vip_signals_payment_keyboard

        promo = {
            "ua": (
                " *VIP Сигнали  $5 / 10 днів*\n\n"
                "Окрема підписка на VIP сигнали\n"
                "без апгрейду на повний VIP план.\n\n"
                "Отримуй найточніші сигнали від\n"
                "наших аналітиків 10 днів.\n\n"
                " 399⭐ або $5\n\n"
                " Обери спосіб оплати:"
            ),
            "ru": (
                " *VIP Сигналы  $5 / 10 дней*\n\n"
                "Отдельная подписка на VIP сигналы\n"
                "без апгрейда на полный VIP план.\n\n"
                "Получай самые точные сигналы от\n"
                "наших аналитиков 10 дней.\n\n"
                " 399⭐ или $5\n\n"
                " Выбери способ оплаты:"
            ),
            "en": (
                " *VIP Signals  $5 / 10 days*\n\n"
                "Separate VIP signals subscription\n"
                "without full VIP upgrade.\n\n"
                "Get most accurate signals from\n"
                "our analysts for 10 days.\n\n"
                " 399⭐ or $5\n\n"
                " Choose payment:"
            ),
        }
        await query.message.reply_text(
            promo.get(lang, promo["ua"]),
            parse_mode="Markdown",
            reply_markup=vip_signals_payment_keyboard(lang),
        )
