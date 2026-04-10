import re


LANG_TAGS = {"ua", "ru", "en", "alllangs"}
AUDIENCE_TAGS = {"trial", "basic", "vip", "all"}


def parse_segmented_post(raw_text: str):
    text = (raw_text or "").strip()
    text = re.sub(r"^/sendpost(?:@\w+)?", "", text, count=1).strip()

    lang_tag = None
    audience_tag = None
    content_lines = []

    for line in text.splitlines():
        stripped = line.strip()
        lowered = stripped.lower()

        if lowered.startswith("/") and lowered[1:] in LANG_TAGS:
            lang_tag = lowered[1:]
            continue

        if lowered.startswith("/") and lowered[1:] in AUDIENCE_TAGS:
            audience_tag = lowered[1:]
            continue

        content_lines.append(line)

    content = "\n".join(content_lines).strip()

    if not lang_tag:
        lang_tag = "alllangs"
    if not audience_tag:
        audience_tag = "all"

    return {
        "text": content,
        "lang_tag": lang_tag,
        "audience_tag": audience_tag,
    }


def is_sendpost_text(text: str) -> bool:
    return bool((text or "").strip().startswith("/sendpost"))
