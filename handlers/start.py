# -*- coding: utf-8 -*-
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from keyboards import main_menu_keyboard, welcome_offer_keyboard, access_keyboard
from db import (
    create_user_if_not_exists,
    get_user,
    is_onboarding_completed,
    user_has_access,
    is_trial_available,
    get_trial_remaining,
    start_trial_mode,
    has_used_promo_offer,
)
from handlers.onboarding import start_onboarding


def _normalize_lang(lang: str) -> str:
    lang = (lang or "en").lower()
    if lang.startswith("uk") or lang.startswith("ua"):
        return "ua"
    if lang.startswith("ru"):
        return "ru"
    return "en"


def _welcome_text(lang: str, promo_available: bool) -> str:
    lang = _normalize_lang(lang)

    if lang == "ua":
        return (
            "😤 Зливаєш гроші на ставках?\n\n"
            "Bet Tracker Bot аналізує твої ставки і показує:\n"
            " Де ти зливаєш найбільше\n"
            " Коли ставиш на емоціях\n"
            " Твій реальний ROI і winrate\n\n"
            "📊 1,847 беттерів вже контролюють свої ставки\n\n"
            "🎁 Спробуй 7 днів безкоштовно 👇"
        )

    if lang == "ru":
        return (
            "😤 Сливаешь деньги на ставках?\n\n"
            "Bet Tracker Bot анализирует твои ставки и показывает:\n"
            " Где ты теряешь больше всего\n"
            " Когда ставишь на эмоциях\n"
            " Твой реальный ROI и winrate\n\n"
            "📊 1,847 беттеров уже контролируют свои ставки\n\n"
            "🎁 Попробуй 7 дней бесплатно 👇"
        )

    return (
        "😤 Losing money on bets?\n\n"
        "Bet Tracker Bot analyzes your bets and shows:\n"
        " Where you lose the most\n"
        " When you bet on emotions\n"
        " Your real ROI and winrate\n\n"
        "📊 1,847 bettors already track their stats\n\n"
        "🎁 Try free for 7 days 👇"
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    create_user_if_not_exists(user)

    db_user = get_user(user.id)
    lang = _normalize_lang((db_user or {}).get("lang", "en"))

    if not is_onboarding_completed(user.id):
        return await start_onboarding(update, context)

    await send_standard_start(update, lang)
    return ConversationHandler.END


async def send_standard_start(update: Update, lang: str):
    user = update.effective_user

    if user_has_access(user.id):
        active_text = {
            "ua": "вњ” Р”РѕСЃС‚СѓРї Р°РєС‚РёРІРЅРёР№.",
            "ru": "вњ” Р”РѕСЃС‚СѓРї Р°РєС‚РёРІРµРЅ.",
            "en": "вњ” Access is active.",
        }[lang]

        await update.message.reply_text(
            active_text,
            reply_markup=main_menu_keyboard(lang, (db_user or {}).get("plan", "basic"))
        )
        return

    promo_available = not has_used_promo_offer(user.id)

    await update.message.reply_text(
        _welcome_text(lang, promo_available),
        reply_markup=welcome_offer_keyboard(lang)
    )


async def start_offer_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    tg_user = update.effective_user
    create_user_if_not_exists(tg_user)

    user = get_user(tg_user.id)
    lang = _normalize_lang((user or {}).get("lang", "en"))

    if user_has_access(tg_user.id):
        active_text = {
            "ua": "вњ” Р”РѕСЃС‚СѓРї Р°РєС‚РёРІРЅРёР№.",
            "ru": "вњ” Р”РѕСЃС‚СѓРї Р°РєС‚РёРІРµРЅ.",
            "en": "вњ” Access is active.",
        }[lang]

        await query.message.reply_text(
            active_text,
            reply_markup=main_menu_keyboard(lang, (user or {}).get("plan", "basic"))
        )
        return

    if query.data == "try_trial":
        if is_trial_available(tg_user.id):
            start_trial_mode(tg_user.id)

            trial_text = {
                "ua": (
                    "🚀 Пробний доступ активовано!\n\n"
                    "У тебе є 7 днів і 5 скрінів на день.\n"
                    "Надішли перший скрін ставки 👇"
                ),
                "ru": (
                    "🚀 Пробный доступ активирован!\n\n"
                    "У тебя есть 7 дней и 5 скринов в день.\n"
                    "Отправь первый скрин ставки 👇"
                ),
                "en": (
                    "🚀 Trial access activated!\n\n"
                    "You have 7 days and 5 screenshots per day.\n"
                    "Send your first bet screenshot 👇"
                ),
            }[lang]

            await query.message.reply_text(
                trial_text,
                reply_markup=main_menu_keyboard(lang, (user or {}).get("plan", "basic"))
            )
        else:
            remaining = get_trial_remaining(tg_user.id)

            limit_text = {
                "ua": f"вќЊ РџСЂРѕР±РЅРёР№ РґРѕСЃС‚СѓРї РІР¶Рµ РІРёРєРѕСЂРёСЃС‚Р°РЅРѕ. Р—Р°Р»РёС€РёР»РѕСЃСЊ: {remaining}",
                "ru": f"вќЊ РџСЂРѕР±РЅС‹Р№ РґРѕСЃС‚СѓРї СѓР¶Рµ РёСЃРїРѕР»СЊР·РѕРІР°РЅ. РћСЃС‚Р°Р»РѕСЃСЊ: {remaining}",
                "en": f"вќЊ Trial access has already been used. Remaining: {remaining}",
            }[lang]

            await query.message.reply_text(limit_text)

    elif query.data == "pay_now":
        buy_text = {
            "ua": (
                "рџљЂ РџРѕРІРЅРёР№ РґРѕСЃС‚СѓРї РґР°С”:\n\n"
                "рџ“Љ РџРѕРІРЅСѓ СЃС‚Р°С‚РёСЃС‚РёРєСѓ\n"
                "рџ§  РђРЅР°Р»С–С‚РёРєСѓ\n"
                "рџ“€ РљРѕРЅС‚СЂРѕР»СЊ ROI\n"
                #"рџЋЇ РЎС‚Р°РІРєРё Р· РІРёСЃРѕРєРѕСЋ Р№РјРѕРІС–СЂРЅС–СЃС‚СЋ\n\n"
                "рџ‘‡ РћР±РµСЂРё С‚Р°СЂРёС„"
            ),
            "ru": (
                "рџљЂ РџРѕР»РЅС‹Р№ РґРѕСЃС‚СѓРї РґР°С‘С‚:\n\n"
                "рџ“Љ РџРѕР»РЅСѓСЋ СЃС‚Р°С‚РёСЃС‚РёРєСѓ\n"
                "рџ§  РђРЅР°Р»РёС‚РёРєСѓ\n"
                "рџ“€ РљРѕРЅС‚СЂРѕР»СЊ ROI\n"
                #"рџЋЇ РЎС‚Р°РІРєРё СЃ РІС‹СЃРѕРєРѕР№ РІРµСЂРѕСЏС‚РЅРѕСЃС‚СЊСЋ\n\n"
                "рџ‘‡ Р’С‹Р±РµСЂРё С‚Р°СЂРёС„"
            ),
            "en": (
                "рџљЂ Full access gives you:\n\n"
                "рџ“Љ Full statistics\n"
                "рџ§  Analytics\n"
                "рџ“€ ROI control\n"
                "рџЋЇ High-probability bets\n\n"
                "рџ‘‡ Choose a plan"
            ),
        }[lang]

        await query.message.reply_text(
            buy_text,
            reply_markup=access_keyboard(lang)
        )

#def _welcome_text(lang: str, promo_available: bool) -> str:
#    if lang == "ru":
#       return (
#            "РџСЂРёРІРµС‚ рџ‘‹\n\n"
#           "Р­С‚Рѕ Bet Tracker Bot вЂ” РёРЅСЃС‚СЂСѓРјРµРЅС‚ РґР»СЏ Р°РЅР°Р»РёР·Р° С‚РІРѕРёС… СЃС‚Р°РІРѕРє рџ“Љ\n\n"
#            "Р§С‚Рѕ С‚С‹ РїРѕР»СѓС‡РёС€СЊ:\n"
#            "вЂў РЎС‚Р°С‚РёСЃС‚РёРєСѓ РїСЂРёР±С‹Р»Рё Рё СѓР±С‹С‚РєРѕРІ рџ’°\n"
#           "вЂў ROI Рё РІРёРЅСЂРµР№С‚ рџ“€\n"
#            "вЂў РЎСЂРµРґРЅРёР№ РєРѕСЌС„С„РёС†РёРµРЅС‚ рџЋЇ\n"
#            "вЂў РђРЅР°Р»РёС‚РёРєСѓ РїРѕ СЃС‚Р°РІРєР°Рј\n\n"
#            "рџ”Ґ РЈР¶Рµ 1200+ РїРѕР»СЊР·РѕРІР°С‚РµР»РµР№\n"
#            "рџ“Љ РЎСЂРµРґРЅРёР№ ROI: +11%\n\n"
#            "РРЅСЃС‚СЂСѓРєС†РёСЏ @bets_academy_platform\n"
#            "рџ‘‡ РџРѕРїСЂРѕР±СѓР№ СЃР°Рј"
#        )
#    else:
#        return (
#            "РџСЂРёРІС–С‚ рџ‘‹\n\n"
#            "Р¦Рµ Bet Tracker Bot вЂ” С–РЅСЃС‚СЂСѓРјРµРЅС‚ РґР»СЏ Р°РЅР°Р»С–Р·Сѓ С‚РІРѕС—С… СЃС‚Р°РІРѕРє рџ“Љ\n\n"
#            "Р©Рѕ С‚Рё РѕС‚СЂРёРјР°С”С€:\n"
#            "вЂў РЎС‚Р°С‚РёСЃС‚РёРєСѓ РїСЂРёР±СѓС‚РєСѓ С‚Р° Р·Р±РёС‚РєС–РІ рџ’°\n"
#            "вЂў ROI С– РІС–РЅСЂРµР№С‚ рџ“€\n"
#            "вЂў РЎРµСЂРµРґРЅС–Р№ РєРѕРµС„С–С†С–С”РЅС‚ рџЋЇ\n"
#            "вЂў РђРЅР°Р»С–С‚РёРєСѓ РїРѕ СЃС‚Р°РІРєР°С…\n\n"
#            "рџ”Ґ Р’Р¶Рµ 1200+ РєРѕСЂРёСЃС‚СѓРІР°С‡С–РІ\n"
#            "рџ“Љ РЎРµСЂРµРґРЅС–Р№ ROI: +11%\n\n"
#            "Р†РЅСЃС‚СЂСѓРєС†С–СЏ @bets_academy_platform\n"
#            "рџ‘‡ РЎРїСЂРѕР±СѓР№ СЃР°Рј"
#        )
