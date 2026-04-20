# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont

from bets_db import get_full_stats_between
from db import get_conn


BG_COLOR = "#0E1A2E"
GREEN_COLOR = "#00E676"
RED_COLOR = "#FF5252"
TEXT_COLOR = "#FFFFFF"
SUBTEXT_COLOR = "#8899BB"
CARD_COLOR = "#152540"


def _load_font(size: int, bold: bool = False):
    font_name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    try:
        return ImageFont.truetype(font_name, size=size)
    except Exception:
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
    start_dt = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
    end_dt = min(now, start_dt + timedelta(days=7))
    return start_dt, end_dt


def get_week_stats(user_id: int) -> dict:
    """Отримує статистику за поточний тиждень (пн-нд)"""
    start_dt, end_dt = _week_range()
    stats = get_full_stats_between(user_id, start_dt, end_dt)
    stats["start_dt"] = start_dt
    stats["end_dt"] = end_dt
    return stats


def get_user_rank_percentile(user_id: int) -> int:
    """
    Порівнює ROI юзера з усіма активними юзерами за останні 30 днів.
    Повертає відсоток юзерів з нижчим ROI (наприклад 78 = "ти кращий за 78%")
    SQL: SELECT COUNT(*) FROM users WHERE is_active=1 ... 
    """
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


def generate_weekly_card(user_id: int, stats: dict, username: str, rank_percentile: int) -> bytes:
    """
    Генерує PNG картинку 1080x1080 зі статистикою тижня.
    Повертає bytes.
    
    Дизайн:
    - Фон темний #0E1A2E
    - Верхній блок: "ТВІЙ ТИЖДЕНЬ" + дати
    - Центр великим шрифтом: ROI з кольором (зелений якщо > 0, червоний якщо < 0)
    - Сітка 2x2: Winrate / Прибуток / Ставок / Сер.коеф
    - Внизу: "Ти в топ X% беттерів" + watermark "Bet Tracker Bot"
    
    Кольори:
    - Фон: #0E1A2E
    - Зелений: #00E676
    - Червоний: #FF5252
    - Текст: #FFFFFF
    - Субтекст: #8899BB
    
    Шрифти: використовуй ImageFont.load_default(size=N) якщо немає ttf файлів
    """
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

    draw.rounded_rectangle((60, 60, 1020, 260), radius=34, fill=CARD_COLOR)
    draw.text((100, 96), "ТВІЙ ТИЖДЕНЬ", font=title_font, fill=TEXT_COLOR)
    draw.text((100, 158), date_range_text, font=subtitle_font, fill=SUBTEXT_COLOR)
    draw.text((100, 200), f"@{safe_username}", font=subtitle_font, fill=SUBTEXT_COLOR)

    roi = round(float(stats.get("roi", 0) or 0), 2)
    roi_color = GREEN_COLOR if roi > 0 else RED_COLOR if roi < 0 else TEXT_COLOR
    draw.text((540, 330), _format_roi(roi), font=hero_font, fill=roi_color, anchor="ma")
    draw.text((540, 470), "ROI за тиждень", font=subtitle_font, fill=SUBTEXT_COLOR, anchor="ma")

    cards = [
        ("Winrate", f"{round(float(stats.get('win_rate', 0) or 0), 2)}%"),
        ("Прибуток", _format_profit(round(float(stats.get("net_profit", 0) or 0), 2))),
        ("Ставок", str(int(stats.get("total_bets", 0) or 0))),
        ("Сер. коеф", str(round(float(stats.get("avg_odds", 0) or 0), 2))),
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

    draw.text((540, 975), f"Ти в топ {rank_percentile}% беттерів", font=footer_font, fill=TEXT_COLOR, anchor="ma")
    draw.text((540, 1025), "Bet Tracker Bot", font=watermark_font, fill=SUBTEXT_COLOR, anchor="ma")

    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer.getvalue()
