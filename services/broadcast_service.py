# -*- coding: utf-8 -*-
import re
from typing import Tuple

from db import get_broadcast_recipients


LANG_TAGS = {"ua", "ru", "en", "alllangs"}
AUDIENCE_TAGS = {"trial", "basic", "vip", "all"}


def parse_broadcast_text(raw_text: str) -> Tuple[str, str, str]:
    """
    Expected formats:

    /sendpost
    Message text...

    /ua
    /vip

    or

    /sendpost Message text...

    /en
    /all
    """
    text = (raw_text or "").strip()
    if not text:
        return "", "alllangs", "all"

    text = re.sub(r"^/sendpost\b", "", text, flags=re.IGNORECASE).strip()

    lines = [line.rstrip() for line in text.splitlines()]
    lang_tag = "alllangs"
    audience_tag = "all"
    cleaned_lines = []

    for line in lines:
        stripped = line.strip()
        if re.fullmatch(r"/(ua|ru|en|alllangs)", stripped, flags=re.IGNORECASE):
            lang_tag = stripped[1:].lower()
            continue
        if re.fullmatch(r"/(trial|basic|vip|all)", stripped, flags=re.IGNORECASE):
            audience_tag = stripped[1:].lower()
            continue
        cleaned_lines.append(line)

    clean_text = "\n".join(cleaned_lines).strip()
    return clean_text, lang_tag, audience_tag


def broadcast_help_text() -> str:
    return (
        "Формат розсилки:\n\n"
        "/sendpost\n"
        "Текст повідомлення\n\n"
        "/ua\n"
        "/basic\n\n"
        "Мова:\n"
        "/ua /ru /en /alllangs\n\n"
        "Аудиторія:\n"
        "/trial /basic /vip /all\n\n"
        "Можна також надіслати фото з caption у такому ж форматі, "
        "починаючи caption з /sendpost"
    )


async def send_broadcast(bot, text: str, lang_tag: str = "alllangs", audience_tag: str = "all") -> tuple[int, int]:
    recipients = get_broadcast_recipients(lang_tag=lang_tag, audience_tag=audience_tag)

    sent = 0
    failed = 0

    for user_id in recipients:
        try:
            await bot.send_message(chat_id=user_id, text=text)
            sent += 1
        except Exception:
            failed += 1

    return sent, failed


async def send_photo_broadcast(bot, photo_file_id: str, caption: str, lang_tag: str = "alllangs", audience_tag: str = "all") -> tuple[int, int]:
    recipients = get_broadcast_recipients(lang_tag=lang_tag, audience_tag=audience_tag)

    sent = 0
    failed = 0

    for user_id in recipients:
        try:
            await bot.send_photo(chat_id=user_id, photo=photo_file_id, caption=caption or "")
            sent += 1
        except Exception:
            failed += 1

    return sent, failed
