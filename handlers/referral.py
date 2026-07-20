# -*- coding: utf-8 -*-
import re

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from config import ADMIN_ID, PAYOUT_MIN_USD
from db import (
    create_payout_request,
    get_pending_payout_request,
    get_referral_dashboard,
    get_user,
)


def _normalize_lang(lang: str) -> str:
    lang = (lang or "ua").lower()
    if lang.startswith("uk") or lang.startswith("ua"):
        return "ua"
    if lang.startswith("ru"):
        return "ru"
    return "en"


def _fmt_usd(value) -> str:
    return f"{float(value or 0):.2f}"


def referral_keyboard(lang: str) -> InlineKeyboardMarkup:
    labels = {
        "ua": "💸 Подати запит на вивід коштів",
        "ru": "💸 Подать заявку на вывод",
        "en": "💸 Request payout",
    }
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(labels.get(lang, labels["en"]), callback_data="referral_payout")
    ]])


def referral_text(lang: str, link: str, data: dict) -> str:
    balance = _fmt_usd(data.get("balance"))
    total = int(data.get("total_referrals") or 0)
    paid = int(data.get("paid_referrals") or 0)
    if lang == "ru":
        return (
            f"👥 Твоя реферальная ссылка:\n{link}\n\n"
            "За каждого друга, который активирует бота и добавит 3 ставки,\n"
            "ты получишь 3 дня Basic бесплатно 🎁\n\n"
            f"💰 Твой баланс: ${balance}\n"
            f"📊 Рефералов: {total}  С подпиской: {paid}\n"
            "Заработок: 25% от трат реферала в течение 3 месяцев\n\n"
            f"Минимальная сумма вывода: ${PAYOUT_MIN_USD:g}"
        )
    if lang == "en":
        return (
            f"👥 Your referral link:\n{link}\n\n"
            "For every friend who activates the bot and adds 3 bets,\n"
            "you get 3 Basic days for free 🎁\n\n"
            f"💰 Your balance: ${balance}\n"
            f"📊 Referrals: {total}  With subscription: {paid}\n"
            "Earnings: 25% of referral spend during 3 months\n\n"
            f"Minimum payout: ${PAYOUT_MIN_USD:g}"
        )
    return (
        f"👥 Твоє реферальне посилання:\n{link}\n\n"
        "За кожного друга, який активує бота і додасть 3 ставки,\n"
        "ти отримаєш 3 дні Basic безкоштовно 🎁\n\n"
        f"💰 Твій баланс: ${balance}\n"
        f"📊 Рефералів: {total}  З підпискою: {paid}\n"
        "Заробіток: 25% від витрат реферала протягом 3 місяців\n\n"
        f"Мінімальна сума виводу: ${PAYOUT_MIN_USD:g}"
    )


def _payout_low_balance_text(lang: str, balance: float) -> str:
    if lang == "ru":
        return f"Минимальная сумма вывода - ${PAYOUT_MIN_USD:g}. Твой баланс: ${balance:.2f}."
    if lang == "en":
        return f"Minimum payout is ${PAYOUT_MIN_USD:g}. Your balance: ${balance:.2f}."
    return f"Мінімальна сума виводу - ${PAYOUT_MIN_USD:g}. Твій баланс: ${balance:.2f}."


def _wallet_prompt_text(lang: str, amount: float) -> str:
    if lang == "ru":
        return f"Введи USDT-адрес для вывода ${amount:.2f}. Укажи сеть: TRC20 или TON."
    if lang == "en":
        return f"Enter a USDT wallet for ${amount:.2f}. Include the network: TRC20 or TON."
    return f"Введи USDT-адресу для виводу ${amount:.2f}. Вкажи мережу: TRC20 або TON."


def _invalid_wallet_text(lang: str) -> str:
    if lang == "ru":
        return "Введи корректный USDT-адрес и сеть: TRC20 или TON."
    if lang == "en":
        return "Enter a valid USDT wallet and network: TRC20 or TON."
    return "Введи коректну USDT-адресу і мережу: TRC20 або TON."


def _valid_wallet(text: str) -> bool:
    value = (text or "").strip()
    upper = value.upper()
    has_network = "TRC20" in upper or "TON" in upper
    trc20 = re.search(r"\bT[1-9A-HJ-NP-Za-km-z]{33}\b", value)
    ton = re.search(r"\b(?:EQ|UQ)[A-Za-z0-9_-]{46,}\b", value)
    return bool(has_network and (trc20 or ton))


async def show_referrals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = get_user(user_id) or {}
    lang = _normalize_lang(user.get("lang"))
    bot_username = context.bot.username or "bet_tracker_stats_bot"
    link = f"https://t.me/{bot_username}?start=ref_{user_id}"
    data = get_referral_dashboard(user_id)

    await update.effective_message.reply_text(
        referral_text(lang, link, data),
        reply_markup=referral_keyboard(lang),
    )


async def referral_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    user = get_user(user_id) or {}
    lang = _normalize_lang(user.get("lang"))
    data = get_referral_dashboard(user_id)
    balance = float(data.get("balance") or 0)

    if query.data != "referral_payout":
        return

    pending = get_pending_payout_request(user_id)
    if pending:
        await query.message.reply_text(
            {
                "ua": "У тебе вже є pending-запит на вивід. Дочекайся обробки.",
                "ru": "У тебя уже есть pending-заявка на вывод. Дождись обработки.",
                "en": "You already have a pending payout request. Wait until it is processed.",
            }.get(lang, "You already have a pending payout request. Wait until it is processed.")
        )
        return

    if balance < PAYOUT_MIN_USD:
        await query.message.reply_text(_payout_low_balance_text(lang, balance))
        return

    context.user_data["awaiting_referral_payout_wallet"] = True
    context.user_data["referral_payout_amount"] = balance
    await query.message.reply_text(_wallet_prompt_text(lang, balance))


async def handle_payout_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    user_id = update.effective_user.id
    user = get_user(user_id) or {}
    lang = _normalize_lang(user.get("lang"))
    wallet = update.message.text.strip()

    if not _valid_wallet(wallet):
        await update.message.reply_text(_invalid_wallet_text(lang))
        return

    pending = get_pending_payout_request(user_id)
    if pending:
        context.user_data.pop("awaiting_referral_payout_wallet", None)
        context.user_data.pop("referral_payout_amount", None)
        await update.message.reply_text(
            {
                "ua": "У тебе вже є pending-запит на вивід.",
                "ru": "У тебя уже есть pending-заявка на вывод.",
                "en": "You already have a pending payout request.",
            }.get(lang, "You already have a pending payout request.")
        )
        return

    data = get_referral_dashboard(user_id)
    amount = float(data.get("balance") or 0)
    if amount < PAYOUT_MIN_USD:
        context.user_data.pop("awaiting_referral_payout_wallet", None)
        context.user_data.pop("referral_payout_amount", None)
        await update.message.reply_text(_payout_low_balance_text(lang, amount))
        return

    payout_id = create_payout_request(user_id, amount, wallet)
    context.user_data.pop("awaiting_referral_payout_wallet", None)
    context.user_data.pop("referral_payout_amount", None)

    if not payout_id:
        await update.message.reply_text(_payout_low_balance_text(lang, 0))
        return

    if lang == "ru":
        text = f"✅ Заявка на вывод ${amount:.2f} создана. Обработка до 3 рабочих дней."
    elif lang == "en":
        text = f"✅ Payout request for ${amount:.2f} created. Processing takes up to 3 business days."
    else:
        text = f"✅ Запит на вивід ${amount:.2f} створено. Обробка до 3 робочих днів."
    await update.message.reply_text(text)

    if ADMIN_ID:
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=(
                "💸 Новий referral payout\n"
                f"ID: {payout_id}\n"
                f"User: {user_id}\n"
                f"Amount: ${amount:.2f}\n"
                f"Wallet: {wallet}"
            ),
        )
