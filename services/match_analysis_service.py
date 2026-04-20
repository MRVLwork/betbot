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

Your task: analyze ONLY the information that is visible on the screenshot or explicitly provided in the user's text. Do not invent hidden stats, injuries, or external data. Do not claim certainty or guaranteed wins.

Write the answer in {language}.
Use plain text only. Keep the structure EXACTLY as below, with the same sections and order:

🧠 AI Match Report

⚽ <match name or 'Матч не вдалося точно визначити'>
🏆 <league/tournament or 'Невідомо'>

📊 Загальна оцінка матчу:
<score from 1.0 to 10.0> / 10

🔥 Найсильніші сценарії:
1️⃣ <market> — <score>/10
Причина:
<short useful reason>

2️⃣ <market> — <score>/10
Причина:
<short useful reason>

3️⃣ <market> — <score>/10
Причина:
<short useful reason>

⚠️ Ризики:
— <risk 1>
— <risk 2>
— <risk 3>

🚫 Що краще не брати:
<one weak market/scenario with short comment>

📌 Висновок:
<2 short lines with the clearest takeaway for decision making>

Rules:
- Base the analysis on the visible screen structure: market direction, bookmaker odds, visible form icons, visible H2H tabs, visible tournament and match context.
- If the screenshot mainly shows totals, use totals in the top scenarios.
- If the screenshot mainly shows 1X2, BTTS, handicap, corners or cards, adapt to that.
- Give practical, decision-oriented reasons, not generic fluff.
- If information is limited, say so inside the reasons and risks.
- Never say a bet is guaranteed or certain.
- Never output markdown tables or JSON.
- Keep the full answer concise and readable.
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
            max_output_tokens=900,
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
            max_output_tokens=700,
        )

        text = (response.output_text or "").strip()
        if not text:
            return {"ok": False, "error": "Empty AI response"}
        return {"ok": True, "report_text": text}
    except Exception as e:
        return {"ok": False, "error": str(e)}
