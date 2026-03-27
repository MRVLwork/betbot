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


def analyze_basic_bet_screenshot(image_bytes: bytes) -> dict:
    """
    Аналізує скрін ставки для Basic-підписки.
    Повертає:
    - bet_result: win / lose / refund / pending
    - stake_amount
    - odds
    - currency
    - bet_type: total / result
    - bet_subtype: tb / tm / win / draw / double_chance / handicap / qualification / other
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
                                "Return only 6 lines in exactly this format:\n"
                                "RESULT=win|lose|refund|pending\n"
                                "STAKE=<number>\n"
                                "ODDS=<decimal number>\n"
                                "CURRENCY=UAH|USD|EUR\n"
                                "BET_TYPE=total|result\n"
                                "BET_SUBTYPE=tb|tm|win|draw|double_chance|handicap|qualification|other\n\n"
                                "Classification rules:\n"
                                "- If the bet is not settled yet, match is not finished, there is no final payout/result, "
                                "or the screenshot shows potential payout / possible win instead of actual settled payout, then RESULT=pending\n"
                                "- If the bet is on total over/under (ТБ, ТМ, Over, Under), BET_TYPE=total\n"
                                "- For totals: ТБ/Over -> BET_SUBTYPE=tb, ТМ/Under -> BET_SUBTYPE=tm\n"
                                "- If the bet is on match result, 1X2, P1/P2, draw, double chance, handicap, qualification, BET_TYPE=result\n"
                                "- For result-like bets:\n"
                                "  * win / P1 / P2 / перемога -> BET_SUBTYPE=win\n"
                                "  * draw / нічия / X -> BET_SUBTYPE=draw\n"
                                "  * 1X / X2 / 12 -> BET_SUBTYPE=double_chance\n"
                                "  * фора / handicap -> BET_SUBTYPE=handicap\n"
                                "  * прохід / qualify -> BET_SUBTYPE=qualification\n"
                                "  * anything else in result markets -> BET_SUBTYPE=other\n"
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
            max_output_tokens=160
        )

        text = (response.output_text or "").strip()

        result = (_extract_line(text, "RESULT") or "").lower()
        stake_raw = _extract_line(text, "STAKE")
        odds_raw = _extract_line(text, "ODDS")
        currency = (_extract_line(text, "CURRENCY") or "UAH").upper()
        bet_type = (_extract_line(text, "BET_TYPE") or "").lower()
        bet_subtype = (_extract_line(text, "BET_SUBTYPE") or "").lower()

        stake_amount = _to_float(stake_raw)
        odds = _to_float(odds_raw)

        valid_results = {"win", "lose", "refund", "pending"}
        valid_types = {"total", "result"}
        valid_subtypes = {"tb", "tm", "win", "draw", "double_chance", "handicap", "qualification", "other"}

        if result not in valid_results:
            return {"ok": False, "error": f"Invalid RESULT: {result}", "raw_text": text}
        if stake_amount is None or stake_amount <= 0:
            return {"ok": False, "error": f"Invalid STAKE: {stake_raw}", "raw_text": text}
        if odds is None or odds <= 1:
            return {"ok": False, "error": f"Invalid ODDS: {odds_raw}", "raw_text": text}
        if bet_type not in valid_types:
            return {"ok": False, "error": f"Invalid BET_TYPE: {bet_type}", "raw_text": text}
        if bet_subtype not in valid_subtypes:
            return {"ok": False, "error": f"Invalid BET_SUBTYPE: {bet_subtype}", "raw_text": text}

        return {
            "ok": True,
            "bet_result": result,
            "stake_amount": round(stake_amount, 2),
            "odds": round(odds, 2),
            "currency": currency,
            "bet_type": bet_type,
            "bet_subtype": bet_subtype,
            "raw_json": {
                "raw_text": text,
                "RESULT": result,
                "STAKE": stake_amount,
                "ODDS": odds,
                "CURRENCY": currency,
                "BET_TYPE": bet_type,
                "BET_SUBTYPE": bet_subtype
            }
        }

    except Exception as e:
        return {"ok": False, "error": str(e)}
