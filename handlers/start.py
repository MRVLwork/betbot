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
            "😤 Ти зараз в мінусі чи в плюсі?\n\n"
            "Більшість беттерів думають що в плюсі.\n"
            "Реальна статистика показує інше.\n\n"
            "Bet Tracker Bot аналізує твої ставки і показує:\n"
            " Коли ти ставиш на тілті  і скільки це коштує\n"
            " Які типи ставок реально дають плюс\n"
            " Твій чесний ROI без самообману\n\n"
            "Надішли перший скрін \n"
            "і за 30 секунд побачиш реальну картину.\n\n"
            "🎁 7 днів безкоштовно 👇"
        )

    if lang == "ru":
        return (
            "😤 Ты сейчас в минусе или в плюсе?\n\n"
            "Большинство беттеров думают что в плюсе.\n"
            "Реальная статистика показывает другое.\n\n"
            "Bet Tracker Bot анализирует твои ставки и показывает:\n"
            " Когда ты ставишь на тилте  и сколько это стоит\n"
            " Какие типы ставок реально дают плюс\n"
            " Твой честный ROI без самообмана\n\n"
            "Отправь первый скрин \n"
            "и за 30 секунд увидишь реальную картину.\n\n"
            "🎁 7 дней бесплатно 👇"
        )

    return (
        "😤 Are you currently in profit or loss?\n\n"
        "Most bettors think they're in profit.\n"
        "Real stats show something different.\n\n"
        "Bet Tracker Bot analyzes your bets and shows:\n"
        " When you bet on tilt  and what it costs you\n"
        " Which bet types actually make profit\n"
        " Your honest ROI without self-deception\n\n"
        "Send your first screenshot \n"
        "and see the real picture in 30 seconds.\n\n"
        "🎁 7 days free 👇"
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
                    "рџљЂ РџСЂРѕР±РЅРёР№ РґРѕСЃС‚СѓРї Р°РєС‚РёРІРѕРІР°РЅРѕ!\n\n"
                    "РЈ С‚РµР±Рµ С” 7 РґРЅС–РІ С– 5 СЃРєСЂС–РЅС–РІ РЅР° РґРµРЅСЊ.\n"
                    "РќР°РґС–С€Р»Рё РїРµСЂС€РёР№ СЃРєСЂС–РЅ СЃС‚Р°РІРєРё рџ‘‡"
                ),
                "ru": (
                    "рџљЂ РџСЂРѕР±РЅС‹Р№ РґРѕСЃС‚СѓРї Р°РєС‚РёРІРёСЂРѕРІР°РЅ!\n\n"
                    "РЈ С‚РµР±СЏ РµСЃС‚СЊ 7 РґРЅРµР№ Рё 5 СЃРєСЂРёРЅРѕРІ РІ РґРµРЅСЊ.\n"
                    "РћС‚РїСЂР°РІСЊ РїРµСЂРІС‹Р№ СЃРєСЂРёРЅ СЃС‚Р°РІРєРё рџ‘‡"
                ),
                "en": (
                    "рџљЂ Trial access activated!\n\n"
                    "You have 7 days and 5 screenshots per day.\n"
                    "Send your first bet screenshot рџ‘‡"
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
                "рџ’і РћР±РµСЂРё С‚Р°СЂРёС„:\n\n"
                "рџ”№ Basic 1 РјС–СЃСЏС†СЊ  $5\n"
                " 15 СЃРєСЂС–РЅС–РІ РЅР° РґРµРЅСЊ\n"
                " РџРѕРІРЅР° СЃС‚Р°С‚РёСЃС‚РёРєР° С– Р°РЅР°Р»С–С‚РёРєР°\n\n"
                " VIP 1 РјС–СЃСЏС†СЊ  $19.99\n"
                " 30 СЃРєСЂС–РЅС–РІ РЅР° РґРµРЅСЊ\n"
                " AI РўСЂРµРЅРµСЂ\n"
                " Р’СЃС– С„СѓРЅРєС†С–С— Р±РµР· РѕР±РјРµР¶РµРЅСЊ"
            ),
            "ru": (
                "рџ’і Р’С‹Р±РµСЂРё С‚Р°СЂРёС„:\n\n"
                "рџ”№ Basic 1 РјРµСЃСЏС†  $5\n"
                " 15 СЃРєСЂРёРЅРѕРІ РІ РґРµРЅСЊ\n"
                " РџРѕР»РЅР°СЏ СЃС‚Р°С‚РёСЃС‚РёРєР° Рё Р°РЅР°Р»РёС‚РёРєР°\n\n"
                " VIP 1 РјРµСЃСЏС†  $19.99\n"
                " 30 СЃРєСЂРёРЅРѕРІ РІ РґРµРЅСЊ\n"
                " AI РўСЂРµРЅРµСЂ\n"
                " Р’СЃРµ С„СѓРЅРєС†РёРё Р±РµР· РѕРіСЂР°РЅРёС‡РµРЅРёР№"
            ),
            "en": (
                "рџ’і Choose your plan:\n\n"
                "рџ”№ Basic 1 month  $5\n"
                " 15 screenshots per day\n"
                " Full statistics and analytics\n\n"
                " VIP 1 month  $19.99\n"
                " 30 screenshots per day\n"
                " AI Coach\n"
                " All features unlimited"
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
