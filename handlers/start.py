from telegram import Update
from telegram.ext import ContextTypes

from db import get_user, create_user_if_not_exists
from keyboards import welcome_offer_keyboard


def _welcome_text(lang: str) -> str:
    if lang == "ru":
        return """Привет 👋

❗️ Ты уверен, что не в минусе на ставках?

Большинство игроков **теряют деньги**, даже когда им кажется, что всё идёт нормально.

Почему так происходит:
— не считают реальную прибыль  
— не видят свой ROI  
— не замечают, какие ставки реально тянут вниз  
— играют по ощущениям, а не по цифрам  

📊 Bet Tracker Bot покажет правду о твоих ставках:
• прибыль или убыток 💰  
• ROI 📈  
• винрейт 🎯  
• средний коэффициент  
• серии выигрышей и проигрышей  

⚡️ Уже после нескольких ставок ты увидишь:
👉 ты реально в плюсе или тебе только так кажется  
👉 где именно теряешь деньги  
👉 есть ли у тебя система  

👇 Выбери, с чего начать:
"""
    else:
        return """Привіт 👋

❗️ Ти впевнений, що не в мінусі на ставках?

Більшість гравців **втрачають гроші**, навіть коли їм здається, що все йде нормально.

Чому так відбувається:
— не рахують реальний прибуток  
— не бачать свій ROI  
— не помічають, які ставки реально тягнуть вниз  
— грають на відчуттях, а не по цифрах  

📊 Bet Tracker Bot покаже правду про твої ставки:
• прибуток або збиток 💰  
• ROI 📈  
• винрейт 🎯  
• середній коефіцієнт  
• серії виграшів і програшів  

⚡️ Уже після кількох ставок ти побачиш:
👉 ти реально в плюсі чи лише так здається  
👉 де саме втрачаєш гроші  
👉 чи є у тебе система  

👇 Обери, з чого почати:
"""


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_lang = update.effective_user.language_code or "uk"

    create_user_if_not_exists(user_id, user_lang)

    user = get_user(user_id)
    lang = user["lang"] if user else "ua"

    text = _welcome_text(lang)

    await update.message.reply_text(
        text,
        reply_markup=welcome_offer_keyboard(lang)
    )
