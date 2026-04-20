from datetime import datetime

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bets_db import create_bet, get_basic_stats_between, get_tilt_signal_context, update_bet_emotion
from db import (
    TRIAL_SCREEN_LIMIT,
    get_user,
    user_has_access,
    get_user_daily_limit,
    count_user_photos_today,
    get_user_remaining_photos_today,
    log_user_photo,
    is_trial_available,
    get_trial_remaining,
    increment_trial_usage,
    get_trial_start,
)
from keyboards import access_keyboard, welcome_offer_keyboard
from languages import get_text
from services.ai_service import analyze_basic_bet_screenshot
from handlers.tools import handle_ai_analysis_input


def _normalize_lang(lang: str) -> str:
    lang = (lang or "en").lower()
    if lang.startswith("uk") or lang.startswith("ua"):
        return "ua"
    if lang.startswith("ru"):
        return "ru"
    return "en"


def _result_label(lang: str, result: str) -> str:
    if result == "win":
        return get_text(lang, "bet_result_win")
    if result == "lose":
        return get_text(lang, "bet_result_lose")
    if result == "refund":
        return get_text(lang, "bet_result_refund")
    if result == "pending":
        return get_text(lang, "bet_result_pending")
    return result


def _bet_type_label(lang: str, bet_type: str | None = None, bet_market: str | None = None) -> str:
    lang = _normalize_lang(lang)

    labels = {
        "ua": {
            "1x2": "1X2",
            "total": "С‚РѕС‚Р°Р»",
            "btts": "РѕР±РёРґРІС– Р·Р°Р±'СЋС‚СЊ",
            "handicap": "С„РѕСЂР°",
            "double_chance": "1X/2X",
            "corners": "РєСѓС‚РѕРІС–",
            "cards": "РєР°СЂС‚РєРё",
            "other": "С–РЅС€Рµ",
            "result": "СЂРµР·СѓР»СЊС‚Р°С‚",
        },
        "ru": {
            "1x2": "1X2",
            "total": "С‚РѕС‚Р°Р»",
            "btts": "РѕР±Рµ Р·Р°Р±СЊСЋС‚",
            "handicap": "С„РѕСЂР°",
            "double_chance": "1X/2X",
            "corners": "СѓРіР»РѕРІС‹Рµ",
            "cards": "РєР°СЂС‚РѕС‡РєРё",
            "other": "РґСЂСѓРіРѕРµ",
            "result": "СЂРµР·СѓР»СЊС‚Р°С‚",
        },
        "en": {
            "1x2": "1X2",
            "total": "total",
            "btts": "both teams to score",
            "handicap": "handicap",
            "double_chance": "1X/2X",
            "corners": "corners",
            "cards": "cards",
            "other": "other",
            "result": "result",
        },
    }

    if bet_market:
        return labels.get(lang, labels["en"]).get(bet_market, bet_market)
    if bet_type:
        return labels.get(lang, labels["en"]).get(bet_type, bet_type)
    return "-"


def _daily_limit_reached_text(lang: str, plan: str, limit: int) -> str:
    lang = _normalize_lang(lang)
    plan = (plan or "basic").lower()

    texts = {
        "ua": {
            "trial": (
                f"рџљ« Р›С–РјС–С‚ РЅР° СЃСЊРѕРіРѕРґРЅС–: {limit}/{limit} СЃРєСЂС–РЅС–РІ РІРёРєРѕСЂРёСЃС‚Р°РЅРѕ\n\n"
                "Р’ Basic: 15 СЃРєСЂС–РЅС–РІ/РґРµРЅСЊ\n"
                "Р’ VIP: 30 СЃРєСЂС–РЅС–РІ/РґРµРЅСЊ\n\n"
                "рџ‘‡ РћРЅРѕРІРёС‚Рё РїР»Р°РЅ"
            ),
            "basic": (
                f"рџљ« Р›С–РјС–С‚ РЅР° СЃСЊРѕРіРѕРґРЅС–: {limit}/{limit} СЃРєСЂС–РЅС–РІ РІРёРєРѕСЂРёСЃС‚Р°РЅРѕ\n\n"
                "Р’ VIP: 30 СЃРєСЂС–РЅС–РІ/РґРµРЅСЊ + AI РўСЂРµРЅРµСЂ\n\n"
                "рџ‘‡ РћРЅРѕРІРёС‚Рё РґРѕ VIP"
            ),
            "vip": (
                f"рџљ« Р›С–РјС–С‚ РЅР° СЃСЊРѕРіРѕРґРЅС–: {limit}/{limit} СЃРєСЂС–РЅС–РІ РІРёРєРѕСЂРёСЃС‚Р°РЅРѕ\n"
                "РџРѕРІРµСЂРЅРёСЃСЊ Р·Р°РІС‚СЂР° рџЊ™"
            ),
        },
        "ru": {
            "trial": (
                f"рџљ« Р›РёРјРёС‚ РЅР° СЃРµРіРѕРґРЅСЏ: {limit}/{limit} СЃРєСЂРёРЅРѕРІ РёСЃРїРѕР»СЊР·РѕРІР°РЅРѕ\n\n"
                "Р’ Basic: 15 СЃРєСЂРёРЅРѕРІ/РґРµРЅСЊ\n"
                "Р’ VIP: 30 СЃРєСЂРёРЅРѕРІ/РґРµРЅСЊ\n\n"
                "рџ‘‡ РћР±РЅРѕРІРёС‚СЊ РїР»Р°РЅ"
            ),
            "basic": (
                f"рџљ« Р›РёРјРёС‚ РЅР° СЃРµРіРѕРґРЅСЏ: {limit}/{limit} СЃРєСЂРёРЅРѕРІ РёСЃРїРѕР»СЊР·РѕРІР°РЅРѕ\n\n"
                "Р’ VIP: 30 СЃРєСЂРёРЅРѕРІ/РґРµРЅСЊ + AI РўСЂРµРЅРµСЂ\n\n"
                "рџ‘‡ РћР±РЅРѕРІРёС‚СЊ РґРѕ VIP"
            ),
            "vip": (
                f"рџљ« Р›РёРјРёС‚ РЅР° СЃРµРіРѕРґРЅСЏ: {limit}/{limit} СЃРєСЂРёРЅРѕРІ РёСЃРїРѕР»СЊР·РѕРІР°РЅРѕ\n"
                "Р’РѕР·РІСЂР°С‰Р°Р№СЃСЏ Р·Р°РІС‚СЂР° рџЊ™"
            ),
        },
        "en": {
            "trial": (
                f"рџљ« Today's limit reached: {limit}/{limit} screenshots used\n\n"
                "In Basic: 15 screenshots/day\n"
                "In VIP: 30 screenshots/day\n\n"
                "рџ‘‡ Upgrade plan"
            ),
            "basic": (
                f"рџљ« Today's limit reached: {limit}/{limit} screenshots used\n\n"
                "In VIP: 30 screenshots/day + AI Coach\n\n"
                "рџ‘‡ Upgrade to VIP"
            ),
            "vip": (
                f"рџљ« Today's limit reached: {limit}/{limit} screenshots used\n"
                "Come back tomorrow рџЊ™"
            ),
        },
    }

    return texts.get(lang, texts["en"]).get(plan, texts.get(lang, texts["en"])["basic"])


def _trial_progress_text(lang: str, used_trial: int, remaining_trial: int) -> str:
    lang = _normalize_lang(lang)

    if lang == "ua":
        text = f"вњ… РЎРєСЂС–РЅ Р·Р°СЂР°С…РѕРІР°РЅРѕ.\nР’РёРєРѕСЂРёСЃС‚Р°РЅРѕ: {used_trial}/3"
        if remaining_trial > 0:
            text += f"\nР—Р°Р»РёС€РёР»РѕСЃСЊ: {remaining_trial}/3"
        return text

    if lang == "ru":
        text = f"вњ… РЎРєСЂРёРЅ Р·Р°СЃС‡РёС‚Р°РЅ.\nРСЃРїРѕР»СЊР·РѕРІР°РЅРѕ: {used_trial}/3"
        if remaining_trial > 0:
            text += f"\nРћСЃС‚Р°Р»РѕСЃСЊ: {remaining_trial}/3"
        return text

    text = f"вњ… Screenshot counted.\nUsed: {used_trial}/3"
    if remaining_trial > 0:
        text += f"\nRemaining: {remaining_trial}/3"
    return text


def _trial_fail_text(lang: str, used_trial: int, remaining_trial: int) -> str:
    lang = _normalize_lang(lang)

    if lang == "ua":
        text = (
            f"вљ пёЏ Р¦РµР№ СЃРєСЂС–РЅ РЅРµ РІРґР°Р»РѕСЃСЏ СЂРѕР·РїС–Р·РЅР°С‚Рё, Р°Р»Рµ РІС–РЅ Р·Р°СЂР°С…РѕРІР°РЅРёР№ Сѓ С‚РµСЃС‚.\n"
            f"Р’РёРєРѕСЂРёСЃС‚Р°РЅРѕ: {used_trial}/3"
        )
        if remaining_trial > 0:
            text += f"\nР—Р°Р»РёС€РёР»РѕСЃСЊ: {remaining_trial}/3"
        return text

    if lang == "ru":
        text = (
            f"вљ пёЏ Р­С‚РѕС‚ СЃРєСЂРёРЅ РЅРµ СѓРґР°Р»РѕСЃСЊ СЂР°СЃРїРѕР·РЅР°С‚СЊ, РЅРѕ РѕРЅ Р·Р°СЃС‡РёС‚Р°РЅ РІ С‚РµСЃС‚.\n"
            f"РСЃРїРѕР»СЊР·РѕРІР°РЅРѕ: {used_trial}/3"
        )
        if remaining_trial > 0:
            text += f"\nРћСЃС‚Р°Р»РѕСЃСЊ: {remaining_trial}/3"
        return text

    text = (
        f"вљ пёЏ This screenshot could not be recognized, but it was counted in the trial.\n"
        f"Used: {used_trial}/3"
    )
    if remaining_trial > 0:
        text += f"\nRemaining: {remaining_trial}/3"
    return text


def _trial_progress_text(lang: str, used_trial: int, remaining_trial: int) -> str:
    lang = _normalize_lang(lang)

    if lang == "ua":
        text = f"вњ… РЎРєСЂС–РЅ Р·Р°СЂР°С…РѕРІР°РЅРѕ.\nР’РёРєРѕСЂРёСЃС‚Р°РЅРѕ: {used_trial}/{TRIAL_SCREEN_LIMIT}"
        if remaining_trial > 0:
            text += f"\nР—Р°Р»РёС€РёР»РѕСЃСЊ: {remaining_trial}/{TRIAL_SCREEN_LIMIT}"
        return text

    if lang == "ru":
        text = f"вњ… РЎРєСЂРёРЅ Р·Р°СЃС‡РёС‚Р°РЅ.\nРСЃРїРѕР»СЊР·РѕРІР°РЅРѕ: {used_trial}/{TRIAL_SCREEN_LIMIT}"
        if remaining_trial > 0:
            text += f"\nРћСЃС‚Р°Р»РѕСЃСЊ: {remaining_trial}/{TRIAL_SCREEN_LIMIT}"
        return text

    text = f"вњ… Screenshot counted.\nUsed: {used_trial}/{TRIAL_SCREEN_LIMIT}"
    if remaining_trial > 0:
        text += f"\nRemaining: {remaining_trial}/{TRIAL_SCREEN_LIMIT}"
    return text


def _trial_fail_text(lang: str, used_trial: int, remaining_trial: int) -> str:
    lang = _normalize_lang(lang)

    if lang == "ua":
        text = (
            "вљ пёЏ Р¦РµР№ СЃРєСЂС–РЅ РЅРµ РІРґР°Р»РѕСЃСЏ СЂРѕР·РїС–Р·РЅР°С‚Рё, Р°Р»Рµ РІС–РЅ Р·Р°СЂР°С…РѕРІР°РЅРёР№ Сѓ С‚РµСЃС‚.\n"
            f"Р’РёРєРѕСЂРёСЃС‚Р°РЅРѕ: {used_trial}/{TRIAL_SCREEN_LIMIT}"
        )
        if remaining_trial > 0:
            text += f"\nР—Р°Р»РёС€РёР»РѕСЃСЊ: {remaining_trial}/{TRIAL_SCREEN_LIMIT}"
        return text

    if lang == "ru":
        text = (
            "вљ пёЏ Р­С‚РѕС‚ СЃРєСЂРёРЅ РЅРµ СѓРґР°Р»РѕСЃСЊ СЂР°СЃРїРѕР·РЅР°С‚СЊ, РЅРѕ РѕРЅ Р·Р°СЃС‡РёС‚Р°РЅ РІ С‚РµСЃС‚.\n"
            f"РСЃРїРѕР»СЊР·РѕРІР°РЅРѕ: {used_trial}/{TRIAL_SCREEN_LIMIT}"
        )
        if remaining_trial > 0:
            text += f"\nРћСЃС‚Р°Р»РѕСЃСЊ: {remaining_trial}/{TRIAL_SCREEN_LIMIT}"
        return text

    text = (
        "вљ пёЏ This screenshot could not be recognized, but it was counted in the trial.\n"
        f"Used: {used_trial}/{TRIAL_SCREEN_LIMIT}"
    )
    if remaining_trial > 0:
        text += f"\nRemaining: {remaining_trial}/{TRIAL_SCREEN_LIMIT}"
    return text


def _build_trial_pitch(lang: str, stats: dict, used_trial: int) -> str | None:
    if used_trial < 2:
        return None

    lang = _normalize_lang(lang)
    profit = float(stats.get("net_profit", 0) or 0)
    roi = float(stats.get("roi", 0) or 0)
    win_rate = float(stats.get("win_rate", 0) or 0)
    avg_odds = float(stats.get("avg_odds", 0) or 0)

    if lang == "en":
        if profit > 0:
            return (
                "рџ“Љ Now the picture is clearer\n\n"
                f"рџ’° Profit: {profit}\n"
                f"рџ“€ ROI: {roi}%\n"
                f"рџЋЇ Winrate: {win_rate}%\n"
                f"рџ“Љ Average odds: {avg_odds}\n\n"
                "рџ”Ґ Good result.\n\n"
                "But here is the key point:\n\n"
                "You are in profit now вЂ”\n"
                "but without a system it is easy to lose it.\n\n"
                "рџ“Љ Only distance shows\n"
                "whether this is luck or a stable edge.\n\n"
                "рџ‘‡ Continue the analysis or lock in the result"
            )

        if profit < 0:
            return (
                "рџ“Љ Now the picture is clearer\n\n"
                f"рџ’° Profit: {profit}\n"
                f"рџ“€ ROI: {roi}%\n"
                f"рџЋЇ Winrate: {win_rate}%\n"
                f"рџ“Љ Average odds: {avg_odds}\n\n"
                "вќ— Important point:\n\n"
                "At this stage most users realize\n"
                "that they are not earning вЂ” they are losing.\n\n"
                "You are at the same stage now.\n\n"
                "рџ‘‡ Continue the analysis or unlock full access"
            )

        return (
            "рџ“Љ You already have the first picture\n\n"
            f"рџ’° Profit: {profit}\n"
            f"рџ“€ ROI: {roi}%\n"
            f"рџЋЇ Winrate: {win_rate}%\n"
            f"рџ“Љ Average odds: {avg_odds}\n\n"
            "For now the result is around zero.\n"
            "The next few bets will show\n"
            "whether you really have a system.\n\n"
            "рџ‘‡ Continue to see the real picture"
        )

    if profit > 0:
        header = "рџ“Љ РўРµРїРµСЂ РІР¶Рµ С” РєР°СЂС‚РёРЅР°\n\n" if lang == "ua" else "рџ“Љ РўРµРїРµСЂСЊ СѓР¶Рµ РµСЃС‚СЊ РєР°СЂС‚РёРЅР°\n\n"
        body = (
            f"рџ’° РџСЂРёР±СѓС‚РѕРє: {profit}\n"
            f"рџ“€ ROI: {roi}%\n"
            f"рџЋЇ Winrate: {win_rate}%\n"
            f"рџ“Љ РЎРµСЂРµРґРЅС–Р№ РєРѕРµС„С–С†С–С”РЅС‚: {avg_odds}\n\n"
            "рџ”Ґ РќРµРїРѕРіР°РЅРёР№ СЂРµР·СѓР»СЊС‚Р°С‚.\n\n"
            "РђР»Рµ С” РЅСЋР°РЅСЃ:\n\n"
            "РўРё Р·Р°СЂР°Р· РІ РїР»СЋСЃС– вЂ”\n"
            "Р°Р»Рµ Р±РµР· СЃРёСЃС‚РµРјРё С†Рµ Р»РµРіРєРѕ РІС‚СЂР°С‚РёС‚Рё.\n\n"
            "рџ“Љ РЎР°РјРµ РЅР° РґРёСЃС‚Р°РЅС†С–С— СЃС‚Р°С” РІРёРґРЅРѕ,\n"
            "С‡Рё С†Рµ РІРёРїР°РґРєРѕРІС–СЃС‚СЊ С‡Рё СЃС‚Р°Р±С–Р»СЊРЅРёР№ РїР»СЋСЃ.\n\n"
            "рџ‘‡ РџСЂРѕРґРѕРІР¶СѓР№ Р°РЅР°Р»С–Р· Р°Р±Рѕ Р·Р°РєСЂС–РїРё СЂРµР·СѓР»СЊС‚Р°С‚"
            if lang == "ua" else
            f"рџ’° РџСЂРёР±С‹Р»СЊ: {profit}\n"
            f"рџ“€ ROI: {roi}%\n"
            f"рџЋЇ Winrate: {win_rate}%\n"
            f"рџ“Љ РЎСЂРµРґРЅРёР№ РєРѕСЌС„С„РёС†РёРµРЅС‚: {avg_odds}\n\n"
            "рџ”Ґ РќРµРїР»РѕС…РѕР№ СЂРµР·СѓР»СЊС‚Р°С‚.\n\n"
            "РќРѕ РµСЃС‚СЊ РЅСЋР°РЅСЃ:\n\n"
            "РўС‹ СЃРµР№С‡Р°СЃ РІ РїР»СЋСЃРµ вЂ”\n"
            "РЅРѕ Р±РµР· СЃРёСЃС‚РµРјС‹ СЌС‚Рѕ Р»РµРіРєРѕ РїРѕС‚РµСЂСЏС‚СЊ.\n\n"
            "рџ“Љ РРјРµРЅРЅРѕ РЅР° РґРёСЃС‚Р°РЅС†РёРё СЃС‚Р°РЅРѕРІРёС‚СЃСЏ РІРёРґРЅРѕ,\n"
            "СЃР»СѓС‡Р°Р№РЅРѕСЃС‚СЊ СЌС‚Рѕ РёР»Рё СЃС‚Р°Р±РёР»СЊРЅС‹Р№ РїР»СЋСЃ.\n\n"
            "рџ‘‡ РџСЂРѕРґРѕР»Р¶Р°Р№ Р°РЅР°Р»РёР· РёР»Рё Р·Р°РєСЂРµРїРё СЂРµР·СѓР»СЊС‚Р°С‚"
        )
        return header + body

    if profit < 0:
        header = "рџ“Љ РўРµРїРµСЂ РІР¶Рµ С” РєР°СЂС‚РёРЅР°\n\n" if lang == "ua" else "рџ“Љ РўРµРїРµСЂСЊ СѓР¶Рµ РµСЃС‚СЊ РєР°СЂС‚РёРЅР°\n\n"
        body = (
            f"рџ’° РџСЂРёР±СѓС‚РѕРє: {profit}\n"
            f"рџ“€ ROI: {roi}%\n"
            f"рџЋЇ Winrate: {win_rate}%\n"
            f"рџ“Љ РЎРµСЂРµРґРЅС–Р№ РєРѕРµС„С–С†С–С”РЅС‚: {avg_odds}\n\n"
            "вќ—пёЏ Р’Р°Р¶Р»РёРІРёР№ РјРѕРјРµРЅС‚:\n\n"
            "Р—Р°Р·РІРёС‡Р°Р№ РЅР° С†СЊРѕРјСѓ РµС‚Р°РїС– Р»СЋРґРё СЂРѕР·СѓРјС–СЋС‚СЊ,\n"
            "С‰Рѕ РІРѕРЅРё РЅРµ Р·Р°СЂРѕР±Р»СЏСЋС‚СЊ, Р° РІС‚СЂР°С‡Р°СЋС‚СЊ.\n\n"
            "РўРё Р·Р°СЂР°Р· РЅР° С†СЊРѕРјСѓ Р¶ РµС‚Р°РїС–.\n\n"
            "рџ‘‡ РџСЂРѕРґРѕРІР¶СѓР№ Р°РЅР°Р»С–Р· Р°Р±Рѕ РІС–РґРєСЂРёР№ РїРѕРІРЅРёР№ РґРѕСЃС‚СѓРї"
            if lang == "ua" else
            f"рџ’° РџСЂРёР±С‹Р»СЊ: {profit}\n"
            f"рџ“€ ROI: {roi}%\n"
            f"рџЋЇ Winrate: {win_rate}%\n"
            f"рџ“Љ РЎСЂРµРґРЅРёР№ РєРѕСЌС„С„РёС†РёРµРЅС‚: {avg_odds}\n\n"
            "вќ—пёЏ Р’Р°Р¶РЅС‹Р№ РјРѕРјРµРЅС‚:\n\n"
            "РћР±С‹С‡РЅРѕ РЅР° СЌС‚РѕРј СЌС‚Р°РїРµ Р»СЋРґРё РїРѕРЅРёРјР°СЋС‚,\n"
            "С‡С‚Рѕ РѕРЅРё РЅРµ Р·Р°СЂР°Р±Р°С‚С‹РІР°СЋС‚, Р° С‚РµСЂСЏСЋС‚.\n\n"
            "РўС‹ СЃРµР№С‡Р°СЃ РЅР° СЌС‚РѕРј Р¶Рµ СЌС‚Р°РїРµ.\n\n"
            "рџ‘‡ РџСЂРѕРґРѕР»Р¶Р°Р№ Р°РЅР°Р»РёР· РёР»Рё РѕС‚РєСЂРѕР№ РїРѕР»РЅС‹Р№ РґРѕСЃС‚СѓРї"
        )
        return header + body

    header = "рџ“Љ РЈР¶Рµ С” РїРµСЂС€Р° РєР°СЂС‚РёРЅР°\n\n" if lang == "ua" else "рџ“Љ РЈР¶Рµ РµСЃС‚СЊ РїРµСЂРІР°СЏ РєР°СЂС‚РёРЅР°\n\n"
    body = (
        f"рџ’° РџСЂРёР±СѓС‚РѕРє: {profit}\n"
        f"рџ“€ ROI: {roi}%\n"
        f"рџЋЇ Winrate: {win_rate}%\n"
        f"рџ“Љ РЎРµСЂРµРґРЅС–Р№ РєРѕРµС„С–С†С–С”РЅС‚: {avg_odds}\n\n"
        "РџРѕРєРё СЂРµР·СѓР»СЊС‚Р°С‚ Р±С–Р»СЏ РЅСѓР»СЏ.\n"
        "РЎР°РјРµ РєС–Р»СЊРєР° РЅР°СЃС‚СѓРїРЅРёС… СЃС‚Р°РІРѕРє РїРѕРєР°Р¶СѓС‚СЊ,\n"
        "С‡Рё С” Сѓ С‚РµР±Рµ СЃРёСЃС‚РµРјР°.\n\n"
        "рџ‘‡ РџСЂРѕРґРѕРІР¶СѓР№, С‰РѕР± РїРѕР±Р°С‡РёС‚Рё СЂРµР°Р»СЊРЅСѓ РєР°СЂС‚РёРЅСѓ"
        if lang == "ua" else
        f"рџ’° РџСЂРёР±С‹Р»СЊ: {profit}\n"
        f"рџ“€ ROI: {roi}%\n"
        f"рџЋЇ Winrate: {win_rate}%\n"
        f"рџ“Љ РЎСЂРµРґРЅРёР№ РєРѕСЌС„С„РёС†РёРµРЅС‚: {avg_odds}\n\n"
        "РџРѕРєР° СЂРµР·СѓР»СЊС‚Р°С‚ РѕРєРѕР»Рѕ РЅСѓР»СЏ.\n"
        "РРјРµРЅРЅРѕ РЅРµСЃРєРѕР»СЊРєРѕ СЃР»РµРґСѓСЋС‰РёС… СЃС‚Р°РІРѕРє РїРѕРєР°Р¶СѓС‚,\n"
        "РµСЃС‚СЊ Р»Рё Сѓ С‚РµР±СЏ СЃРёСЃС‚РµРјР°.\n\n"
        "рџ‘‡ РџСЂРѕРґРѕР»Р¶Р°Р№, С‡С‚РѕР±С‹ СѓРІРёРґРµС‚СЊ СЂРµР°Р»СЊРЅСѓСЋ РєР°СЂС‚РёРЅСѓ"
    )
    return header + body


def _build_limit_pitch(lang: str, stats: dict) -> str:
    lang = _normalize_lang(lang)
    profit = float(stats.get("net_profit", 0) or 0)
    roi = float(stats.get("roi", 0) or 0)
    win_rate = float(stats.get("win_rate", 0) or 0)
    avg_odds = float(stats.get("avg_odds", 0) or 0)
    trial_ended_prefix = {
        "ua": "\u0422\u0432\u0456\u0439 7-\u0434\u0435\u043d\u043d\u0438\u0439 \u043f\u0440\u043e\u0431\u043d\u0438\u0439 \u0434\u043e\u0441\u0442\u0443\u043f \u0437\u0430\u0432\u0435\u0440\u0448\u0435\u043d\u043e.\n\n",
        "ru": "\u0422\u0432\u043e\u0439 7-\u0434\u043d\u0435\u0432\u043d\u044b\u0439 \u043f\u0440\u043e\u0431\u043d\u044b\u0439 \u0434\u043e\u0441\u0442\u0443\u043f \u0437\u0430\u0432\u0435\u0440\u0448\u0451\u043d.\n\n",
        "en": "Your 7-day free trial has ended.\n\n",
    }.get(lang, "Your 7-day free trial has ended.\n\n")
    if lang == "en":
        if profit > 0:
            return (trial_ended_prefix + "рџљ« Limit reached\n\n"
                "рџ“Љ So far:\n"
                f"рџ’° Profit: {profit}\n"
                f"рџ“€ ROI: {roi}%\n"
                f"рџЋЇ Winrate: {win_rate}%\n"
                f"рџ“Љ Average odds: {avg_odds}\n\n"
                "рџ”Ґ You are already showing profit.\n\n"
                "But the main question is:\n\n"
                "рџ‘‰ is it a system or just a short streak?\n\n"
                "вќ— This is exactly where most users:\n"
                "вЂ” lose their profit\n"
                "вЂ” start playing more aggressively\n"
                "вЂ” drain their bankroll\n\n"
                "вљЎ Full access is needed\n"
                "to lock in and scale your result\n\n"
                "рџ‘‡ DonвЂ™t stop here"
            )
        if profit < 0:
            return (trial_ended_prefix + "рџљ« Limit reached\n\n"
                "рџ“Љ So far:\n"
                f"рџ’° Profit: {profit}\n"
                f"рџ“€ ROI: {roi}%\n"
                f"рџЋЇ Winrate: {win_rate}%\n"
                f"рџ“Љ Average odds: {avg_odds}\n\n"
                "вќ— And this is only the beginning.\n\n"
                "Without statistics, you will keep repeating the same mistakes.\n\n"
                "вљЎ Full access unlocks:\n"
                "вЂ” full statistics\n"
                "вЂ” bet analysis\n"
                "вЂ” result control\n\n"
                "рџ‘‡ DonвЂ™t leave it like this"
            )
        return (trial_ended_prefix + "рџљ« Limit reached\n\n"
            "рџ“Љ So far:\n"
            f"рџ’° Profit: {profit}\n"
            f"рџ“€ ROI: {roi}%\n"
            f"рџЋЇ Winrate: {win_rate}%\n"
            f"рџ“Љ Average odds: {avg_odds}\n\n"
            "Right now the result is almost flat.\n"
            "Only distance will show\n"
            "whether your strategy really works.\n\n"
            "рџ‘‡ Unlock full access and continue"
        )

    if profit > 0:
        return (trial_ended_prefix + "рџљ« Р›С–РјС–С‚ РґРѕСЃСЏРіРЅСѓС‚Рѕ\n\n"
            "рџ“Љ Р—Р° С†РµР№ С‡Р°СЃ:\n"
            f"рџ’° РџСЂРёР±СѓС‚РѕРє: {profit}\n"
            f"рџ“€ ROI: {roi}%\n"
            f"рџЋЇ Winrate: {win_rate}%\n"
            f"рџ“Љ РЎРµСЂРµРґРЅС–Р№ РєРѕРµС„С–С†С–С”РЅС‚: {avg_odds}\n\n"
            "рџ”Ґ РўРё РІР¶Рµ РїРѕРєР°Р·СѓС”С€ РїР»СЋСЃ.\n\n"
            "РђР»Рµ РіРѕР»РѕРІРЅРµ РїРёС‚Р°РЅРЅСЏ:\n\n"
            "рџ‘‰ С†Рµ СЃРёСЃС‚РµРјР° С‡Рё РїСЂРѕСЃС‚Рѕ РєРѕСЂРѕС‚РєР° СЃРµСЂС–СЏ?\n\n"
            "вќ—пёЏ РЎР°РјРµ С‚СѓС‚ Р±С–Р»СЊС€С–СЃС‚СЊ РіСЂР°РІС†С–РІ:\n"
            "вЂ” РІС‚СЂР°С‡Р°СЋС‚СЊ РїСЂРёР±СѓС‚РѕРє\n"
            "вЂ” РїРѕС‡РёРЅР°СЋС‚СЊ РіСЂР°С‚Рё Р°РіСЂРµСЃРёРІРЅС–С€Рµ\n"
            "вЂ” Р·Р»РёРІР°СЋС‚СЊ Р±Р°РЅРє\n\n"
            "вљЎпёЏ РџРѕРІРЅРёР№ РґРѕСЃС‚СѓРї РїРѕС‚СЂС–Р±РµРЅ,\n"
            "С‰РѕР± Р·Р°С„С–РєСЃСѓРІР°С‚Рё С– РјР°СЃС€С‚Р°Р±СѓРІР°С‚Рё СЂРµР·СѓР»СЊС‚Р°С‚\n\n"
            "рџ‘‡ РќРµ Р·СѓРїРёРЅСЏР№СЃСЏ РЅР° С†СЊРѕРјСѓ"
            if lang == "ua" else
            "рџљ« Р›РёРјРёС‚ РґРѕСЃС‚РёРіРЅСѓС‚\n\n"
            "рџ“Љ Р—Р° СЌС‚Рѕ РІСЂРµРјСЏ:\n"
            f"рџ’° РџСЂРёР±С‹Р»СЊ: {profit}\n"
            f"рџ“€ ROI: {roi}%\n"
            f"рџЋЇ Winrate: {win_rate}%\n"
            f"рџ“Љ РЎСЂРµРґРЅРёР№ РєРѕСЌС„С„РёС†РёРµРЅС‚: {avg_odds}\n\n"
            "рџ”Ґ РўС‹ СѓР¶Рµ РїРѕРєР°Р·С‹РІР°РµС€СЊ РїР»СЋСЃ.\n\n"
            "РќРѕ РіР»Р°РІРЅС‹Р№ РІРѕРїСЂРѕСЃ:\n\n"
            "рџ‘‰ СЌС‚Рѕ СЃРёСЃС‚РµРјР° РёР»Рё РїСЂРѕСЃС‚Рѕ РєРѕСЂРѕС‚РєР°СЏ СЃРµСЂРёСЏ?\n\n"
            "вќ—пёЏ РРјРµРЅРЅРѕ Р·РґРµСЃСЊ Р±РѕР»СЊС€РёРЅСЃС‚РІРѕ РёРіСЂРѕРєРѕРІ:\n"
            "вЂ” С‚РµСЂСЏСЋС‚ РїСЂРёР±С‹Р»СЊ\n"
            "вЂ” РЅР°С‡РёРЅР°СЋС‚ РёРіСЂР°С‚СЊ Р°РіСЂРµСЃСЃРёРІРЅРµРµ\n"
            "вЂ” СЃР»РёРІР°СЋС‚ Р±Р°РЅРє\n\n"
            "вљЎпёЏ РџРѕР»РЅС‹Р№ РґРѕСЃС‚СѓРї РЅСѓР¶РµРЅ,\n"
            "С‡С‚РѕР±С‹ Р·Р°С„РёРєСЃРёСЂРѕРІР°С‚СЊ Рё РјР°СЃС€С‚Р°Р±РёСЂРѕРІР°С‚СЊ СЂРµР·СѓР»СЊС‚Р°С‚\n\n"
            "рџ‘‡ РќРµ РѕСЃС‚Р°РЅР°РІР»РёРІР°Р№СЃСЏ РЅР° СЌС‚РѕРј"
        )

    if profit < 0:
        return (trial_ended_prefix + "рџљ« Р›С–РјС–С‚ РґРѕСЃСЏРіРЅСѓС‚Рѕ\n\n"
            "рџ“Љ Р—Р° С†РµР№ С‡Р°СЃ:\n"
            f"рџ’° РџСЂРёР±СѓС‚РѕРє: {profit}\n"
            f"рџ“€ ROI: {roi}%\n"
            f"рџЋЇ Winrate: {win_rate}%\n"
            f"рџ“Љ РЎРµСЂРµРґРЅС–Р№ РєРѕРµС„С–С†С–С”РЅС‚: {avg_odds}\n\n"
            "вќ—пёЏ Р† С†Рµ С‚С–Р»СЊРєРё РїРѕС‡Р°С‚РѕРє.\n\n"
            "Р‘РµР· СЃС‚Р°С‚РёСЃС‚РёРєРё С‚Рё Р±СѓРґРµС€ РїРѕРІС‚РѕСЂСЋРІР°С‚Рё С‚С– Р¶ РїРѕРјРёР»РєРё.\n\n"
            "вљЎпёЏ РџРѕРІРЅРёР№ РґРѕСЃС‚СѓРї РІС–РґРєСЂРёС”:\n"
            "вЂ” РІСЃСЋ СЃС‚Р°С‚РёСЃС‚РёРєСѓ\n"
            "вЂ” Р°РЅР°Р»С–Р· СЃС‚Р°РІРѕРє\n"
            "вЂ” РєРѕРЅС‚СЂРѕР»СЊ СЂРµР·СѓР»СЊС‚Р°С‚С–РІ\n\n"
            "рџ‘‡ РќРµ Р·Р°Р»РёС€Р°Р№ С†Рµ РїСЂРѕСЃС‚Рѕ С‚Р°Рє"
            if lang == "ua" else
            "рџљ« Р›РёРјРёС‚ РґРѕСЃС‚РёРіРЅСѓС‚\n\n"
            "рџ“Љ Р—Р° СЌС‚Рѕ РІСЂРµРјСЏ:\n"
            f"рџ’° РџСЂРёР±С‹Р»СЊ: {profit}\n"
            f"рџ“€ ROI: {roi}%\n"
            f"рџЋЇ Winrate: {win_rate}%\n"
            f"рџ“Љ РЎСЂРµРґРЅРёР№ РєРѕСЌС„С„РёС†РёРµРЅС‚: {avg_odds}\n\n"
            "вќ—пёЏ Р СЌС‚Рѕ С‚РѕР»СЊРєРѕ РЅР°С‡Р°Р»Рѕ.\n\n"
            "Р‘РµР· СЃС‚Р°С‚РёСЃС‚РёРєРё С‚С‹ Р±СѓРґРµС€СЊ РїРѕРІС‚РѕСЂСЏС‚СЊ С‚Рµ Р¶Рµ РѕС€РёР±РєРё.\n\n"
            "вљЎпёЏ РџРѕР»РЅС‹Р№ РґРѕСЃС‚СѓРї РѕС‚РєСЂРѕРµС‚:\n"
            "вЂ” РІСЃСЋ СЃС‚Р°С‚РёСЃС‚РёРєСѓ\n"
            "вЂ” Р°РЅР°Р»РёР· СЃС‚Р°РІРѕРє\n"
            "вЂ” РєРѕРЅС‚СЂРѕР»СЊ СЂРµР·СѓР»СЊС‚Р°С‚РѕРІ\n\n"
            "рџ‘‡ РќРµ РѕСЃС‚Р°РІР»СЏР№ СЌС‚Рѕ РїСЂРѕСЃС‚Рѕ С‚Р°Рє"
        )

    return (trial_ended_prefix + "рџљ« Р›С–РјС–С‚ РґРѕСЃСЏРіРЅСѓС‚Рѕ\n\n"
        "рџ“Љ Р—Р° С†РµР№ С‡Р°СЃ:\n"
        f"рџ’° РџСЂРёР±СѓС‚РѕРє: {profit}\n"
        f"рџ“€ ROI: {roi}%\n"
        f"рџЋЇ Winrate: {win_rate}%\n"
        f"рџ“Љ РЎРµСЂРµРґРЅС–Р№ РєРѕРµС„С–С†С–С”РЅС‚: {avg_odds}\n\n"
        "Р—Р°СЂР°Р· СЂРµР·СѓР»СЊС‚Р°С‚ РјР°Р№Р¶Рµ СЂС–РІРЅРёР№.\n"
        "РЎР°РјРµ РЅР° РґРёСЃС‚Р°РЅС†С–С— СЃС‚Р°РЅРµ РІРёРґРЅРѕ,\n"
        "С‡Рё РїСЂР°С†СЋС” С‚РІРѕСЏ СЃС‚СЂР°С‚РµРіС–СЏ.\n\n"
        "рџ‘‡ Р’С–РґРєСЂРёР№ РїРѕРІРЅРёР№ РґРѕСЃС‚СѓРї С– РїСЂРѕРґРѕРІР¶СѓР№ Р°РЅР°Р»С–Р·"
        if lang == "ua" else
        "рџљ« Р›РёРјРёС‚ РґРѕСЃС‚РёРіРЅСѓС‚\n\n"
        "рџ“Љ Р—Р° СЌС‚Рѕ РІСЂРµРјСЏ:\n"
        f"рџ’° РџСЂРёР±С‹Р»СЊ: {profit}\n"
        f"рџ“€ ROI: {roi}%\n"
        f"рџЋЇ Winrate: {win_rate}%\n"
        f"рџ“Љ РЎСЂРµРґРЅРёР№ РєРѕСЌС„С„РёС†РёРµРЅС‚: {avg_odds}\n\n"
        "РЎРµР№С‡Р°СЃ СЂРµР·СѓР»СЊС‚Р°С‚ РїРѕС‡С‚Рё СЂР°РІРЅС‹Р№.\n"
        "РРјРµРЅРЅРѕ РЅР° РґРёСЃС‚Р°РЅС†РёРё СЃС‚Р°РЅРµС‚ РІРёРґРЅРѕ,\n"
        "СЂР°Р±РѕС‚Р°РµС‚ Р»Рё С‚РІРѕСЏ СЃС‚СЂР°С‚РµРіРёСЏ.\n\n"
        "рџ‘‡ РћС‚РєСЂРѕР№ РїРѕР»РЅС‹Р№ РґРѕСЃС‚СѓРї Рё РїСЂРѕРґРѕР»Р¶Р°Р№ Р°РЅР°Р»РёР·"
    )


def _emotion_prompt_text(lang: str) -> str:
    if lang == "ua":
        return "РЇРє С‚Рё СЃРµР±Рµ РїРѕС‡СѓРІР°РІ РїРµСЂРµРґ С†С–С”СЋ СЃС‚Р°РІРєРѕСЋ?"
    if lang == "ru":
        return "РљР°Рє С‚С‹ СЃРµР±СЏ С‡СѓРІСЃС‚РІРѕРІР°Р» РїРµСЂРµРґ СЌС‚РѕР№ СЃС‚Р°РІРєРѕР№?"
    return "How did you feel before this bet?"


def _emotion_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("рџ¤ РўС–Р»С‚", callback_data="emotion_tilt")],
        [InlineKeyboardButton("рџ° РўСЂРёРІРѕРіР°", callback_data="emotion_anxiety")],
        [InlineKeyboardButton("рџЋ Р’РїРµРІРЅРµРЅРёР№", callback_data="emotion_confident")],
        [InlineKeyboardButton("рџ¤” РќРµР№С‚СЂР°Р»СЊРЅРѕ", callback_data="emotion_neutral")],
    ])


def _bet_saved_confirmation_text(lang: str, result: dict, remaining: int, daily_limit: int) -> str:
    if result["bet_result"] == "pending":
        return get_text(lang, "bet_pending_saved").format(
            stake_amount=result["stake_amount"],
            odds=result["odds"],
            bet_type=_bet_type_label(lang, result.get("bet_type"), result.get("bet_market")),
            remaining=remaining,
            limit=daily_limit,
        )

    return get_text(lang, "bet_saved").format(
        bet_result=_result_label(lang, result["bet_result"]),
        stake_amount=result["stake_amount"],
        odds=result["odds"],
        bet_type=_bet_type_label(lang, result.get("bet_type"), result.get("bet_market")),
        remaining=remaining,
        limit=daily_limit,
    )


async def emotion_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    user = get_user(user_id)
    lang = _normalize_lang(user["lang"] if user and user.get("lang") else "en")

    bet_id = context.user_data.get("last_bet_id")
    result = context.user_data.get("last_bet_result")
    daily_limit = context.user_data.get("last_bet_daily_limit")

    if not bet_id or not result or daily_limit is None:
        await query.message.reply_text(get_text(lang, "bet_parse_failed"))
        return

    emotion = query.data.removeprefix("emotion_")
    update_bet_emotion(bet_id, emotion)

    context.user_data.pop("last_bet_id", None)
    context.user_data.pop("last_bet_result", None)
    context.user_data.pop("last_bet_daily_limit", None)

    remaining = get_user_remaining_photos_today(user_id)

    await query.message.edit_reply_markup(None)
    await query.message.reply_text(
        _bet_saved_confirmation_text(lang, result, remaining, daily_limit)
    )


def _tilt_warning_keyboard(lang: str) -> InlineKeyboardMarkup:
    labels = {
        "ua": ("вњ… Р—СЂРѕР·СѓРјС–РІ, РїСЂРѕРґРѕРІР¶СѓСЋ", "рџ›‘ Р—СЂРѕР±РёС‚Рё РїР°СѓР·Сѓ"),
        "ru": ("вњ… РџРѕРЅСЏР», РїСЂРѕРґРѕР»Р¶Р°СЋ", "рџ›‘ РЎРґРµР»Р°С‚СЊ РїР°СѓР·Сѓ"),
        "en": ("вњ… Got it, continue", "рџ›‘ Take a break"),
    }
    continue_label, pause_label = labels.get(lang, labels["en"])
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(continue_label, callback_data="tilt_warning_ack")],
        [InlineKeyboardButton(pause_label, callback_data="tilt_warning_pause")],
    ])


def _tilt_warning_text(lang: str, signal_code: str, signal_context: dict) -> str:
    count = signal_context.get("count_last_60m", 0)
    hour = signal_context.get("hour", datetime.now().hour)

    if signal_code == "chasing_losses":
        if lang == "ua":
            return (
                "рџљЁ РЎС‚РѕРї-СЃРёРіРЅР°Р»!\n\n"
                "РћСЃС‚Р°РЅРЅС– 3 СЃС‚Р°РІРєРё  РїСЂРѕРіСЂР°С€. РЎС…РѕР¶Рµ РЅР° СЃРїСЂРѕР±Сѓ РІС–РґС–РіСЂР°С‚Рё.\n"
                "РЎС‚Р°С‚РёСЃС‚РёРєР°: РІ С‚Р°РєС–Р№ СЃРёС‚СѓР°С†С–С— Р±С–Р»СЊС€С–СЃС‚СЊ Р±РµС‚С‚РµСЂС–РІ РїСЂРѕРіСЂР°С” С‰Рµ Р±С–Р»СЊС€Рµ.\n\n"
                "Р РµРєРѕРјРµРЅРґСѓСЋ Р·СЂРѕР±РёС‚Рё РїР°СѓР·Сѓ 30 С…РІРёР»РёРЅ."
            )
        if lang == "ru":
            return (
                "рџљЁ РЎС‚РѕРї-СЃРёРіРЅР°Р»!\n\n"
                "РџРѕСЃР»РµРґРЅРёРµ 3 СЃС‚Р°РІРєРё  РїСЂРѕРёРіСЂС‹С€. РџРѕС…РѕР¶Рµ РЅР° РїРѕРїС‹С‚РєСѓ РѕС‚С‹РіСЂР°С‚СЊСЃСЏ.\n"
                "РЎС‚Р°С‚РёСЃС‚РёРєР°: РІ С‚Р°РєРѕР№ СЃРёС‚СѓР°С†РёРё Р±РѕР»СЊС€РёРЅСЃС‚РІРѕ Р±РµС‚С‚РµСЂРѕРІ РїСЂРѕРёРіСЂС‹РІР°РµС‚ РµС‰Рµ Р±РѕР»СЊС€Рµ.\n\n"
                "Р РµРєРѕРјРµРЅРґСѓСЋ СЃРґРµР»Р°С‚СЊ РїР°СѓР·Сѓ 30 РјРёРЅСѓС‚."
            )
        return (
            "рџљЁ Stop signal!\n\n"
            "Your last 3 bets were losses. This looks like chasing losses.\n"
            "Statistics show that in this situation most bettors lose even more.\n\n"
            "I recommend taking a 30-minute break."
        )

    if signal_code == "rapid_betting":
        if lang == "ua":
            return (
                "вљ пёЏ РЈРІР°РіР°!\n\n"
                f"РўРё РїРѕСЃС‚Р°РІРёРІ {count} СЃС‚Р°РІРєРё Р·Р° РѕСЃС‚Р°РЅРЅСЋ РіРѕРґРёРЅСѓ.\n"
                "РЁРІРёРґРєРµ Р±РµС‚С‚С–РЅРіСѓРІР°РЅРЅСЏ Р·РЅРёР¶СѓС” СЏРєС–СЃС‚СЊ СЂС–С€РµРЅСЊ.\n\n"
                "РЎРїРѕРІС–Р»СЊРЅРёСЃСЊ."
            )
        if lang == "ru":
            return (
                "вљ пёЏ Р’РЅРёРјР°РЅРёРµ!\n\n"
                f"РўС‹ СЃРґРµР»Р°Р» {count} СЃС‚Р°РІРєРё Р·Р° РїРѕСЃР»РµРґРЅРёР№ С‡Р°СЃ.\n"
                "Р‘С‹СЃС‚СЂС‹Р№ Р±РµС‚С‚РёРЅРі СЃРЅРёР¶Р°РµС‚ РєР°С‡РµСЃС‚РІРѕ СЂРµС€РµРЅРёР№.\n\n"
                "РџСЂРёС‚РѕСЂРјРѕР·Рё."
            )
        return (
            "вљ пёЏ Warning!\n\n"
            f"You placed {count} bets in the last hour.\n"
            "Rapid betting lowers decision quality.\n\n"
            "Slow down."
        )

    if lang == "ua":
        return (
            "рџЊ™ РџС–Р·РЅС–Р№ С‡Р°СЃ.\n\n"
            f"Р’Р¶Рµ {hour}:00. РўРІС–Р№ winrate РїС–СЃР»СЏ 23:00 Р·Р°Р·РІРёС‡Р°Р№ РЅРёР¶С‡РёР№.\n"
            "РџРѕРґСѓРјР°Р№ РґРІС–С‡С– РїРµСЂРµРґ РЅР°СЃС‚СѓРїРЅРѕСЋ СЃС‚Р°РІРєРѕСЋ."
        )
    if lang == "ru":
        return (
            "рџЊ™ РџРѕР·РґРЅРµРµ РІСЂРµРјСЏ.\n\n"
            f"РЈР¶Рµ {hour}:00. РўРІРѕР№ winrate РїРѕСЃР»Рµ 23:00 РѕР±С‹С‡РЅРѕ РЅРёР¶Рµ.\n"
            "РџРѕРґСѓРјР°Р№ РґРІР°Р¶РґС‹ РїРµСЂРµРґ СЃР»РµРґСѓСЋС‰РµР№ СЃС‚Р°РІРєРѕР№."
        )
    return (
        "рџЊ™ Late hour.\n\n"
        f"It is already {hour}:00. Your win rate after 23:00 is usually lower.\n"
        "Think twice before the next bet."
    )


def _tilt_break_text(lang: str) -> str:
    if lang == "ua":
        return "Р“Р°СЂРЅРµ СЂС–С€РµРЅРЅСЏ! РџРѕР±Р°С‡РёРјРѕСЃСЊ С‡РµСЂРµР· 30 С…РІРёР»РёРЅ рџ’Є"
    if lang == "ru":
        return "РҐРѕСЂРѕС€РµРµ СЂРµС€РµРЅРёРµ! РЈРІРёРґРёРјСЃСЏ С‡РµСЂРµР· 30 РјРёРЅСѓС‚ рџ’Є"
    return "Good call! See you in 30 minutes рџ’Є"


async def tilt_warning_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    user = get_user(user_id)
    lang = _normalize_lang(user["lang"] if user and user.get("lang") else "en")

    await query.message.edit_reply_markup(None)

    if query.data == "tilt_warning_pause":
        await query.message.reply_text(_tilt_break_text(lang))


async def process_bet_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("awaiting_ai_match_analysis"):
        await handle_ai_analysis_input(update, context)
        return

    if not update.message or not update.message.photo:
        return

    user_id = update.effective_user.id
    user = get_user(user_id)
    lang = _normalize_lang(user["lang"] if user and user.get("lang") else "en")
    plan = ((user.get("plan") if user else None) or "basic").lower()

    has_access = user_has_access(user_id)
    trial_started = get_trial_start(user_id) is not None
    is_trial_exhausted = (not has_access) and trial_started and not is_trial_available(user_id)
    in_trial = (not has_access) and is_trial_available(user_id) and get_trial_start(user_id) is not None

    if is_trial_exhausted:
        await update.message.reply_text(
            _daily_limit_reached_text(lang, "trial", TRIAL_SCREEN_LIMIT),
            reply_markup=access_keyboard(lang)
        )
        return

    if not has_access and not in_trial:
        no_access_text = (
            "в›” РЈ С‚РµР±Рµ РЅРµРјР°С” Р°РєС‚РёРІРЅРѕРіРѕ РґРѕСЃС‚СѓРїСѓ.\n\nРЎРїРѕС‡Р°С‚РєСѓ РЅР°С‚РёСЃРЅРё В«РЎРїСЂРѕР±СѓРІР°С‚РёВ» Р°Р±Рѕ РѕС„РѕСЂРјРё РїС–РґРїРёСЃРєСѓ."
            if lang == "ua" else
            "в›” РЈ С‚РµР±СЏ РЅРµС‚ Р°РєС‚РёРІРЅРѕРіРѕ РґРѕСЃС‚СѓРїР°.\n\nРЎРЅР°С‡Р°Р»Р° РЅР°Р¶РјРё В«РџРѕРїСЂРѕР±РѕРІР°С‚СЊВ» РёР»Рё РѕС„РѕСЂРјРё РїРѕРґРїРёСЃРєСѓ."
            if lang == "ru" else
            "в›” You do not have active access.\n\nPress вЂњTryвЂќ first or buy a subscription."
        )
        await update.message.reply_text(no_access_text, reply_markup=welcome_offer_keyboard(lang))
        return

    if has_access:
        daily_limit = get_user_daily_limit(user_id)
        used_today = count_user_photos_today(user_id)

        if used_today >= daily_limit:
            await update.message.reply_text(
                _daily_limit_reached_text(lang, plan, daily_limit),
                reply_markup=access_keyboard(lang) if plan == "basic" else None
            )
            return

    photo = update.message.photo[-1]
    file_id = photo.file_id

    if has_access:
        log_user_photo(user_id, file_id)
    else:
        increment_trial_usage(user_id)

    await update.message.reply_text(get_text(lang, "bet_analysis_started"))

    tg_file = await photo.get_file()
    image_bytes = await tg_file.download_as_bytearray()

    result = analyze_basic_bet_screenshot(bytes(image_bytes))

    if result["ok"]:
        bet_id = create_bet(
            user_id=user_id,
            photo_file_id=file_id,
            stake_amount=result["stake_amount"],
            odds=result["odds"],
            bet_result=result["bet_result"],
            currency=result["currency"],
            parse_status="parsed",
            raw_json=result.get("raw_json"),
            bet_type=result.get("bet_type"),
            bet_subtype=result.get("bet_subtype"),
            bet_market=result.get("bet_market"),
            is_trial=not has_access,
        )

        if has_access:
            signal_context = get_tilt_signal_context(user_id)
            signals = signal_context["signals"]

            context.user_data["last_bet_id"] = bet_id
            context.user_data["last_bet_result"] = result
            context.user_data["last_bet_daily_limit"] = daily_limit

            for signal_code in signals:
                await update.message.reply_text(
                    _tilt_warning_text(lang, signal_code, signal_context),
                    reply_markup=_tilt_warning_keyboard(lang),
                )

            await update.message.reply_text(
                _emotion_prompt_text(lang),
                reply_markup=_emotion_keyboard(),
            )
            return

        remaining_trial = get_trial_remaining(user_id)
        used_trial = 3 - remaining_trial

        await update.message.reply_text(_trial_progress_text(lang, used_trial, remaining_trial))

        if used_trial >= 2:
            trial_start = get_trial_start(user_id)
            start_dt = trial_start or datetime.now()
            end_dt = datetime.now()

            stats = get_basic_stats_between(user_id, start_dt, end_dt, include_trial=True)
            trial_pitch = _build_trial_pitch(lang, stats, used_trial)
            if trial_pitch:
                await update.message.reply_text(trial_pitch)

    else:
        create_bet(
            user_id=user_id,
            photo_file_id=file_id,
            stake_amount=None,
            odds=None,
            bet_result=None,
            currency="UAH",
            parse_status="failed",
            raw_json={"raw_text": result.get("raw_text")} if result.get("raw_text") else None,
            extraction_error=result.get("error"),
            is_trial=not has_access,
        )

        if has_access:
            debug_error = result.get("error", "unknown error")
            await update.message.reply_text(
                f"{get_text(lang, 'bet_parse_failed')}\n\nDEBUG: {debug_error}"
            )
            return

        remaining_trial = get_trial_remaining(user_id)
        used_trial = 3 - remaining_trial

        await update.message.reply_text(_trial_fail_text(lang, used_trial, remaining_trial))

        if used_trial >= 2:
            trial_start = get_trial_start(user_id)
            start_dt = trial_start or datetime.now()
            end_dt = datetime.now()

            stats = get_basic_stats_between(user_id, start_dt, end_dt, include_trial=True)
            trial_pitch = _build_trial_pitch(lang, stats, used_trial)
            if trial_pitch:
                await update.message.reply_text(trial_pitch)

    if not has_access and get_trial_remaining(user_id) == 0:
        trial_start = get_trial_start(user_id)
        start_dt = trial_start or datetime.now()
        end_dt = datetime.now()

        stats = get_basic_stats_between(user_id, start_dt, end_dt, include_trial=True)

        await update.message.reply_text(
            _build_limit_pitch(lang, stats),
            reply_markup=access_keyboard(lang)
        )



