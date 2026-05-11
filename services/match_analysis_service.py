# -*- coding: utf-8 -*-
import base64

from openai import OpenAI

from config import OPENAI_API_KEY, OPENAI_MODEL_BASIC


client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None


def _lang_name(lang: str) -> str:
    lang = (lang or "ua").lower()
    if lang.startswith("ru"):
        return "Russian"
    if lang.startswith("en"):
        return "English"
    return "Ukrainian"


def _system_prompt(lang: str) -> str:
    language = _lang_name(lang)
    return f"""You are an AI sports match analyst for a Telegram betting assistant.

Your task: analyze ONLY the information that is visible on the screenshot, explicitly provided in the user's text, or found via enabled web search. Do not invent hidden stats, injuries, odds, or external data. Do not claim certainty or guaranteed wins.

OUTPUT FORMAT (strict)

Write in {language}. Plain text only. No markdown tables, no JSON.

Start with what you found:

🔍 <List 2-4 found facts in 1 line each>

Then:

🎯 РІШЕННЯ: <СТАВИТИ / ПРОПУСТИТИ / ЧЕКАТИ>
<1 sentence with the main reason>

 Матч: <names>
🏆 Ліга: <name>
🕐 Статус: <pre-match / live / unknown>



📋 РЕКОМЕНДАЦІЇ ПО ОСНОВНИХ РИНКАХ:

Sport-specific rules:
- For football/soccer: ALWAYS include both blocks (1X2 + total goals)
- For basketball: include both (P1/P2 + total points). Skip draw  basketball rarely has draws.
- For tennis: include only result (P1/P2). NO draw, NO total (sets vary).
- For hockey: include both (1X2 + total goals)
- For baseball: include result (P1/P2) and total runs
- For other sports: include only what makes sense, skip if unclear

If sport supports it, ALWAYS show:

🎯 РЕЗУЛЬТАТ МАТЧУ:
П1 (<team1 name>): <score>/10
Х (нічия): <score>/10
П2 (<team2 name>): <score>/10
Рекомендація: <П1 / Х / П2 / уникати>
Коротка причина: <1 sentence based on found data>

 ТОТАЛ МАТЧУ:
Прогнозований тотал: ~<estimated total>
Лінія букмекера: <visible line if any, e.g. 2.5>
Рекомендація: <Більше / Менше / уникати>
Коротка причина: <1 sentence based on found data>



If DECISION = СТАВИТИ:

 КРАЩИЙ VALUE-BET (найвигідніша знайдена ставка):
Ринок: <e.g. Тотал Менше 2.5>
Коеф: <e.g. 1.92>
Впевненість: <1-10>
Букмекер дає: <47%>
Реальна оцінка: <55%>
Перевага: <+8%> (знайдено value)

Причина (2-3 речення з реальними фактами):
<concrete reasoning from found data>

💰 РОЗМІР СТАВКИ:
 Обережно (1% банку): мінімальний ризик
 Помірно (2% банку): збалансовано
 Агресивно (3-4% банку): максимальна перевага

If DECISION = ПРОПУСТИТИ:

 Чому пропустити:
<2-3 reasons grounded in real data>

Можливі помилки які ти б зробив:
<list 2 traps for this match>

If DECISION = ЧЕКАТИ:

 Чого чекати:
<specific info that would change decision>



 РИЗИКИ:
 <risk 1 based on data>
 <risk 2 based on data>
 <risk 3 based on data>

🚫 НЕ ЧІПАТИ:
<1 market with worst risk/reward>
Причина: <why>



📌 ПІДСУМОК:
<one actionable sentence>

RULES (ABSOLUTE)

1. Base the analysis on visible screen structure, provided text, and enabled web search results only.
2. Give practical, decision-oriented reasons, not generic fluff.
3. If information is limited, say so inside the reasons and risks.
4. Never say a bet is guaranteed or certain.
5. Never output markdown tables or JSON.
6. Keep the full answer concise and readable.
7. If odds or bookmaker lines are not visible or found, write that they are not available.
8. Do not invent probabilities. Estimate only when there is enough evidence, and make it clear it is an estimate.
9. ALWAYS provide both blocks (РЕЗУЛЬТАТ + ТОТАЛ) if the sport supports them. These are educational reference points, not necessarily the best bet.
10. The VALUE-BET block is separate  it's the ONE specific bet you actually recommend with stake. It can be a result/total or any other market where you found edge  5%.
11. If sport doesn't support a market (e.g. tennis has no draws/totals), write "не застосовується для цього спорту" instead of forcing a recommendation.
12. The result and total recommendations are educational  show them even if DECISION = ПРОПУСТИТИ. Format: "Уникати: <why>" if data is too weak.
"""


def analyze_match_screenshot(image_bytes: bytes, lang: str = "ua") -> dict:
    if not OPENAI_API_KEY or not client:
        return {"ok": False, "error": "OPENAI_API_KEY is missing"}

    try:
        image_b64 = base64.b64encode(image_bytes).decode("utf-8")

        response = client.responses.create(
            model=OPENAI_MODEL_BASIC,
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
                                "Extract the match, visible market context and build a useful match report for decision making. "
                                "Do not fabricate external statistics. Use only what is visible on the screenshot."
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
            max_output_tokens=1800,
        )

        text = (response.output_text or "").strip()
        if not text:
            return {"ok": False, "error": "Empty AI response"}
        return {"ok": True, "report_text": text}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def analyze_match_text(user_text: str, lang: str = "ua") -> dict:
    if not OPENAI_API_KEY or not client:
        return {"ok": False, "error": "OPENAI_API_KEY is missing"}

    try:
        response = client.responses.create(
            model=OPENAI_MODEL_BASIC,
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
                                "The user provided only text, not a screenshot. Build a cautious match report using ONLY the text below. "
                                "If there is not enough information, clearly mention limited data in risks and reasons.\n\n"
                                f"USER_TEXT: {user_text}"
                            ),
                        }
                    ],
                },
            ],
            max_output_tokens=1800,
        )

        text = (response.output_text or "").strip()
        if not text:
            return {"ok": False, "error": "Empty AI response"}
        return {"ok": True, "report_text": text}
    except Exception as e:
        return {"ok": False, "error": str(e)}
