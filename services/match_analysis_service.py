# -*- coding: utf-8 -*-
import base64
import logging

from openai import OpenAI

from config import OPENAI_API_KEY, OPENAI_MODEL_ANALYSIS


client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None


def _lang_name(lang: str) -> str:
    lang = (lang or "ua").lower()
    if lang.startswith("ru"):
        return "Russian"
    if lang.startswith("en"):
        return "English"
    return "Ukrainian"


def _structured_system_prompt(language: str) -> str:
    return f"""You are a professional sports betting analyst for a Telegram decision-support tool.

Write the full answer in {language}. Plain text only. No markdown tables, no JSON.

You MUST use web_search for real current match data for every paid or trial user. Functionality is identical for Basic and VIP.
Do a MAXIMUM of 2 web search queries per analysis. First plan exactly what to search, then execute no more than 2 searches.

Never invent statistics, injuries, form, lineups, odds, probabilities, or H2H. If data is missing, say so clearly in risks and recommend WAIT.
If the match is finished, say the match is finished and analysis no longer makes sense.

Decision rules:
- Every recommendation must include confidence as X/10, never a guarantee.
- Value-bet is allowed ONLY when estimated edge is at least 5 percentage points.
- If edge is below 5 percentage points, hide the value-bet block and set decision to SKIP.
- If there is too little reliable data, set decision to WAIT and do not create fake numbers.
- Use bookmaker implied probability = 1 / odds * 100 when odds are visible.

Use this strict structure, translated naturally into {language}:

[status: 🔴 LIVE / 📅 PRE-MATCH / 🏁 FINISHED]

 Матч: <teams> | 🏆 <league> | 🕐 <time/status>

🔍 FOUND DATA (real, from search):
 Form A (5 matches): <WWDLW or "not found">
 Form B (5 matches): <...>
 H2H: <...>
 Key: <injuries / motivation / lineup / other>

📊 MARKET EVALUATION:
 Result: Home <X/10> | Draw <X/10> | Away <X/10>
 Total: projection ~<N>, line <if visible>, evaluation <Over/Under/avoid>

🎯 DECISION: <BET / SKIP / WAIT>
<1-2 sentences with the main reason, based on found data>

If and only if DECISION = BET and edge >= 5 percentage points, include:

💎 IF BETTING - value bet:
 Market: <specific> | Odds: <number> | Confidence: <X/10>
 Bookmaker implies: <implied %> | Real estimate: <%> | Edge: <+Z%>

 RISKS: <2-3 concrete risks from data>
🚫 AVOID: <worst market + reason>
"""


def _system_prompt(lang: str) -> str:
    language = _lang_name(lang)
    return _structured_system_prompt(language)


def analyze_match_screenshot(image_bytes: bytes, lang: str = "ua") -> dict:
    if not OPENAI_API_KEY or not client:
        return {"ok": False, "error": "OPENAI_API_KEY is missing"}

    try:
        image_b64 = base64.b64encode(image_bytes).decode("utf-8")

        response = client.responses.create(
            model=OPENAI_MODEL_ANALYSIS,
            input=[
                {
                    "role": "system",
                    "content": [{"type": "input_text", "text": _system_prompt(lang)}],
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": (
                                "Analyze this event screenshot from a bookmaker or analytics site. "
                                "Extract teams or players, league, market, odds, match time/status and visible context. "
                                "Then use web search with a maximum of 2 queries to find real current statistics, form, H2H, injuries, motivation or live data. "
                                "Build the analysis on the found data. Never invent statistics. "
                                "If you cannot find reliable data, say so in risks and recommend WAIT."
                            ),
                        },
                        {
                            "type": "input_image",
                            "image_url": f"data:image/jpeg;base64,{image_b64}",
                            "detail": "high",
                        },
                    ],
                },
            ],
            tools=[{"type": "web_search"}],
            max_output_tokens=2500,
        )

        text = (response.output_text or "").strip()
        if not text:
            return {"ok": False, "error": "Empty AI response"}
        return {"ok": True, "report_text": text}
    except Exception as e:
        logging.error(f"Match analysis failed: {e}", exc_info=True)
        return {"ok": False, "error": str(e)}


def analyze_match_text(user_text: str, lang: str = "ua") -> dict:
    if not OPENAI_API_KEY or not client:
        return {"ok": False, "error": "OPENAI_API_KEY is missing"}

    try:
        response = client.responses.create(
            model=OPENAI_MODEL_ANALYSIS,
            input=[
                {
                    "role": "system",
                    "content": [{"type": "input_text", "text": _system_prompt(lang)}],
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": (
                                "The user provided match details as text. Extract teams or players, league, market, odds, match time/status and visible context. "
                                "Then use web search with a maximum of 2 queries to find real current statistics, form, H2H, injuries, motivation or live data. "
                                "Build the analysis on the found data. Never invent statistics. "
                                "If you cannot find reliable data, say so in risks and recommend WAIT.\n\n"
                                f"USER_TEXT: {user_text}"
                            ),
                        }
                    ],
                },
            ],
            tools=[{"type": "web_search"}],
            max_output_tokens=2500,
        )

        text = (response.output_text or "").strip()
        if not text:
            return {"ok": False, "error": "Empty AI response"}
        return {"ok": True, "report_text": text}
    except Exception as e:
        logging.error(f"Match analysis failed: {e}", exc_info=True)
        return {"ok": False, "error": str(e)}
