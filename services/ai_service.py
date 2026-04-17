import base64
import re

from openai import OpenAI
from config import OPENAI_API_KEY, OPENAI_MODEL_BASIC


client = OpenAI(api_key=OPENAI_API_KEY)


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
