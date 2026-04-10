from telegram import Update
from telegram.ext import ContextTypes

from db import (
    get_user,
    user_has_access,
    subscribe_bet_day_basic,
    subscribe_bet_day_vip,
    is_subscribed_bet_day_basic,
    is_subscribed_bet_day_vip,
    has_vip_bet_day_access,
)
from keyboards import bet_day_menu_keyboard, bet_day_basic_keyboard, bet_day_vip_keyboard, access_keyboard
from services.tools_service import get_tools_menu


def _normalize_lang(lang: str) -> str:
    lang = (lang or "en").lower()
    if lang.startswith("uk") or lang.startswith("ua"):
        return "ua"
    if lang.startswith("ru"):
        return "ru"
    return "en"


async def open_tools_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = get_user(user_id) or {}
    lang = _normalize_lang(user.get("lang", "en"))
    has_access = user_has_access(user_id)

    text, keyboard = get_tools_menu(lang, has_access)
    await update.message.reply_text(text, reply_markup=keyboard)


async def tools_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    user = get_user(user_id) or {}
    lang = _normalize_lang(user.get("lang", "en"))
    has_access = user_has_access(user_id)
    plan = (user.get("plan") or "").lower()

    if query.data == "tools_back":
        text, keyboard = get_tools_menu(lang, has_access)
        await query.message.reply_text(text, reply_markup=keyboard)
        return

    if query.data == "tool_bet_day":
        text = {
            "ua": "🎯 Ставка дня\n\nОбери формат доступу:",
            "ru": "🎯 Ставка дня\n\nВыбери формат доступа:",
            "en": "🎯 Bet of the day\n\nChoose the access format:",
        }[lang]
        await query.message.reply_text(text, reply_markup=bet_day_menu_keyboard(lang))
        return

    if query.data == "betday_basic":
        if not has_access:
            text = {
                "ua": "🔒 Базова ставка дня доступна тільки після активації підписки.\n\n👇 Обери тариф:",
                "ru": "🔒 Базовая ставка дня доступна только после активации подписки.\n\n👇 Выбери тариф:",
                "en": "🔒 Basic bet of the day is available only after activating a subscription.\n\n👇 Choose a plan:",
            }[lang]
            await query.message.reply_text(text, reply_markup=access_keyboard(lang))
            return

        subscribed = is_subscribed_bet_day_basic(user_id)
        text = {
            "ua": "🎯 Ставка дня (Basic)\n\nЦей потік входить у базову підписку.\nНатисни «Підписатися», щоб почати отримувати базові ставки дня в боті.",
            "ru": "🎯 Ставка дня (Basic)\n\nЭтот поток входит в базовую подписку.\nНажми «Подписаться», чтобы начать получать базовые ставки дня в боте.",
            "en": "🎯 Bet of the day (Basic)\n\nThis stream is included in the basic subscription.\nPress “Subscribe” to start receiving basic daily bets in the bot.",
        }[lang]
        if subscribed:
            extra = {
                "ua": "\n\n✅ Ти вже підписаний на базову ставку дня.",
                "ru": "\n\n✅ Ты уже подписан на базовую ставку дня.",
                "en": "\n\n✅ You are already subscribed to the basic bet of the day.",
            }[lang]
            text += extra

        await query.message.reply_text(text, reply_markup=bet_day_basic_keyboard(lang, is_subscribed=subscribed))
        return

    if query.data == "betday_vip":
        vip_bet_day_access = has_vip_bet_day_access(user_id)
        subscribed = is_subscribed_bet_day_vip(user_id)

        if plan == "vip":
            text = {
                "ua": "🔥 Ставка дня (VIP)\n\nVIP ставка дня вже входить у твою VIP підписку.\nНатисни «Підписатися», щоб почати отримувати VIP ставки в боті.",
                "ru": "🔥 Ставка дня (VIP)\n\nVIP ставка дня уже входит в твою VIP подписку.\nНажми «Подписаться», чтобы начать получать VIP ставки в боте.",
                "en": "🔥 Bet of the day (VIP)\n\nVIP bet of the day is already included in your VIP plan.\nPress “Subscribe” to start receiving VIP bets in the bot.",
            }[lang]
            if subscribed:
                extra = {
                    "ua": "\n\n✅ Ти вже підписаний на VIP ставку дня.",
                    "ru": "\n\n✅ Ты уже подписан на VIP ставку дня.",
                    "en": "\n\n✅ You are already subscribed to the VIP bet of the day.",
                }[lang]
                text += extra
            await query.message.reply_text(text, reply_markup=bet_day_vip_keyboard(lang, has_access=True, is_subscribed=subscribed))
            return

        if vip_bet_day_access:
            text = {
                "ua": "🔥 Ставка дня (VIP)\n\nУ тебе вже активний окремий VIP доступ до ставки дня.\nНатисни «Підписатися», щоб почати отримувати VIP ставки в боті.",
                "ru": "🔥 Ставка дня (VIP)\n\nУ тебя уже активен отдельный VIP доступ к ставке дня.\nНажми «Подписаться», чтобы начать получать VIP ставки в боте.",
                "en": "🔥 Bet of the day (VIP)\n\nYou already have separate VIP access to the bet of the day.\nPress “Subscribe” to start receiving VIP bets in the bot.",
            }[lang]
            if subscribed:
                extra = {
                    "ua": "\n\n✅ Ти вже підписаний на VIP ставку дня.",
                    "ru": "\n\n✅ Ты уже подписан на VIP ставку дня.",
                    "en": "\n\n✅ You are already subscribed to the VIP bet of the day.",
                }[lang]
                text += extra
            await query.message.reply_text(text, reply_markup=bet_day_vip_keyboard(lang, has_access=True, is_subscribed=subscribed))
            return

        text = {
            "ua": "🔥 Ставка дня (VIP)\n\nVIP ставка дня входить у повний VIP, а також доступна окремо на 30 днів.\n\n💰 Ціна: 4.99$ або 499⭐\n\n👇 Обери спосіб активації:",
            "ru": "🔥 Ставка дня (VIP)\n\nVIP ставка дня входит в полный VIP, а также доступна отдельно на 30 дней.\n\n💰 Цена: 4.99$ или 499⭐\n\n👇 Выбери способ активации:",
            "en": "🔥 Bet of the day (VIP)\n\nVIP bet of the day is included in the full VIP plan and is also available separately for 30 days.\n\n💰 Price: $4.99 or 499⭐\n\n👇 Choose an activation method:",
        }[lang]
        await query.message.reply_text(text, reply_markup=bet_day_vip_keyboard(lang, has_access=False, is_subscribed=False))
        return

    if query.data == "betday_basic_subscribe":
        if not has_access:
            text = {
                "ua": "🔒 Спочатку активуй підписку.",
                "ru": "🔒 Сначала активируй подписку.",
                "en": "🔒 Activate a subscription first.",
            }[lang]
            await query.message.reply_text(text, reply_markup=access_keyboard(lang))
            return

        subscribe_bet_day_basic(user_id)
        text = {
            "ua": "✅ Ти підписаний на базову ставку дня. Відтепер ти отримуватимеш базові ставки в боті.",
            "ru": "✅ Ты подписан на базовую ставку дня. Теперь ты будешь получать базовые ставки в боте.",
            "en": "✅ You are subscribed to the basic bet of the day. From now on, you will receive basic bets in the bot.",
        }[lang]
        await query.message.reply_text(text, reply_markup=bet_day_basic_keyboard(lang, is_subscribed=True))
        return

    if query.data == "betday_vip_subscribe":
        if not (plan == "vip" or has_vip_bet_day_access(user_id)):
            text = {
                "ua": "🔒 Спочатку активуй VIP ставку дня.",
                "ru": "🔒 Сначала активируй VIP ставку дня.",
                "en": "🔒 Activate VIP bet of the day first.",
            }[lang]
            await query.message.reply_text(text)
            return

        subscribe_bet_day_vip(user_id)
        text = {
            "ua": "✅ Ти підписаний на VIP ставку дня. Відтепер ти отримуватимеш VIP ставки в боті.",
            "ru": "✅ Ты подписан на VIP ставку дня. Теперь ты будешь получать VIP ставки в боте.",
            "en": "✅ You are subscribed to the VIP bet of the day. From now on, you will receive VIP bets in the bot.",
        }[lang]
        await query.message.reply_text(text, reply_markup=bet_day_vip_keyboard(lang, has_access=True, is_subscribed=True))
        return

    if query.data == "tool_live":
        text = {
            "ua": "⚡ Live\n\nРозділ live сигналів підключимо наступним етапом.",
            "ru": "⚡ Live\n\nРаздел live сигналов подключим следующим этапом.",
            "en": "⚡ Live\n\nThe live signals section will be connected in the next step.",
        }[lang]
        await query.message.reply_text(text)
        return

    if query.data == "tool_ai":
        text = {
            "ua": "🤖 AI-аналіз\n\nAI-аналіз підключимо наступним етапом.",
            "ru": "🤖 AI-анализ\n\nAI-анализ подключим следующим этапом.",
            "en": "🤖 AI analysis\n\nAI analysis will be connected in the next step.",
        }[lang]
        await query.message.reply_text(text)
        return

    if query.data == "tool_challenge":
        text = {
            "ua": "🚀 Челендж\n\nЧелендж підключимо наступним етапом.",
            "ru": "🚀 Челлендж\n\nЧеллендж подключим следующим этапом.",
            "en": "🚀 Challenge\n\nThe challenge will be connected in the next step.",
        }[lang]
        await query.message.reply_text(text)
        return
