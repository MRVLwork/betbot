# -*- coding: utf-8 -*-
import base64
import json
import logging
import re
from datetime import datetime, timedelta

from openai import AsyncOpenAI, OpenAI
from config import OPENAI_API_KEY, OPENAI_MODEL_BASIC
from db import get_ai_daily_remaining, increment_ai_daily_usage


client = OpenAI(api_key=OPENAI_API_KEY)
async_client = AsyncOpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None


VIP_PLAN_ALIASES = {
    "vip",
    "vip_signals",
    "stars_vip",
    "stars_vip_month",
    "stars_vip_signals_10d",
    "usdt_vip",
    "usdt_vip_month",
    "usdt_vip_signals_10d",
}


def is_vip(plan: str | None) -> bool:
    return (plan or "").strip().lower() in VIP_PLAN_ALIASES


def _to_float(value: str | None):
    if not value:
        return None

    cleaned = value.strip().replace(" ", "").replace(",", ".")
    try:
        return float(cleaned)
    except Exception:
        return None


def _extract_line(text: str, key: str) -> str | None:
    pattern = rf"{key}\s*=\s*(.+)"
    match = re.search(pattern, text, re.IGNORECASE)
    if not match:
        return None
    return match.group(1).strip()


def _normalize_text(value: str | None) -> str:
    return (value or "").strip().lower()


def _detect_market_from_text(text: str, bet_type: str) -> str:
    t = _normalize_text(text)

    if any(x in t for x in ["кутов", "corners", "corner"]):
        return "corners"
    if any(x in t for x in ["картк", "cards", "yellow cards", "жовт"]):
        return "cards"
    if any(x in t for x in ["обидві заб", "обе заб", "both teams to score", "btts"]):
        return "btts"
    if any(x in t for x in ["фора", "handicap", "азиат", "asian handicap"]):
        return "handicap"
    if any(x in t for x in ["1x", "x2", "12", "double chance", "двійний шанс", "подвійний шанс"]):
        return "double_chance"
    if any(x in t for x in ["тотал", "total", "over", "under", "більше", "менше"]):
        return "total"

    if bet_type == "result":
        return "1x2"
    return "other"


def _detect_type_from_text(text: str) -> str:
    t = _normalize_text(text)
    if any(x in t for x in ["тотал", "total", "over", "under", "більше", "менше"]):
        return "total"
    return "result"


def _detect_subtype_from_text(text: str, bet_type: str, bet_market: str) -> str:
    t = _normalize_text(text)

    if bet_type == "total":
        if any(x in t for x in ["більше", "over", "тб"]):
            return "tb"
        if any(x in t for x in ["менше", "under", "тм"]):
            return "tm"
        return "other"

    if bet_market == "double_chance":
        return "double_chance"
    if bet_market == "handicap":
        return "handicap"
    if any(x in t for x in ["прохід", "qualification", "qualify"]):
        return "qualification"
    if any(x in t for x in ["нічия", "draw"]):
        return "draw"
    if bet_market == "btts":
        if any(x in t for x in ["так", "yes"]):
            return "yes"
        if any(x in t for x in ["ні", "no"]):
            return "no"
    if any(x in t for x in ["п1", "п2", "перемога", "win", "home", "away", "1 ", " 2"]):
        return "win"
    return "other"


def analyze_basic_bet_screenshot(image_bytes: bytes) -> dict:
    """
    Аналізує скрін ставки для Basic-підписки.
    Повертає:
    - bet_result: win / lose / refund / pending
    - stake_amount
    - odds
    - currency
    - bet_type: total / result
    - bet_market: 1x2 / total / btts / handicap / double_chance / corners / cards / other
    - bet_subtype: tb / tm / win / draw / yes / no / double_chance / handicap / qualification / other
    """

    if not OPENAI_API_KEY:
        return {"ok": False, "error": "OPENAI_API_KEY is missing"}

    try:
        image_b64 = base64.b64encode(image_bytes).decode("utf-8")

        response = client.responses.create(
            model=OPENAI_MODEL_BASIC,
            input=[
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "input_text",
                            "text": (
                                "You analyze a screenshot of a sports bet. "
                                "Return only 7 lines in exactly this format:\n"
                                "RESULT=win|lose|refund|pending\n"
                                "STAKE=<number>\n"
                                "ODDS=<decimal number>\n"
                                "CURRENCY=UAH|USD|EUR\n"
                                "BET_TYPE=total|result\n"
                                "BET_MARKET=1x2|total|btts|handicap|double_chance|corners|cards|other\n"
                                "BET_SUBTYPE=tb|tm|win|draw|yes|no|double_chance|handicap|qualification|other\n\n"
                                "Classification rules:\n"
                                "- If the bet is not settled yet, match is not finished, there is no final payout/result, "
                                "or the screenshot shows potential payout / possible win instead of actual settled payout, then RESULT=pending\n"
                                "- If the bet is on total over/under (ТБ, ТМ, Over, Under, individual total), BET_TYPE=total and BET_MARKET=total\n"
                                "- If the bet is on corners totals, BET_MARKET=corners\n"
                                "- If the bet is on cards totals, BET_MARKET=cards\n"
                                "- If the bet is on both teams to score / обидві заб'ють, BET_MARKET=btts\n"
                                "- If the bet is on handicap / фора, BET_MARKET=handicap\n"
                                "- If the bet is on 1X / X2 / 12 / double chance, BET_MARKET=double_chance\n"
                                "- If the bet is on who wins / draw / 1X2 market, BET_MARKET=1x2\n"
                                "- For totals: ТБ/Over/Більше -> BET_SUBTYPE=tb, ТМ/Under/Менше -> BET_SUBTYPE=tm\n"
                                "- For BTTS: yes -> BET_SUBTYPE=yes, no -> BET_SUBTYPE=no\n"
                                "- For 1X2 and winner-like bets: win / P1 / P2 / перемога -> BET_SUBTYPE=win\n"
                                "- For draw / нічия / X -> BET_SUBTYPE=draw\n"
                                "- For 1X / X2 / 12 -> BET_SUBTYPE=double_chance\n"
                                "- For фора / handicap -> BET_SUBTYPE=handicap\n"
                                "- For прохід / qualify -> BET_SUBTYPE=qualification\n"
                                "- Use RESULT=lose only if the screenshot clearly shows the bet is settled and lost\n"
                                "- Use RESULT=refund only if the screenshot clearly shows refund/return\n"
                                "- Use RESULT=win only if the screenshot clearly shows the bet is settled and won\n"
                                "\n"
                                "CRITICALLY IMPORTANT - CashOut / Keshaut:\n"
                                "If the screenshot shows a button or text such as CashOut, Keshaut, Кешаут, Викуп, Sell "
                                "with a concrete amount, for example CashOut 940 UAH, this is NOT a loss and NOT a win.\n"
                                "CashOut is a partial return when the user took the bet before the match ended.\n"
                                "- If there is an active CashOut button but no clear sign that the user pressed/accepted it, "
                                "and the match is still running, return RESULT=pending. Do not count it as CashOut/refund.\n"
                                "- If there is a clear sign that CashOut was completed, such as Cashed Out, Викуплено, "
                                "Виплачено, paid out, accepted, changed settled status/color, return RESULT=refund.\n"
                                "- For completed CashOut, treat the CashOut amount as the returned payout. "
                                "The profit is payout minus stake, for example 940 - 1000 = -60 UAH.\n"
                                "- Example: CashOut 940.00 UAH while the match is still running and no accepted/completed marker "
                                "is visible -> RESULT=pending.\n"
                                "- Example: Cashed Out 940 UAH or Викуплено 940 -> RESULT=refund.\n"
                                "\n"
                                "- Return decimal odds only\n"
                                "- Return stake amount only\n"
                                "- No extra text, no markdown, no JSON"
                            )
                        }
                    ]
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": (
                                "Read this bet screenshot and return exactly:\n"
                                "RESULT=...\n"
                                "STAKE=...\n"
                                "ODDS=...\n"
                                "CURRENCY=...\n"
                                "BET_TYPE=...\n"
                                "BET_MARKET=...\n"
                                "BET_SUBTYPE=..."
                            )
                        },
                        {
                            "type": "input_image",
                            "image_url": f"data:image/jpeg;base64,{image_b64}",
                            "detail": "high"
                        }
                    ]
                }
            ],
            max_output_tokens=200
        )

        text = (response.output_text or "").strip()

        result = (_extract_line(text, "RESULT") or "").lower()
        stake_raw = _extract_line(text, "STAKE")
        odds_raw = _extract_line(text, "ODDS")
        currency = (_extract_line(text, "CURRENCY") or "UAH").upper()
        bet_type = (_extract_line(text, "BET_TYPE") or "").lower()
        bet_market = (_extract_line(text, "BET_MARKET") or "").lower()
        bet_subtype = (_extract_line(text, "BET_SUBTYPE") or "").lower()

        stake_amount = _to_float(stake_raw)
        odds = _to_float(odds_raw)

        valid_results = {"win", "lose", "refund", "pending"}
        valid_types = {"total", "result"}
        valid_markets = {"1x2", "total", "btts", "handicap", "double_chance", "corners", "cards", "other"}
        valid_subtypes = {"tb", "tm", "win", "draw", "yes", "no", "double_chance", "handicap", "qualification", "other"}

        if result not in valid_results:
            return {"ok": False, "error": f"Invalid RESULT: {result}", "raw_text": text}
        if stake_amount is None or stake_amount <= 0:
            return {"ok": False, "error": f"Invalid STAKE: {stake_raw}", "raw_text": text}
        if odds is None or odds <= 1:
            return {"ok": False, "error": f"Invalid ODDS: {odds_raw}", "raw_text": text}

        if bet_type not in valid_types:
            bet_type = _detect_type_from_text(text)
        if bet_market not in valid_markets:
            bet_market = _detect_market_from_text(text, bet_type)
        if bet_subtype not in valid_subtypes:
            bet_subtype = _detect_subtype_from_text(text, bet_type, bet_market)

        if bet_type not in valid_types:
            return {"ok": False, "error": f"Invalid BET_TYPE: {bet_type}", "raw_text": text}
        if bet_market not in valid_markets:
            bet_market = "other"
        if bet_subtype not in valid_subtypes:
            bet_subtype = "other"

        return {
            "ok": True,
            "bet_result": result,
            "stake_amount": round(stake_amount, 2),
            "odds": round(odds, 2),
            "currency": currency,
            "bet_type": bet_type,
            "bet_market": bet_market,
            "bet_subtype": bet_subtype,
            "raw_json": {
                "raw_text": text,
                "RESULT": result,
                "STAKE": stake_amount,
                "ODDS": odds,
                "CURRENCY": currency,
                "BET_TYPE": bet_type,
                "BET_MARKET": bet_market,
                "BET_SUBTYPE": bet_subtype
            }
        }

    except Exception as e:
        return {"ok": False, "error": str(e)}


COACH_TOOLS = [
    {
        "type": "function",
        "name": "tool_get_overall_stats",
        "description": "Get exact overall betting stats for the user for a period.",
        "parameters": {
            "type": "object",
            "properties": {
                "period": {
                    "type": "string",
                    "enum": ["all", "today", "current_month", "last_30_days"],
                    "description": "Use current_month when the user asks about this month.",
                }
            },
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "tool_get_last_bet",
        "description": "Get the user's latest saved bet.",
        "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
    },
    {
        "type": "function",
        "name": "tool_get_avg_odds",
        "description": "Get exact average odds and count, optionally filtered by bet type, market, sport, and period.",
        "parameters": {
            "type": "object",
            "properties": {
                "bet_type": {"type": "string", "description": "total/result or localized equivalent"},
                "bet_market": {"type": "string", "description": "1x2/total/btts/handicap/double_chance/corners/cards/other"},
                "sport": {"type": "string", "description": "Sport name if the user asks about a sport"},
                "period": {"type": "string", "enum": ["all", "today", "current_month", "last_30_days"]},
            },
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "tool_get_stats_by_sport",
        "description": "Get exact stats for bets matched to a sport in stored bet data.",
        "parameters": {
            "type": "object",
            "properties": {
                "sport": {"type": "string"},
                "period": {"type": "string", "enum": ["all", "today", "current_month", "last_30_days"]},
            },
            "required": ["sport"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "tool_get_bets_by_result",
        "description": "Get exact count and totals for bets with a specific result.",
        "parameters": {
            "type": "object",
            "properties": {
                "result": {"type": "string", "enum": ["win", "lose", "refund", "pending"]},
                "period": {"type": "string", "enum": ["all", "today", "current_month", "last_30_days"]},
            },
            "required": ["result"],
            "additionalProperties": False,
        },
    },
]


def _coach_no_access_text(lang: str) -> str:
    if lang.startswith("ru"):
        return "ColdMind AI Agent доступен только для VIP-подписки."
    if lang.startswith("ua"):
        return "ColdMind AI Agent доступний тільки для VIP-підписки."
    return "ColdMind AI Agent is available only for VIP users."


def _coach_service_error_text(lang: str) -> str:
    if lang.startswith("ru"):
        return "Не удалось получить ответ ColdMind AI Agent. Попробуй ещё раз."
    if lang.startswith("ua"):
        return "Не вдалося отримати відповідь ColdMind AI Agent. Спробуй ще раз."
    return "Failed to get a ColdMind AI Agent reply. Try again."


def _coach_low_data_text(lang: str) -> str:
    if lang.startswith("ru"):
        return "Добавь сначала несколько ставок, минимум 3, чтобы мне было что анализировать. После этого я смогу честно показать слабые места и точные цифры."
    if lang.startswith("ua"):
        return "Додай спершу кілька ставок, мінімум 3, щоб я мав що аналізувати. Після цього я зможу чесно показати слабкі місця й точні цифри."
    return "Add a few bets first, at least 3, so I have enough data to analyze. Then I can show weak spots and exact numbers honestly."


def _coach_limit_text(lang: str) -> str:
    if lang.startswith("ru"):
        return "Лимит AI запросов на сегодня исчерпан."
    if lang.startswith("ua"):
        return "Ліміт AI запитів на сьогодні вичерпано."
    return "Your AI daily limit has been reached for today."


def _coach_system_prompt(lang: str) -> str:
    return f"""Ти ColdMind AI Agent, персональний AI-агент з беттингу.
Мова відповіді: {lang}. Відповідай мовою юзера: ua/ru/en.

У тебе є інструменти для отримання точних даних про ставки юзера.
Коли питають про статистику, останню ставку, середній коефіцієнт, спорт, результат, прибуток, ROI, типи ставок або місяць - ЗАВЖДИ виклич відповідний інструмент.

ЖОРСТКО:
- НІКОЛИ не називай числа, яких не отримав з інструменту.
- Якщо інструмент повернув порожньо або даних немає - чесно скажи про це.
- Не рахуй сам і не вигадуй.
- Тільки беттинг, статистика, дисципліна. Ніяких прогнозів на майбутні матчі.
- Максимум 200 слів.

Дозволені формати відповідей: конкретна цифра з поясненням, зріз, коротка порада на основі отриманих даних.
Якщо користувач питає "цього місяця", передавай period="current_month".
Для складених питань можна зробити кілька послідовних викликів, але не більше 3 tool-викликів.
"""


def _extract_response_tool_calls(response) -> list[dict]:
    calls = []
    for item in getattr(response, "output", []) or []:
        if getattr(item, "type", None) != "function_call":
            continue
        calls.append({
            "call_id": getattr(item, "call_id", None),
            "name": getattr(item, "name", None),
            "arguments": getattr(item, "arguments", "{}") or "{}",
        })
    return [call for call in calls if call["call_id"] and call["name"]]


def _execute_coach_tool(user_id: int, name: str, arguments: str) -> dict:
    from bets_db import (
        tool_get_avg_odds,
        tool_get_bets_by_result,
        tool_get_last_bet,
        tool_get_overall_stats,
        tool_get_stats_by_sport,
    )

    tool_map = {
        "tool_get_overall_stats": tool_get_overall_stats,
        "tool_get_last_bet": tool_get_last_bet,
        "tool_get_avg_odds": tool_get_avg_odds,
        "tool_get_stats_by_sport": tool_get_stats_by_sport,
        "tool_get_bets_by_result": tool_get_bets_by_result,
    }
    try:
        args = json.loads(arguments or "{}")
        if not isinstance(args, dict):
            args = {}
        func = tool_map.get(name)
        if not func:
            return {"ok": False, "error": "data_unavailable", "reason": "unknown_tool"}
        return func(user_id=user_id, **args)
    except Exception as e:
        logging.error(f"Coach tool failed: {name}: {e}", exc_info=True)
        return {"ok": False, "error": "data_unavailable"}


async def ai_coach_reply(user_id: int, user_message: str, lang: str, plan: str) -> str:
    """
    Personal ColdMind AI Agent. Uses tool-calls for exact betting stats and never injects
    calculated numbers directly into the prompt.
    """
    lang = (lang or "en").lower()
    plan = (plan or "basic").lower()

    if not is_vip(plan):
        return _coach_no_access_text(lang)

    if not OPENAI_API_KEY or not async_client:
        if lang.startswith("ru"):
            return "AI сервис временно недоступен."
        if lang.startswith("ua"):
            return "AI сервіс тимчасово недоступний."
        return "AI service is temporarily unavailable."

    remaining = get_ai_daily_remaining(user_id)
    if remaining <= 0:
        return _coach_limit_text(lang)

    try:
        from bets_db import tool_get_overall_stats

        overall = tool_get_overall_stats(user_id=user_id, period="all")
        if int(overall.get("total_bets") or 0) < 3:
            return _coach_low_data_text(lang)

        response = await async_client.responses.create(
            model=OPENAI_MODEL_BASIC,
            input=[
                {
                    "role": "system",
                    "content": [{"type": "input_text", "text": _coach_system_prompt(lang)}],
                },
                {
                    "role": "user",
                    "content": [{"type": "input_text", "text": user_message}],
                },
            ],
            tools=COACH_TOOLS,
            max_output_tokens=300,
        )

        executed_calls = 0
        tool_calls = _extract_response_tool_calls(response)

        while tool_calls and executed_calls < 3:
            outputs = []
            for call in tool_calls:
                if executed_calls >= 3:
                    result = {"ok": False, "error": "tool_limit_reached"}
                else:
                    result = _execute_coach_tool(user_id, call["name"], call["arguments"])
                    executed_calls += 1
                outputs.append({
                    "type": "function_call_output",
                    "call_id": call["call_id"],
                    "output": json.dumps(result, ensure_ascii=False),
                })

            response = await async_client.responses.create(
                model=OPENAI_MODEL_BASIC,
                previous_response_id=response.id,
                input=outputs,
                tools=COACH_TOOLS,
                max_output_tokens=300,
            )
            tool_calls = _extract_response_tool_calls(response)

        if tool_calls:
            logging.error("Coach stopped after tool call limit for user_id=%s", user_id)
            return _coach_service_error_text(lang)

        increment_ai_daily_usage(user_id)
        text = (response.output_text or "").strip()
        if text:
            return text
    except Exception as e:
        logging.error(f"Coach failed: {e}", exc_info=True)

    return _coach_service_error_text(lang)
