# -*- coding: utf-8 -*-
from keyboards import tools_keyboard
from db import get_basic_bet_day_subscribers, get_vip_bet_day_subscribers

async def send_day_bet(bot, text, lang, audience):
    if audience == "basic":
        users = get_basic_bet_day_subscribers()
    elif audience == "vip":
        users = get_vip_bet_day_subscribers()
    else:
        return 0, 0

    sent = 0
    errors = 0

    for user in users:
        user_lang = user.get("lang", "en")

        if lang != "alllangs" and user_lang != lang:
            continue

        try:
            await bot.send_message(user["user_id"], text)
            sent += 1
        except:
            errors += 1

    return sent, errors


def get_tools_menu(lang: str, user_has_any_access: bool):
    if lang == "ru":
        text = (
            "🛠 Инструменты\n\n"
            "Здесь собраны дополнительные разделы платформы.\n"
            "Открывай нужный инструмент ниже."
        )
    elif lang == "en":
        text = (
            "🛠 Tools\n\n"
            "Additional platform sections are collected here.\n"
            "Open the tool you need below."
        )
    else:
        text = (
            "🛠 Інструменти\n\n"
            "Тут зібрані додаткові розділи платформи.\n"
            "Відкривай потрібний інструмент нижче."
        )

    if not user_has_any_access:
        if lang == "ru":
            text += "\n\n⚠️ Некоторые инструменты открываются только после активации подписки."
        elif lang == "en":
            text += "\n\n⚠️ Some tools unlock only after activating a subscription."
        else:
            text += "\n\n⚠️ Частина інструментів відкривається лише після активації підписки."

    return text, tools_keyboard(lang)
