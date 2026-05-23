# -*- coding: utf-8 -*-
from telegram import Update
from telegram.ext import ContextTypes

from db import (
    get_user,
    user_has_access,
    is_trial_available,
    get_user_daily_limit,
    count_user_photos_today,
    subscribe_bet_day_basic,
    subscribe_bet_day_vip,
    is_subscribed_bet_day_basic,
    is_subscribed_bet_day_vip,
    has_vip_bet_day_access,
    subscribe_to_signal,
    is_subscribed_to_signal,
    has_vip_signals_access,
)
from keyboards import (
    ai_signals_keyboard,
    bet_day_menu_keyboard,
    bet_day_basic_keyboard,
    bet_day_vip_keyboard,
    access_keyboard,
)
from services.tools_service import get_tools_menu
from services.match_analysis_service import analyze_match_screenshot, analyze_match_text
from languages import get_text


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


async def open_ai_signals_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = get_user(user_id) or {}
    lang = _normalize_lang(user.get("lang", "en"))
    vip_access = has_vip_signals_access(user_id)

    texts = {
        "ua": (
            " AI Сигнали дня\n\n"
            "Обери потік сигналів:\n"
            "Trial - безкоштовні сигнали для пробного доступу\n"
            "Basic - сигнали для активної підписки\n"
            "VIP - преміум сигнали для VIP або окремої підписки"
        ),
        "ru": (
            " AI Сигналы дня\n\n"
            "Выбери поток сигналов:\n"
            "Trial - бесплатные сигналы для пробного доступа\n"
            "Basic - сигналы для активной подписки\n"
            "VIP - премиум сигналы для VIP или отдельной подписки"
        ),
        "en": (
            " AI Signals\n\n"
            "Choose a signal stream:\n"
            "Trial - free signals for trial access\n"
            "Basic - signals for active subscribers\n"
            "VIP - premium signals for VIP or separate subscription"
        ),
    }
    await update.message.reply_text(
        texts.get(lang, texts["en"]),
        reply_markup=ai_signals_keyboard(lang, vip_access=vip_access),
    )


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

    if query.data in ("tool_ai_signals", "signal_back"):
        texts = {
            "ua": " AI Сигнали дня\n\nОбери тип сигналів:",
            "ru": " AI Сигналы дня\n\nВыбери тип сигналов:",
            "en": " AI Signals\n\nChoose signal type:",
        }
        await query.message.reply_text(
            texts.get(lang, texts["en"]),
            reply_markup=ai_signals_keyboard(lang, vip_access=has_vip_signals_access(user_id)),
        )
        return

    if query.data in ("signal_trial", "signal_basic", "signal_vip"):
        signal_type = query.data.replace("signal_", "")

        if signal_type == "basic" and not has_access:
            no_access = {
                "ua": " Basic сигнали доступні після активації підписки.",
                "ru": " Basic сигналы доступны после активации подписки.",
                "en": " Basic signals are available after activating a subscription.",
            }
            await query.message.reply_text(no_access.get(lang, no_access["en"]), reply_markup=access_keyboard(lang))
            return

        if signal_type == "vip" and not has_vip_signals_access(user_id):
            no_vip = {
                "ua": " VIP сигнали доступні у повному VIP або окремо на 10 днів за 399⭐.",
                "ru": " VIP сигналы доступны в полном VIP или отдельно на 10 дней за 399⭐.",
                "en": " VIP signals are included in VIP or available separately for 10 days at 399⭐.",
            }
            await query.message.reply_text(
                no_vip.get(lang, no_vip["en"]),
                reply_markup=ai_signals_keyboard(lang, vip_access=False),
            )
            return

        if is_subscribed_to_signal(user_id, signal_type):
            already = {
                "ua": f" Ти вже підписаний на {signal_type.upper()} сигнали.",
                "ru": f" Ты уже подписан на {signal_type.upper()} сигналы.",
                "en": f" You are already subscribed to {signal_type.upper()} signals.",
            }
            await query.message.reply_text(already.get(lang, already["en"]))
            return

        duration_days = None
        if signal_type == "vip":
            from datetime import datetime

            expires_raw = user.get("vip_signals_expires_at")
            if plan == "vip":
                expires_raw = user.get("access_until") or expires_raw
            if expires_raw:
                try:
                    seconds_left = (datetime.fromisoformat(expires_raw) - datetime.now()).total_seconds()
                    duration_days = max(1, int(seconds_left // 86400) + 1)
                except Exception:
                    duration_days = 10

        subscribe_to_signal(user_id, signal_type, duration_days=duration_days)
        success = {
            "ua": f" Підписку на {signal_type.upper()} сигнали активовано.",
            "ru": f" Подписка на {signal_type.upper()} сигналы активирована.",
            "en": f" {signal_type.upper()} signals subscription activated.",
        }
        await query.message.reply_text(success.get(lang, success["en"]))
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

    if query.data == "tool_kelly":
        if not has_access:
            no_access = {
                "ua": "🔒 Калькулятор Келлі доступний після активації підписки.\n\n👇 Обери тариф:",
                "ru": "🔒 Калькулятор Келли доступен после активации подписки.\n\n👇 Выбери тариф:",
                "en": "🔒 Kelly Calculator is available after subscription.\n\n👇 Choose a plan:",
            }
            await query.message.reply_text(
                no_access.get(lang, no_access["en"]),
                reply_markup=access_keyboard(lang),
            )
            return

        context.user_data["awaiting_kelly_input"] = True
        prompts = {
            "ua": (
                "🧮 *Калькулятор Келлі*\n\n"
                "Допомагає визначити оптимальний розмір ставки\n"
                "щоб захистити банк від злива.\n\n"
                "Надішли 3 числа через пробіл:\n"
                "`<банк> <коефіцієнт> <твоя_ймовірність_у_%>`\n\n"
                "Приклад: 1000 2.10 55\n"
                "(банк 1000, коеф 2.10, шанс 55%)"
            ),
            "ru": (
                "🧮 *Калькулятор Келли*\n\n"
                "Помогает определить оптимальный размер ставки\n"
                "чтобы защитить банк от слива.\n\n"
                "Отправь 3 числа через пробел:\n"
                "`<банк> <коэффициент> <твоя_вероятность_в_%>`\n\n"
                "Пример: 1000 2.10 55\n"
                "(банк 1000, коэф 2.10, шанс 55%)"
            ),
            "en": (
                "🧮 *Kelly Calculator*\n\n"
                "Helps determine optimal bet size\n"
                "to protect bankroll from drain.\n\n"
                "Send 3 numbers separated by space:\n"
                "`<bank> <odds> <your_probability_in_%>`\n\n"
                "Example: 1000 2.10 55\n"
                "(bank 1000, odds 2.10, chance 55%)"
            ),
        }
        await query.message.reply_text(
            prompts.get(lang, prompts["en"]),
            parse_mode="Markdown",
        )
        return

    if query.data == "tool_ai":
        if not has_access:
            await query.message.reply_text(get_text(lang, "ai_analysis_no_access"), reply_markup=access_keyboard(lang))
            return

        context.user_data["awaiting_ai_match_analysis"] = True
        await query.message.reply_text(get_text(lang, "ai_analysis_send_prompt"))
        return

    if query.data == "tool_bank_limit":
        if not has_access:
            no_access = {
                "ua": "🔒 Налаштування ліміту банку доступне після підписки.\n\n👇 Обери тариф:",
                "ru": "🔒 Настройка лимита банка доступна после подписки.\n\n👇 Выбери тариф:",
                "en": "🔒 Bank limit setup is available after subscription.\n\n👇 Choose a plan:",
            }
            await query.message.reply_text(
                no_access.get(lang, no_access["en"]),
                reply_markup=access_keyboard(lang),
            )
            return

        context.user_data["awaiting_bank_limit"] = True
        prompts = {
            "ua": (
                "📊 *Ліміт банку*\n\n"
                "Встанови денний ліміт ставок щоб не\n"
                "зливати банк за один тілт.\n\n"
                "Надішли число  максимум на день у твоїй валюті.\n"
                "Приклад: 500\n\n"
                "Бот попередить коли ти близький до ліміту\n"
                "і заблокує нові скріни при перевищенні."
            ),
            "ru": (
                "📊 *Лимит банка*\n\n"
                "Установи дневной лимит ставок чтобы не\n"
                "сливать банк за один тилт.\n\n"
                "Отправь число  максимум на день в твоей валюте.\n"
                "Пример: 500\n\n"
                "Бот предупредит когда близко к лимиту\n"
                "и заблокирует новые скрины при превышении."
            ),
            "en": (
                "📊 *Bank limit*\n\n"
                "Set daily betting limit to avoid\n"
                "draining bankroll on tilt.\n\n"
                "Send a number  max amount per day.\n"
                "Example: 500\n\n"
                "Bot will warn when you're near limit\n"
                "and block new screens after exceeding."
            ),
        }
        await query.message.reply_text(
            prompts.get(lang, prompts["en"]),
            parse_mode="Markdown",
        )
        return


async def handle_kelly_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробляє ввід для калькулятора Келлі"""
    if not context.user_data.get("awaiting_kelly_input"):
        return

    user_id = update.effective_user.id
    user = get_user(user_id) or {}
    lang = _normalize_lang(user.get("lang", "en"))

    text = (update.message.text or "").strip()
    parts = text.split()

    error_text = {
        "ua": " Неправильний формат.\nПриклад: 1000 2.10 55",
        "ru": " Неправильный формат.\nПример: 1000 2.10 55",
        "en": " Wrong format.\nExample: 1000 2.10 55",
    }

    if len(parts) != 3:
        await update.message.reply_text(
            error_text.get(lang, error_text["en"]),
            parse_mode="Markdown",
        )
        return

    try:
        bank = float(parts[0])
        odds = float(parts[1])
        probability = float(parts[2])

        if bank <= 0 or odds <= 1 or probability <= 0 or probability >= 100:
            raise ValueError()

    except (ValueError, IndexError):
        await update.message.reply_text(
            error_text.get(lang, error_text["en"]),
            parse_mode="Markdown",
        )
        return

    p = probability / 100
    q = 1 - p
    b = odds - 1
    kelly_fraction = (b * p - q) / b

    context.user_data["awaiting_kelly_input"] = False

    if kelly_fraction <= 0:
        no_value = {
            "ua": (
                f" *Не роби цю ставку!*\n\n"
                f"При коеф {odds} і шансі {probability}%\n"
                f"математичне очікування негативне.\n\n"
                f"Букмекер пропонує тобі гірші умови\n"
                f"ніж реальний шанс перемоги."
            ),
            "ru": (
                f" *Не делай эту ставку!*\n\n"
                f"При коэф {odds} и шансе {probability}%\n"
                f"математическое ожидание отрицательное.\n\n"
                f"Букмекер предлагает тебе худшие условия\n"
                f"чем реальный шанс победы."
            ),
            "en": (
                f" *Don't make this bet!*\n\n"
                f"At odds {odds} and chance {probability}%\n"
                f"expected value is negative.\n\n"
                f"Bookmaker offers worse conditions\n"
                f"than your real winning chance."
            ),
        }
        await update.message.reply_text(
            no_value.get(lang, no_value["en"]),
            parse_mode="Markdown",
        )
        return

    full_kelly = bank * kelly_fraction
    half_kelly = full_kelly / 2
    quarter_kelly = full_kelly / 4

    result = {
        "ua": (
            f"🧮 *Калькулятор Келлі*\n\n"
            f"Банк: {bank:.0f}\n"
            f"Коеф: {odds}\n"
            f"Твій шанс: {probability}%\n\n"
            f"📊 Рекомендовані ставки:\n\n"
            f"🟢 *Безпечно (Quarter):* {quarter_kelly:.0f}\n"
            f"🟡 *Помірно (Half):* {half_kelly:.0f}\n"
            f"🔴 *Агресивно (Full):* {full_kelly:.0f}\n\n"
            f"💡 Більшість профі використовують\n"
            f"Quarter або Half Kelly щоб мінімізувати\n"
            f"волатильність банку."
        ),
        "ru": (
            f"🧮 *Калькулятор Келли*\n\n"
            f"Банк: {bank:.0f}\n"
            f"Коэф: {odds}\n"
            f"Твой шанс: {probability}%\n\n"
            f"📊 Рекомендуемые ставки:\n\n"
            f"🟢 *Безопасно (Quarter):* {quarter_kelly:.0f}\n"
            f"🟡 *Умеренно (Half):* {half_kelly:.0f}\n"
            f"🔴 *Агрессивно (Full):* {full_kelly:.0f}\n\n"
            f"💡 Большинство профи используют\n"
            f"Quarter или Half Kelly чтобы минимизировать\n"
            f"волатильность банка."
        ),
        "en": (
            f"🧮 *Kelly Calculator*\n\n"
            f"Bank: {bank:.0f}\n"
            f"Odds: {odds}\n"
            f"Your chance: {probability}%\n\n"
            f"📊 Recommended bet sizes:\n\n"
            f"🟢 *Safe (Quarter):* {quarter_kelly:.0f}\n"
            f"🟡 *Moderate (Half):* {half_kelly:.0f}\n"
            f"🔴 *Aggressive (Full):* {full_kelly:.0f}\n\n"
            f"💡 Most pros use Quarter or Half Kelly\n"
            f"to minimize bankroll volatility."
        ),
    }
    await update.message.reply_text(
        result.get(lang, result["en"]),
        parse_mode="Markdown",
    )


async def handle_bank_limit_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробляє ввід для встановлення ліміту банку"""
    if not context.user_data.get("awaiting_bank_limit"):
        return

    user_id = update.effective_user.id
    user = get_user(user_id) or {}
    lang = _normalize_lang(user.get("lang", "en"))

    text = (update.message.text or "").strip()

    try:
        limit = float(text.replace(",", "."))
        if limit < 0:
            raise ValueError()
    except ValueError:
        error = {
            "ua": " Введи число. Приклад: 500",
            "ru": " Введи число. Пример: 500",
            "en": " Enter a number. Example: 500",
        }
        await update.message.reply_text(
            error.get(lang, error["en"]),
            parse_mode="Markdown",
        )
        return

    from db import set_user_bank_limit
    set_user_bank_limit(user_id, limit)
    context.user_data["awaiting_bank_limit"] = False

    if limit == 0:
        confirm = {
            "ua": " Ліміт скасовано. Бот не буде блокувати ставки.",
            "ru": " Лимит отменён. Бот не будет блокировать ставки.",
            "en": " Limit cancelled. Bot won't block bets.",
        }
    else:
        confirm = {
            "ua": (
                f" Денний ліміт встановлено: *{limit:.0f}*\n\n"
                f"Бот попередить коли ти витратиш 70% ліміту\n"
                f"і заблокує нові скріни при перевищенні."
            ),
            "ru": (
                f" Дневной лимит установлен: *{limit:.0f}*\n\n"
                f"Бот предупредит когда ты потратишь 70% лимита\n"
                f"и заблокирует новые скрины при превышении."
            ),
            "en": (
                f" Daily limit set: *{limit:.0f}*\n\n"
                f"Bot will warn when you spend 70% of limit\n"
                f"and block new screens after exceeding."
            ),
        }

    await update.message.reply_text(
        confirm.get(lang, confirm["en"]),
        parse_mode="Markdown",
    )


async def handle_ai_analysis_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = get_user(user_id) or {}
    lang = _normalize_lang(user.get("lang", "en"))

    if not context.user_data.get("awaiting_ai_match_analysis"):
        return

    await_target = update.message
    if not await_target:
        return

    processing_text = get_text(lang, "ai_analysis_processing")
    await await_target.reply_text(processing_text)

    result = None
    try:
        if update.message.photo:
            photo = update.message.photo[-1]
            tg_file = await photo.get_file()
            image_bytes = bytes(await tg_file.download_as_bytearray())
            result = analyze_match_screenshot(image_bytes, lang=lang)
        elif update.message.text:
            result = analyze_match_text(update.message.text, lang=lang)
        else:
            result = {"ok": False, "error": "Unsupported input"}
    finally:
        context.user_data.pop("awaiting_ai_match_analysis", None)

    if not result or not result.get("ok"):
        error = (result or {}).get("error", "Unknown error")
        await await_target.reply_text(get_text(lang, "ai_analysis_failed").format(error=error))
        return

    await await_target.reply_text(result["report_text"])

    has_access = user_has_access(user_id)
    user = get_user(user_id)
    trial_started = user.get("trial_started_at") if user else None
    in_trial = (
        not has_access
        and trial_started is not None
        and is_trial_available(user_id)
    )

    if in_trial:
        used_today = count_user_photos_today(user_id)
        daily_limit = get_user_daily_limit(user_id)

        if used_today >= daily_limit:
            limit_texts = {
                "ua": (
                    "🚫 Денний ліміт вичерпано (5/5)\n\n"
                    "Щоб продовжити аналіз сьогодні:\n\n"
                    "🔹 Basic  $7/міс  15 скрінів/день\n"
                    " VIP  $19.99/міс  30 скрінів/день\n\n"
                    "👇 Оформи підписку і аналізуй без обмежень"
                ),
                "ru": (
                    "🚫 Дневной лимит исчерпан (5/5)\n\n"
                    "Чтобы продолжить анализ сегодня:\n\n"
                    "🔹 Basic  $7/мес  15 скринов/день\n"
                    " VIP  $19.99/мес  30 скринов/день\n\n"
                    "👇 Оформи подписку и анализируй без ограничений"
                ),
                "en": (
                    "🚫 Daily limit reached (5/5)\n\n"
                    "To continue analysis today:\n\n"
                    "🔹 Basic  $7/mo  15 screenshots/day\n"
                    " VIP  $19.99/mo  30 screenshots/day\n\n"
                    "👇 Subscribe and analyze without limits"
                ),
            }
            await await_target.reply_text(
                limit_texts.get(lang, limit_texts["en"]),
                reply_markup=access_keyboard(lang)
            )
            return

    await await_target.reply_text(
        get_text(lang, "ai_analysis_done_hint")
    )
