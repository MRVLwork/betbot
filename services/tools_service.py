from keyboards import tools_keyboard


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
