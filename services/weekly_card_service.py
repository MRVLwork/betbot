# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from io import BytesIO
import os
import urllib.request

from PIL import Image, ImageDraw, ImageFont

from bets_db import get_full_stats_between
from db import get_conn


BG_COLOR = "#0E1A2E"
GREEN_COLOR = "#00E676"
RED_COLOR = "#FF5252"
TEXT_COLOR = "#FFFFFF"
SUBTEXT_COLOR = "#8899BB"
CARD_COLOR = "#152540"

FONTS_DIR = os.path.join(os.path.dirname(__file__), "..", "fonts")
FONT_REGULAR = os.path.join(FONTS_DIR, "DejaVuSans.ttf")
FONT_BOLD = os.path.join(FONTS_DIR, "DejaVuSans-Bold.ttf")

FONT_URLS = {
    "DejaVuSans.ttf": (
        "https://github.com/dejavu-fonts/dejavu-fonts/"
        "raw/master/ttf/DejaVuSans.ttf"
    ),
    "DejaVuSans-Bold.ttf": (
        "https://github.com/dejavu-fonts/dejavu-fonts/"
        "raw/master/ttf/DejaVuSans-Bold.ttf"
    ),
}


def _ensure_fonts_downloaded():
    """
    Завантажує шрифти якщо їх немає локально.
    Викликається один раз при імпорті модуля.
    """
    os.makedirs(FONTS_DIR, exist_ok=True)

    for font_name, url in FONT_URLS.items():
        font_path = os.path.join(FONTS_DIR, font_name)
        if not os.path.exists(font_path):
            try:
                print(f"Downloading font {font_name}...")
                urllib.request.urlretrieve(url, font_path)
                print(f"Font {font_name} downloaded OK")
            except Exception as e:
                print(f"Failed to download {font_name}: {e}")


try:
    _ensure_fonts_downloaded()
except Exception as e:
    print(f"Font setup error: {e}")


def _load_font(size: int, bold: bool = False):
    """
    Завантажує шрифт з підтримкою кирилиці.
    """
    font_name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"

    search_paths = [
        os.path.join(FONTS_DIR, font_name),
        os.path.join(os.path.dirname(__file__), "..", font_name),
        f"/usr/share/fonts/truetype/dejavu/{font_name}",
        f"/usr/share/fonts/dejavu/{font_name}",
        f"/run/current-system/sw/share/fonts/truetype/{font_name}",
    ]

    try:
        import glob

        nix_fonts = glob.glob(
            f"/nix/store/*/share/fonts/truetype/{font_name}"
        )
        search_paths.extend(nix_fonts)
    except Exception:
        pass

    for path in search_paths:
        try:
            if os.path.exists(path):
                return ImageFont.truetype(path, size=size)
        except (IOError, OSError):
            continue

    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def _format_roi(roi: float) -> str:
    if roi > 0:
        return f"+{roi}%"
    return f"{roi}%"


def _format_profit(value: float) -> str:
    if value > 0:
        return f"+{value}"
    return str(value)


def _week_range(now: datetime | None = None) -> tuple[datetime, datetime]:
    now = now or datetime.now()
    start_dt = (now - timedelta(days=now.weekday())).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    end_dt = min(now, start_dt + timedelta(days=7))
    return start_dt, end_dt


def get_week_stats(user_id: int) -> dict:
    start_dt, end_dt = _week_range()
    stats = get_full_stats_between(user_id, start_dt, end_dt)
    stats["start_dt"] = start_dt
    stats["end_dt"] = end_dt
    return stats


def get_user_rank_percentile(user_id: int) -> int:
    end_dt = datetime.now()
    start_dt = end_dt - timedelta(days=30)
    user_stats = get_full_stats_between(user_id, start_dt, end_dt)
    user_roi = float(user_stats.get("roi", 0) or 0)

    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT user_id
        FROM users
        WHERE is_active = 1
          AND access_until IS NOT NULL
          AND access_until > ?
    """,
        (end_dt.isoformat(),),
    )
    rows = cur.fetchall()
    conn.close()

    if not rows:
        return 0

    active_user_ids = [int(row["user_id"]) for row in rows]
    lower_count = 0

    for active_user_id in active_user_ids:
        stats = get_full_stats_between(active_user_id, start_dt, end_dt)
        roi = float(stats.get("roi", 0) or 0)
        if roi < user_roi:
            lower_count += 1

    return int(round((lower_count / len(active_user_ids)) * 100))


def generate_weekly_card(
    user_id: int,
    stats: dict,
    username: str,
    rank_percentile: int,
    lang: str = "ua",
) -> bytes:
    image = Image.new("RGB", (1080, 1080), BG_COLOR)
    draw = ImageDraw.Draw(image)

    title_font = _load_font(48, bold=True)
    subtitle_font = _load_font(28)
    hero_font = _load_font(148, bold=True)
    metric_title_font = _load_font(30)
    metric_value_font = _load_font(52, bold=True)
    footer_font = _load_font(34, bold=True)
    watermark_font = _load_font(24)

    start_dt = stats.get("start_dt") or _week_range()[0]
    end_dt = stats.get("end_dt") or _week_range()[1]
    date_range_text = f"{start_dt.strftime('%d.%m')} - {end_dt.strftime('%d.%m')}"
    safe_username = username or f"user_{user_id}"
    lang = (lang or "ua").lower()

    labels = (
        ["Winrate", "Прибуток", "Ставок", "Сер. коеф"]
        if lang == "ua"
        else ["Winrate", "Profit", "Bets", "Avg odds"]
    )

    draw.rounded_rectangle((60, 60, 1020, 260), radius=34, fill=CARD_COLOR)
    draw.text((100, 96), "ТВІЙ ТИЖДЕНЬ", font=title_font, fill=TEXT_COLOR)
    draw.text((100, 158), date_range_text, font=subtitle_font, fill=SUBTEXT_COLOR)
    draw.text((100, 200), f"@{safe_username}", font=subtitle_font, fill=SUBTEXT_COLOR)

    roi = round(float(stats.get("roi", 0) or 0), 2)
    roi_color = GREEN_COLOR if roi > 0 else RED_COLOR if roi < 0 else TEXT_COLOR
    draw.text((540, 330), _format_roi(roi), font=hero_font, fill=roi_color, anchor="ma")
    draw.text((540, 470), "ROI за тиждень", font=subtitle_font, fill=SUBTEXT_COLOR, anchor="ma")

    cards = [
        (labels[0], f"{round(float(stats.get('win_rate', 0) or 0), 2)}%"),
        (labels[1], _format_profit(round(float(stats.get("net_profit", 0) or 0), 2))),
        (labels[2], str(int(stats.get("total_bets", 0) or 0))),
        (labels[3], str(round(float(stats.get("avg_odds", 0) or 0), 2))),
    ]

    positions = [
        (80, 560, 500, 720),
        (580, 560, 1000, 720),
        (80, 760, 500, 920),
        (580, 760, 1000, 920),
    ]

    for (label, value), (x1, y1, x2, y2) in zip(cards, positions):
        draw.rounded_rectangle((x1, y1, x2, y2), radius=28, fill=CARD_COLOR)
        draw.text((x1 + 32, y1 + 28), label, font=metric_title_font, fill=SUBTEXT_COLOR)
        draw.text((x1 + 32, y1 + 82), value, font=metric_value_font, fill=TEXT_COLOR)

    draw.text(
        (540, 975),
        f"Ти в топ {rank_percentile}% беттерів",
        font=footer_font,
        fill=TEXT_COLOR,
        anchor="ma",
    )
    draw.text((540, 1025), "Bet Tracker Bot", font=watermark_font, fill=SUBTEXT_COLOR, anchor="ma")

    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer.getvalue()


def generate_profile_card(
    user_id: int,
    stats: dict,
    username: str,
    rank_percentile: int,
    xp_data: dict,
) -> bytes:
    image = Image.new("RGB", (1080, 1080), BG_COLOR)
    draw = ImageDraw.Draw(image)

    for y in range(0, 1080, 60):
        draw.line((0, y, 1080, y), fill="#0F1E30", width=1)

    title_font = _load_font(72, bold=True)
    big_font = _load_font(120, bold=True)
    medium_font = _load_font(52)
    small_font = _load_font(40)

    safe_username = username or f"user_{user_id}"
    roi = round(float(stats.get("roi", 0) or 0), 2)
    roi_str = f"+{roi}%" if roi > 0 else f"{roi}%"
    roi_color = GREEN_COLOR if roi > 0 else RED_COLOR if roi < 0 else TEXT_COLOR
    winrate = round(float(stats.get("win_rate", 0) or 0), 2)
    total_bets = int(stats.get("total_bets") or 0)
    level = int(xp_data.get("current_level") or 1)
    top_percent = max(1, 100 - int(rank_percentile or 0))

    draw.text((80, 80), "BET TRACKER", font=title_font, fill=GREEN_COLOR)
    draw.text((80, 170), safe_username, font=medium_font, fill=SUBTEXT_COLOR)

    draw.text((80, 280), roi_str, font=big_font, fill=roi_color)
    draw.text((80, 420), "ROI за 30 днів", font=small_font, fill=SUBTEXT_COLOR)

    grid_items = [
        (f"{winrate}%", "Winrate"),
        (str(total_bets), "Ставок"),
        (f"Рівень {level}", "XP"),
        (f"Топ {top_percent}%", "Рейтинг"),
    ]
    positions = [(80, 520), (560, 520), (80, 720), (560, 720)]

    for (value, label), (x, y) in zip(grid_items, positions):
        draw.rectangle((x, y, x + 440, y + 160), fill=CARD_COLOR, outline="#1E3A5F", width=2)
        draw.text((x + 20, y + 20), value, font=medium_font, fill=TEXT_COLOR)
        draw.text((x + 20, y + 95), label, font=small_font, fill=SUBTEXT_COLOR)

    draw.text((80, 1000), "t.me/bet_tracker_stats_bot", font=small_font, fill="#2A4A6B")

    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer.getvalue()
