# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
import json

from db import get_conn


VALID_RESULTS = {"win", "lose", "refund", "pending"}
SETTLED_RESULTS = {"win", "lose", "refund"}
ODDS_BUCKETS = ("lt2", "mid", "high")
TYPE_BUCKETS = ("total", "result")
MARKET_BUCKETS = ("1x2", "total", "btts", "handicap", "double_chance", "corners", "cards", "other")


def add_column_if_not_exists(table_name: str, column_name: str, column_def: str):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = ? AND column_name = ?
    """,
        (table_name, column_name),
    )
    exists = cur.fetchone()

    if not exists:
        cur.execute(f'ALTER TABLE "{table_name}" ADD COLUMN "{column_name}" {column_def}')
        conn.commit()

    conn.close()


def init_bets_table():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS bets (
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL,
            photo_file_id TEXT,
            stake_amount DOUBLE PRECISION,
            odds DOUBLE PRECISION,
            bet_result TEXT,
            currency TEXT DEFAULT 'UAH',
            parse_status TEXT DEFAULT 'parsed',
            raw_json TEXT,
            extraction_error TEXT,
            bet_type TEXT,
            bet_subtype TEXT,
            is_trial INTEGER DEFAULT 0,
            created_at TEXT NOT NULL
        )
    """
    )

    conn.commit()
    conn.close()

    add_column_if_not_exists("bets", "bet_type", "TEXT")
    add_column_if_not_exists("bets", "bet_subtype", "TEXT")
    add_column_if_not_exists("bets", "bet_market", "TEXT")
    add_column_if_not_exists("bets", "is_trial", "INTEGER DEFAULT 0")
    add_column_if_not_exists("bets", "emotion", "TEXT")
    add_column_if_not_exists("bets", "profit", "DOUBLE PRECISION DEFAULT 0")
    add_column_if_not_exists("bets", "first_reminder_sent_at", "TEXT")
    add_column_if_not_exists("bets", "final_reminder_sent_at", "TEXT")


def create_bet(
    user_id: int,
    photo_file_id: str | None,
    stake_amount,
    odds,
    bet_result,
    currency: str = "UAH",
    parse_status: str = "parsed",
    raw_json=None,
    extraction_error: str | None = None,
    bet_type: str | None = None,
    bet_subtype: str | None = None,
    bet_market: str | None = None,
    is_trial: bool = False,
):
    conn = get_conn()
    cur = conn.cursor()

    raw_json_value = json.dumps(raw_json, ensure_ascii=False) if raw_json is not None else None

    cur.execute(
        """
        INSERT INTO bets (
            user_id,
            photo_file_id,
            stake_amount,
            odds,
            bet_result,
            currency,
            parse_status,
            raw_json,
            extraction_error,
            bet_type,
            bet_subtype,
            bet_market,
            is_trial,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        RETURNING id
    """,
        (
            user_id,
            photo_file_id,
            stake_amount,
            odds,
            bet_result,
            currency,
            parse_status,
            raw_json_value,
            extraction_error,
            bet_type,
            bet_subtype,
            bet_market,
            1 if is_trial else 0,
            datetime.now().isoformat(),
        ),
    )

    row = cur.fetchone()
    conn.commit()
    conn.close()
    return row["id"] if row else None


def update_bet_emotion(bet_id: int, emotion: str):
    """Зберігає емоцію до ставки"""
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        UPDATE bets
        SET emotion = ?
        WHERE id = ?
    """,
        (emotion, bet_id),
    )

    conn.commit()
    conn.close()


def get_pending_bets(user_id: int) -> list[dict]:
    """
    Return pending bets for a user that are older than 30 minutes.
    """
    conn = get_conn()
    cur = conn.cursor()
    threshold = (datetime.now() - timedelta(minutes=30)).isoformat()

    cur.execute(
        """
        SELECT id, stake_amount, odds, created_at, bet_type, bet_market
        FROM bets
        WHERE user_id = ?
          AND bet_result = 'pending'
          AND parse_status = 'parsed'
          AND created_at <= ?
        ORDER BY created_at DESC
        LIMIT 10
    """,
        (user_id, threshold),
    )
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_all_pending_bets_for_reminder() -> list[dict]:
    """
    Return parsed pending bets due for a reminder.
    First reminder: once after 4 hours.
    Final reminder: once after 48 hours.
    """
    conn = get_conn()
    cur = conn.cursor()

    four_hours_ago = (datetime.now() - timedelta(hours=4)).isoformat()
    two_days_ago = (datetime.now() - timedelta(hours=48)).isoformat()

    cur.execute(
        """
        SELECT b.id, b.user_id, b.stake_amount, b.odds, b.bet_type,
               b.bet_market, b.created_at, u.lang
        FROM bets b
        JOIN users u ON u.user_id = b.user_id
        WHERE b.bet_result = 'pending'
          AND b.parse_status = 'parsed'
          AND (
                (b.created_at <= ? AND COALESCE(b.final_reminder_sent_at, '') = '')
             OR (b.created_at <= ? AND b.created_at > ? AND COALESCE(b.first_reminder_sent_at, '') = '')
          )
        ORDER BY b.created_at ASC
    """,
        (two_days_ago, four_hours_ago, two_days_ago),
    )
    rows = cur.fetchall()
    conn.close()

    result = []
    for row in rows:
        item = dict(row)
        item["is_final"] = bool((item.get("created_at") or "") <= two_days_ago)
        result.append(item)
    return result


def mark_pending_bet_reminder_sent(bet_id: int, is_final: bool = False):
    """Mark a pending bet reminder as sent."""
    conn = get_conn()
    cur = conn.cursor()
    field_name = "final_reminder_sent_at" if is_final else "first_reminder_sent_at"
    cur.execute(
        f"""
        UPDATE bets
        SET {field_name} = ?
        WHERE id = ?
    """,
        (datetime.now().isoformat(), bet_id),
    )
    conn.commit()
    conn.close()


def get_pending_bets_for_auto_expire(grace_hours: int = 24) -> list[dict]:
    """
    Return pending bets that should be excluded from stats after
    the final reminder grace period has passed.
    """
    conn = get_conn()
    cur = conn.cursor()
    cutoff = (datetime.now() - timedelta(hours=grace_hours)).isoformat()
    cur.execute(
        """
        SELECT b.id, b.user_id, u.lang
        FROM bets b
        JOIN users u ON u.user_id = b.user_id
        WHERE b.bet_result = 'pending'
          AND b.parse_status = 'parsed'
          AND COALESCE(b.final_reminder_sent_at, '') != ''
          AND b.final_reminder_sent_at <= ?
    """,
        (cutoff,),
    )
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def expire_pending_bet(bet_id: int) -> bool:
    """
    Exclude an unresolved pending bet from stats.
    """
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE bets
        SET parse_status = 'expired'
        WHERE id = ?
          AND bet_result = 'pending'
          AND parse_status = 'parsed'
    """,
        (bet_id,),
    )
    conn.commit()
    updated = cur.rowcount > 0
    conn.close()
    return updated


def close_pending_bet(bet_id: int, user_id: int, result: str) -> bool:
    """
    Close a pending bet with a settled result.
    Allowed results: win, lose, refund/return.
    """
    normalized_result = "refund" if result == "return" else result
    if normalized_result not in {"win", "lose", "refund"}:
        return False

    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT stake_amount, odds
        FROM bets
        WHERE id = ? AND user_id = ?
          AND bet_result = 'pending'
    """,
        (bet_id, user_id),
    )
    row = cur.fetchone()

    if not row:
        conn.close()
        return False

    stake = float(row.get("stake_amount") or 0)
    odds = float(row.get("odds") or 1)

    if normalized_result == "win":
        profit = round(stake * (odds - 1), 2)
    elif normalized_result == "lose":
        profit = round(-stake, 2)
    else:
        profit = 0.0

    cur.execute(
        """
        UPDATE bets
        SET bet_result = ?,
            profit = ?
        WHERE id = ? AND user_id = ?
    """,
        (normalized_result, profit, bet_id, user_id),
    )

    conn.commit()
    updated = cur.rowcount > 0
    conn.close()
    return updated


def get_pending_count(user_id: int) -> int:
    """Return the number of parsed pending bets for a user."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT COUNT(*) AS cnt
        FROM bets
        WHERE user_id = ?
          AND bet_result = 'pending'
          AND parse_status = 'parsed'
    """,
        (user_id,),
    )
    row = cur.fetchone()
    conn.close()
    return int((row or {}).get("cnt") or 0)


def _safe_float(value) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def _result_to_symbol(result: str) -> str:
    if result == "win":
        return "✅"
    if result == "lose":
        return "❌"
    if result == "refund":
        return "➖"
    if result == "pending":
        return "⏳"
    return "?"


def _normalize_row(row):
    if row.get("parse_status") != "parsed":
        return None
    result = row.get("bet_result")
    if result not in VALID_RESULTS:
        return None

    stake = _safe_float(row.get("stake_amount"))
    odds = _safe_float(row.get("odds"))
    created_at_raw = row.get("created_at")
    created_at = None
    if created_at_raw:
        try:
            created_at = datetime.fromisoformat(created_at_raw)
        except Exception:
            created_at = None

    if result == "win":
        profit = stake * (odds - 1) if odds > 0 else 0.0
    elif result == "lose":
        profit = -stake
    else:
        profit = 0.0

    market = _normalize_market(row.get("bet_market")) or _infer_market_from_legacy(row.get("bet_type"), row.get("bet_subtype"))
    legacy_group = row.get("bet_type") if row.get("bet_type") in TYPE_BUCKETS else _legacy_group_from_market(market)

    return {
        "stake": stake,
        "odds": odds,
        "bet_result": result,
        "bet_type": legacy_group,
        "bet_market": market,
        "profit": profit,
        "created_at": created_at,
    }




def _normalize_market(value: str | None) -> str | None:
    if not value:
        return None
    value = (value or "").strip().lower()
    return value if value in MARKET_BUCKETS else None


def _infer_market_from_legacy(bet_type: str | None, bet_subtype: str | None) -> str | None:
    bet_type = (bet_type or "").strip().lower()
    bet_subtype = (bet_subtype or "").strip().lower()

    if bet_type in MARKET_BUCKETS:
        return bet_type
    if bet_subtype in MARKET_BUCKETS:
        return bet_subtype

    if bet_type == "total":
        return "total"
    if bet_subtype in {"tb", "tm"}:
        return "total"
    if bet_subtype == "double_chance":
        return "double_chance"
    if bet_subtype == "handicap":
        return "handicap"
    if bet_subtype in {"yes", "no"}:
        return "btts"
    if bet_type == "result":
        return "1x2"
    return None


def _legacy_group_from_market(market: str | None) -> str | None:
    if market in {"total", "corners", "cards"}:
        return "total"
    if market in {"1x2", "btts", "handicap", "double_chance", "other"}:
        return "result"
    return None

def _empty_bucket():
    return {
        "count": 0,
        "settled_count": 0,
        "wins": 0,
        "losses": 0,
        "refunds": 0,
        "pending": 0,
        "stake": 0.0,
        "settled_stake": 0.0,
        "profit": 0.0,
        "odds_sum": 0.0,
        "odds_count": 0,
    }


def _update_bucket(bucket: dict, item: dict):
    bucket["count"] += 1
    bucket["stake"] += item["stake"]

    if item["odds"] > 0:
        bucket["odds_sum"] += item["odds"]
        bucket["odds_count"] += 1

    result = item["bet_result"]
    if result == "win":
        bucket["wins"] += 1
        bucket["settled_count"] += 1
        bucket["settled_stake"] += item["stake"]
    elif result == "lose":
        bucket["losses"] += 1
        bucket["settled_count"] += 1
        bucket["settled_stake"] += item["stake"]
    elif result == "refund":
        bucket["refunds"] += 1
        bucket["settled_count"] += 1
        bucket["settled_stake"] += item["stake"]
    elif result == "pending":
        bucket["pending"] += 1

    bucket["profit"] += item["profit"]


def _finalize_bucket(bucket: dict) -> dict:
    settled_for_wr = bucket["wins"] + bucket["losses"]
    win_rate = round((bucket["wins"] / settled_for_wr) * 100, 2) if settled_for_wr > 0 else 0.0
    roi = round((bucket["profit"] / bucket["settled_stake"]) * 100, 2) if bucket["settled_stake"] > 0 else 0.0
    avg_odds = round(bucket["odds_sum"] / bucket["odds_count"], 2) if bucket["odds_count"] > 0 else 0.0
    bucket["stake"] = round(bucket["stake"], 2)
    bucket["settled_stake"] = round(bucket["settled_stake"], 2)
    bucket["profit"] = round(bucket["profit"], 2)
    bucket["avg_odds"] = avg_odds
    bucket["win_rate"] = win_rate
    bucket["roi"] = roi
    return bucket


def _get_odds_bucket(odds: float) -> str | None:
    if odds <= 0:
        return None
    if odds < 2.0:
        return "lt2"
    if odds < 2.5:
        return "mid"
    return "high"


def _pick_best_bucket(buckets: dict) -> str:
    candidates = [(name, data) for name, data in buckets.items() if data["settled_count"] >= 3]
    if not candidates:
        candidates = [(name, data) for name, data in buckets.items() if data["count"] > 0]
    if not candidates:
        return "none"
    candidates.sort(key=lambda item: (item[1]["roi"], item[1]["profit"], item[1]["win_rate"], item[1]["count"]), reverse=True)
    return candidates[0][0]


def _pick_weak_bucket(buckets: dict) -> str:
    candidates = [
        (name, data)
        for name, data in buckets.items()
        if data["settled_count"] >= 3 and data["roi"] < 0
    ]
    if not candidates:
        candidates = [
            (name, data)
            for name, data in buckets.items()
            if data["count"] > 0 and data["roi"] < 0
        ]
    if not candidates:
        return "none"
    candidates.sort(key=lambda item: (item[1]["roi"], item[1]["profit"], item[1]["win_rate"], -item[1]["count"]))
    return candidates[0][0]


def _profile_code(stats: dict) -> str:
    avg_odds = stats["avg_odds"]
    lt2_share = stats["odds_lt2"]["count"] / stats["total_bets"] if stats["total_bets"] else 0
    high_share = stats["odds_high"]["count"] / stats["total_bets"] if stats["total_bets"] else 0
    total_share = stats["types"]["total"]["count"] / stats["total_bets"] if stats["total_bets"] else 0

    if high_share >= 0.35 or avg_odds >= 2.3:
        return "aggressive"
    if lt2_share >= 0.65 and avg_odds and avg_odds < 1.95:
        return "careful"
    if total_share >= 0.7 and stats["roi"] >= 0:
        return "system"
    if 0.35 <= lt2_share <= 0.65 and 0.15 <= high_share <= 0.3:
        return "balanced"
    if stats["roi"] < 0 and stats["worst_lose_streak"] >= 4:
        return "mixed"
    return "mixed"


def _overall_status_code(stats: dict) -> str:
    if stats["roi"] >= 12 and stats["win_rate"] >= 58:
        return "great"
    if stats["roi"] >= 4 and stats["win_rate"] >= 52:
        return "good"
    if stats["roi"] >= -3 and stats["win_rate"] >= 45:
        return "neutral"
    return "bad"


def _trend_code(recent: dict, previous: dict) -> str:
    recent_profit = recent.get("profit", recent.get("net_profit", 0.0))
    previous_profit = previous.get("profit", previous.get("net_profit", 0.0))
    diff = recent_profit - previous_profit
    if diff > 0.01:
        return "up"
    if diff < -0.01:
        return "down"
    return "flat"


def _recommendation_code(stats: dict) -> str:
    if stats["odds_high"]["roi"] < 0 and stats["odds_high"]["count"] >= 3:
        return "cut_high_odds"
    if stats["types"]["result"]["roi"] < 0 <= stats["types"]["total"]["roi"] and stats["types"]["result"]["count"] >= 3:
        return "focus_total"
    if stats["types"]["total"]["roi"] < 0 <= stats["types"]["result"]["roi"] and stats["types"]["total"]["count"] >= 3:
        return "focus_result"
    if stats["worst_lose_streak"] >= 3:
        return "reduce_risk"
    return "keep_discipline"


def _risk_codes(stats: dict, recent: dict, previous: dict) -> list[str]:
    codes: list[str] = []
    if stats["worst_lose_streak"] >= 3:
        codes.append("losing_streak")
    if stats["roi"] < -10:
        codes.append("negative_roi")
    if stats["odds_high"]["count"] >= 3 and stats["odds_high"]["roi"] < 0:
        codes.append("high_odds_drag")
    if stats["win_rate"] and stats["win_rate"] < 45:
        codes.append("low_winrate")
    recent_profit = recent.get("profit", recent.get("net_profit", 0.0))
    previous_profit = previous.get("profit", previous.get("net_profit", 0.0))
    recent_roi = recent.get("roi", 0.0)
    previous_roi = previous.get("roi", 0.0)
    if recent_profit < previous_profit and recent_roi < previous_roi:
        codes.append("downtrend")
    return codes[:3]


def _calc_stats(rows):
    stats = {
        "total_bets": 0,
        "settled_bets": 0,
        "pending_bets": 0,
        "wins": 0,
        "losses": 0,
        "refunds": 0,
        "total_stake": 0.0,
        "settled_stake": 0.0,
        "net_profit": 0.0,
        "avg_odds": 0.0,
        "roi": 0.0,
        "current_win_streak": 0,
        "best_win_streak": 0,
        "current_lose_streak": 0,
        "worst_lose_streak": 0,
        "last_results": "-",
        "types": {name: _empty_bucket() for name in TYPE_BUCKETS},
        "markets": {name: _empty_bucket() for name in MARKET_BUCKETS},
        "odds_lt2": _empty_bucket(),
        "odds_mid": _empty_bucket(),
        "odds_high": _empty_bucket(),
        "emotions": {
            "tilt": {"count": 0, "profit": 0.0, "stake": 0.0, "wins": 0, "losses": 0},
            "anxiety": {"count": 0, "profit": 0.0, "stake": 0.0, "wins": 0, "losses": 0},
            "confident": {"count": 0, "profit": 0.0, "stake": 0.0, "wins": 0, "losses": 0},
            "neutral": {"count": 0, "profit": 0.0, "stake": 0.0, "wins": 0, "losses": 0},
            "none": {"count": 0, "profit": 0.0, "stake": 0.0, "wins": 0, "losses": 0},
        },
    }

    odds_sum = 0.0
    odds_count = 0
    current_win_streak = 0
    current_lose_streak = 0
    best_win_streak = 0
    worst_lose_streak = 0
    last_results_list = []

    for row in rows:
        item = _normalize_row(row)
        if not item:
            continue

        stats["total_bets"] += 1
        stats["total_stake"] += item["stake"]

        if item["odds"] > 0:
            odds_sum += item["odds"]
            odds_count += 1

        result = item["bet_result"]
        if result in SETTLED_RESULTS:
            stats["settled_bets"] += 1
            stats["settled_stake"] += item["stake"]
        if result == "pending":
            stats["pending_bets"] += 1

        if result == "win":
            stats["wins"] += 1
            current_win_streak += 1
            current_lose_streak = 0
            best_win_streak = max(best_win_streak, current_win_streak)
        elif result == "lose":
            stats["losses"] += 1
            current_lose_streak += 1
            current_win_streak = 0
            worst_lose_streak = max(worst_lose_streak, current_lose_streak)
        elif result == "refund":
            stats["refunds"] += 1
            current_win_streak = 0
            current_lose_streak = 0
        elif result == "pending":
            pass

        stats["net_profit"] += item["profit"]

        if result != "pending":
            last_results_list.append(_result_to_symbol(result))

        if item["bet_type"] in stats["types"]:
            _update_bucket(stats["types"][item["bet_type"]], item)
        if item.get("bet_market") in stats["markets"]:
            _update_bucket(stats["markets"][item["bet_market"]], item)

        odds_bucket = _get_odds_bucket(item["odds"])
        if odds_bucket == "lt2":
            _update_bucket(stats["odds_lt2"], item)
        elif odds_bucket == "mid":
            _update_bucket(stats["odds_mid"], item)
        elif odds_bucket == "high":
            _update_bucket(stats["odds_high"], item)

        emotion_raw = (row.get("emotion") or "none").strip().lower()
        emotion_key = emotion_raw if emotion_raw in stats["emotions"] else "none"
        emotion_bucket = stats["emotions"][emotion_key]
        emotion_bucket["count"] += 1
        emotion_bucket["profit"] += item["profit"]
        emotion_bucket["stake"] += item["stake"]
        if result == "win":
            emotion_bucket["wins"] += 1
        elif result == "lose":
            emotion_bucket["losses"] += 1

    settled_for_wr = stats["wins"] + stats["losses"]
    stats["win_rate"] = round((stats["wins"] / settled_for_wr) * 100, 2) if settled_for_wr > 0 else 0.0
    stats["avg_odds"] = round(odds_sum / odds_count, 2) if odds_count > 0 else 0.0
    stats["total_stake"] = round(stats["total_stake"], 2)
    stats["settled_stake"] = round(stats["settled_stake"], 2)
    stats["net_profit"] = round(stats["net_profit"], 2)
    stats["roi"] = round((stats["net_profit"] / stats["settled_stake"]) * 100, 2) if stats["settled_stake"] > 0 else 0.0
    stats["current_win_streak"] = current_win_streak
    stats["best_win_streak"] = best_win_streak
    stats["current_lose_streak"] = current_lose_streak
    stats["worst_lose_streak"] = worst_lose_streak
    stats["win_streak"] = current_win_streak
    stats["last_results"] = " ".join(last_results_list[-5:]) if last_results_list else "-"

    for bucket_name in TYPE_BUCKETS:
        stats["types"][bucket_name] = _finalize_bucket(stats["types"][bucket_name])
    for bucket_name in MARKET_BUCKETS:
        stats["markets"][bucket_name] = _finalize_bucket(stats["markets"][bucket_name])
    stats["odds_lt2"] = _finalize_bucket(stats["odds_lt2"])
    stats["odds_mid"] = _finalize_bucket(stats["odds_mid"])
    stats["odds_high"] = _finalize_bucket(stats["odds_high"])
    for emotion_bucket in stats["emotions"].values():
        emotion_bucket["profit"] = round(emotion_bucket["profit"], 2)
        emotion_bucket["stake"] = round(emotion_bucket["stake"], 2)
        if emotion_bucket["stake"] > 0:
            emotion_bucket["roi"] = round((emotion_bucket["profit"] / emotion_bucket["stake"]) * 100, 1)
        else:
            emotion_bucket["roi"] = 0.0

    stats["total_type_count"] = stats["types"]["total"]["count"]
    stats["result_type_count"] = stats["types"]["result"]["count"]
    stats["total_type_profit"] = stats["types"]["total"]["profit"]
    stats["result_type_profit"] = stats["types"]["result"]["profit"]
    stats["under_2_count"] = stats["odds_lt2"]["count"]
    stats["over_2_count"] = stats["odds_mid"]["count"] + stats["odds_high"]["count"]
    stats["under_2_profit"] = stats["odds_lt2"]["profit"]
    stats["over_2_profit"] = round(stats["odds_mid"]["profit"] + stats["odds_high"]["profit"], 2)

    return stats


def _format_emotion_stats_vip(emotions: dict, lang: str) -> str:
    """Format the full emotion statistics block for VIP users."""
    labels = {
        "ua": {
            "tilt": "😤 Тільт",
            "anxiety": "😰 Тривога",
            "confident": "😎 Впевнений",
            "neutral": "🤔 Нейтрально",
        },
        "ru": {
            "tilt": "😤 Тилт",
            "anxiety": "😰 Тревога",
            "confident": "😎 Уверен",
            "neutral": "🤔 Нейтрально",
        },
        "en": {
            "tilt": "😤 Tilt",
            "anxiety": "😰 Anxious",
            "confident": "😎 Confident",
            "neutral": "🤔 Neutral",
        },
    }
    current_labels = labels.get(lang, labels["ua"])
    lines = []

    for key in ("confident", "neutral", "anxiety", "tilt"):
        bucket = emotions.get(key, {})
        count = int(bucket.get("count") or 0)
        if count < 2:
            continue
        roi = float(bucket.get("roi") or 0)
        profit = float(bucket.get("profit") or 0)
        roi_s = f"+{roi}%" if roi >= 0 else f"{roi}%"
        profit_s = f"+{round(profit, 1)}" if profit >= 0 else str(round(profit, 1))
        lines.append(f"{current_labels[key]}: {count} | ROI {roi_s} | {profit_s}")

    if not lines:
        no_data = {
            "ua": "Потрібно 2+ ставки з емоцією",
            "ru": "Нужно 2+ ставки с эмоцией",
            "en": "Need 2+ bets with emotion",
        }
        return no_data.get(lang, no_data["ua"])
    return "\n".join(lines)


def _calc_emotion_loss(emotions: dict, lang: str) -> str:
    """Return the VIP-only emotional betting loss summary."""
    tilt_profit = float(emotions.get("tilt", {}).get("profit") or 0)
    anxiety_profit = float(emotions.get("anxiety", {}).get("profit") or 0)
    total_negative_profit = tilt_profit + anxiety_profit
    if total_negative_profit >= 0:
        return ""

    loss = abs(round(total_negative_profit, 1))
    texts = {
        "ua": (
            f"\n💸 Ціна емоційних ставок:\n"
            f"Втрати від тілту і тривоги: -{loss}\n"
            f"Без них результат був би кращим на {loss}"
        ),
        "ru": (
            f"\n💸 Цена эмоциональных ставок:\n"
            f"Потери от тилта и тревоги: -{loss}\n"
            f"Без них результат был бы лучше на {loss}"
        ),
        "en": (
            f"\n💸 Cost of emotional betting:\n"
            f"Loss from tilt and anxiety: -{loss}\n"
            f"Without them result would be better by {loss}"
        ),
    }
    return texts.get(lang, texts["ua"])


def _get_main_insight(stats: dict, lang: str) -> str:
    """Return the main performance insight based on type and odds buckets."""
    best_roi, worst_roi = -999.0, 999.0
    best_label, worst_label = "", ""

    bucket_labels = {
        "ua": {
            "total": "тоталах",
            "result": "результаті",
            "lt2": "коеф. до 2.0",
            "mid": "коеф. 2.0-2.5",
            "high": "коеф. 2.5+",
        },
        "ru": {
            "total": "тоталах",
            "result": "результате",
            "lt2": "коэф. до 2.0",
            "mid": "коэф. 2.0-2.5",
            "high": "коэф. 2.5+",
        },
        "en": {
            "total": "totals",
            "result": "result bets",
            "lt2": "odds below 2.0",
            "mid": "odds 2.0-2.5",
            "high": "odds 2.5+",
        },
    }
    current_labels = bucket_labels.get(lang, bucket_labels["ua"])
    all_buckets = {
        "total": stats["types"].get("total", {}),
        "result": stats["types"].get("result", {}),
        "lt2": stats.get("odds_lt2", {}),
        "mid": stats.get("odds_mid", {}),
        "high": stats.get("odds_high", {}),
    }

    for key, bucket in all_buckets.items():
        if int(bucket.get("count") or 0) < 3:
            continue
        roi = float(bucket.get("roi") or 0)
        if roi > best_roi:
            best_roi = roi
            best_label = current_labels.get(key, key)
        if roi < worst_roi:
            worst_roi = roi
            worst_label = current_labels.get(key, key)

    if not best_label or not worst_label or best_label == worst_label:
        return ""
    if round(best_roi - worst_roi, 1) < 10:
        return ""

    best_roi_s = f"+{round(best_roi, 1)}%" if best_roi >= 0 else f"{round(best_roi, 1)}%"
    worst_roi_s = f"+{round(worst_roi, 1)}%" if worst_roi >= 0 else f"{round(worst_roi, 1)}%"
    texts = {
        "ua": (
            f"💡 Головний інсайт:\n"
            f"Заробляєш на {best_label} (ROI {best_roi_s})\n"
            f"Зливаєш на {worst_label} (ROI {worst_roi_s})"
        ),
        "ru": (
            f"💡 Главный инсайт:\n"
            f"Зарабатываешь на {best_label} (ROI {best_roi_s})\n"
            f"Сливаешь на {worst_label} (ROI {worst_roi_s})"
        ),
        "en": (
            f"💡 Main insight:\n"
            f"Profit on {best_label} (ROI {best_roi_s})\n"
            f"Losing on {worst_label} (ROI {worst_roi_s})"
        ),
    }
    return texts.get(lang, texts["ua"])


def _get_action_items(stats: dict, emotions: dict, lang: str, is_vip: bool) -> str:
    """Return Basic/VIP action items for the week."""
    actions = []

    worst_type = None
    worst_type_roi = 0.0
    for key in ("total", "result"):
        bucket = stats["types"].get(key, {})
        if int(bucket.get("count") or 0) >= 3:
            roi = float(bucket.get("roi") or 0)
            if roi < worst_type_roi:
                worst_type_roi = roi
                worst_type = key

    type_names = {
        "ua": {"total": "тоталів", "result": "ставок на результат"},
        "ru": {"total": "тоталов", "result": "ставок на результат"},
        "en": {"total": "totals", "result": "result bets"},
    }
    if worst_type and worst_type_roi <= -5:
        loss = abs(round(float(stats["types"][worst_type].get("profit") or 0)))
        type_label = type_names.get(lang, type_names["ua"]).get(worst_type, worst_type)
        messages = {
            "ua": f"• Зменши {type_label} (зливають {loss})",
            "ru": f"• Уменьши {type_label} (сливают {loss})",
            "en": f"• Reduce {type_label} (losing {loss})",
        }
        actions.append(messages.get(lang, messages["ua"]))

    if is_vip:
        tilt_bucket = emotions.get("tilt", {})
        if int(tilt_bucket.get("count") or 0) >= 2 and float(tilt_bucket.get("profit") or 0) < 0:
            loss = abs(round(float(tilt_bucket.get("profit") or 0)))
            messages = {
                "ua": f"• 🛑 Не ставкуй на тілті, вже втратив {loss}",
                "ru": f"• 🛑 Не ставь на тилте, уже потерял {loss}",
                "en": f"• 🛑 Do not bet on tilt, already lost {loss}",
            }
            actions.append(messages.get(lang, messages["ua"]))

        best_odds = None
        best_odds_roi = 0.0
        for key in ("lt2", "mid", "high"):
            bucket = stats.get(f"odds_{key}", {})
            if int(bucket.get("count") or 0) >= 3:
                roi = float(bucket.get("roi") or 0)
                if roi > best_odds_roi:
                    best_odds_roi = roi
                    best_odds = key

        odds_labels = {
            "ua": {"lt2": "к. до 2.0", "mid": "к. 2.0-2.5", "high": "к. 2.5+"},
            "ru": {"lt2": "к. до 2.0", "mid": "к. 2.0-2.5", "high": "к. 2.5+"},
            "en": {"lt2": "odds below 2.0", "mid": "odds 2.0-2.5", "high": "odds 2.5+"},
        }
        if best_odds and best_odds_roi >= 5:
            odds_label = odds_labels.get(lang, odds_labels["ua"]).get(best_odds, best_odds)
            roi_s = f"+{round(best_odds_roi, 1)}%"
            messages = {
                "ua": f"• Фокусуйся на {odds_label}, твій ROI {roi_s}",
                "ru": f"• Фокусируйся на {odds_label}, твой ROI {roi_s}",
                "en": f"• Focus on {odds_label}, your ROI is {roi_s}",
            }
            actions.append(messages.get(lang, messages["ua"]))

    if not actions:
        return ""

    title = {
        "ua": "📋 Що зробити цього тижня:",
        "ru": "📋 Что сделать на этой неделе:",
        "en": "📋 Actions for this week:",
    }
    return title.get(lang, title["ua"]) + "\n" + "\n".join(actions)


def _get_rows_between(user_id: int, start_dt, end_dt, include_trial: bool = False):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT *
        FROM bets
        WHERE user_id = ?
          AND created_at >= ?
          AND created_at <= ?
          AND COALESCE(is_trial, 0) = ?
        ORDER BY created_at ASC
    """,
        (
            user_id,
            start_dt.isoformat(),
            end_dt.isoformat(),
            1 if include_trial else 0,
        ),
    )
    rows = cur.fetchall()

    conn.close()
    return rows


def _filter_rows_by_range(rows, start_dt, end_dt):
    filtered = []
    for row in rows:
        created_at_raw = row.get("created_at")
        if not created_at_raw:
            continue
        try:
            created_at = datetime.fromisoformat(created_at_raw)
        except Exception:
            continue
        if start_dt <= created_at <= end_dt:
            filtered.append(row)
    return filtered


def _parse_bet_created_at(row) -> datetime | None:
    created_at_raw = row.get("created_at")
    if not created_at_raw:
        return None
    try:
        return datetime.fromisoformat(created_at_raw)
    except Exception:
        return None


def get_tilt_signal_context(user_id: int) -> dict:
    now = datetime.now()
    start_2h = now - timedelta(hours=2)
    rows = _get_rows_between(user_id, start_2h, now, include_trial=False)

    parsed_rows = []
    for row in rows:
        if row.get("parse_status") != "parsed":
            continue
        created_at = _parse_bet_created_at(row)
        if not created_at:
            continue
        parsed_rows.append({**row, "_created_at_dt": created_at})

    parsed_rows.sort(key=lambda row: row["_created_at_dt"])

    last_90_start = now - timedelta(minutes=90)
    last_60_start = now - timedelta(minutes=60)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    rows_90 = [row for row in parsed_rows if row["_created_at_dt"] >= last_90_start]
    rows_60 = [row for row in parsed_rows if row["_created_at_dt"] >= last_60_start]
    rows_today = [row for row in parsed_rows if row["_created_at_dt"] >= today_start]

    recent_results = [row.get("bet_result") for row in rows_90 if row.get("bet_result")]
    signals: list[str] = []

    if len(rows_90) >= 3 and len(recent_results) >= 3 and recent_results[-3:] == ["lose", "lose", "lose"]:
        signals.append("chasing_losses")

    if len(rows_60) >= 4:
        signals.append("rapid_betting")

    if now.hour >= 23 and len(rows_today) >= 3:
        signals.append("late_night")

    return {
        "signals": signals,
        "count_last_60m": len(rows_60),
        "count_today": len(rows_today),
        "hour": now.hour,
    }


def check_tilt_signals(user_id: int) -> list[str]:
    return get_tilt_signal_context(user_id)["signals"]


def check_discipline_for_day(user_id, date) -> bool:
    if hasattr(date, "year") and hasattr(date, "month") and hasattr(date, "day"):
        target_date = date
    else:
        target_date = datetime.fromisoformat(str(date)).date()

    start_dt = datetime.combine(target_date, datetime.min.time())
    end_dt = start_dt + timedelta(days=1)
    rows = _get_rows_between(user_id, start_dt, end_dt, include_trial=False)

    if not rows:
        return True

    if len(rows) > 3:
        return False

    for row in rows:
        emotion = (row.get("emotion") or "").strip().lower()
        if emotion in {"tilt", "anxiety"}:
            return False

    return True


def _comparison_stats(rows, end_dt: datetime, days: int = 3):
    recent_start = end_dt - timedelta(days=days)
    previous_end = recent_start
    previous_start = previous_end - timedelta(days=days)

    recent_stats = _calc_stats(_filter_rows_by_range(rows, recent_start, end_dt))
    previous_stats = _calc_stats(_filter_rows_by_range(rows, previous_start, previous_end))
    return recent_stats, previous_stats


def _period_comparison(rows, end_dt: datetime, days: int):
    current_start = end_dt - timedelta(days=days)
    previous_end = current_start
    previous_start = previous_end - timedelta(days=days)
    current_stats = _calc_stats(_filter_rows_by_range(rows, current_start, end_dt))
    previous_stats = _calc_stats(_filter_rows_by_range(rows, previous_start, previous_end))
    return current_stats, previous_stats


def get_basic_stats_between(user_id: int, start_dt, end_dt, include_trial: bool = False):
    rows = _get_rows_between(user_id, start_dt, end_dt, include_trial=include_trial)
    stats = _calc_stats(rows)
    return {
        "net_profit": stats["net_profit"],
        "roi": stats["roi"],
        "win_rate": stats["win_rate"],
        "avg_odds": stats["avg_odds"],
        "win_streak": stats["current_win_streak"],
    }


def get_full_stats_between(user_id: int, start_dt, end_dt, include_trial: bool = False):
    rows = _get_rows_between(user_id, start_dt, end_dt, include_trial=include_trial)
    return _calc_stats(rows)


def get_analytics_between(user_id: int, start_dt, end_dt, plan: str = "basic", include_trial: bool = False):
    rows = _get_rows_between(user_id, start_dt, end_dt, include_trial=include_trial)
    stats = _calc_stats(rows)

    recent_stats, previous_stats = _comparison_stats(rows, end_dt, days=3)
    week_current, week_previous = _period_comparison(rows, end_dt, days=7)
    month_current, month_previous = _period_comparison(rows, end_dt, days=30)

    best_type = _pick_best_bucket(stats["types"])
    weak_type = _pick_weak_bucket(stats["types"])
    best_market = _pick_best_bucket(stats["markets"])
    weak_market = _pick_weak_bucket(stats["markets"])
    best_odds_bucket = _pick_best_bucket(
        {"lt2": stats["odds_lt2"], "mid": stats["odds_mid"], "high": stats["odds_high"]}
    )
    weak_odds_bucket = _pick_weak_bucket(
        {"lt2": stats["odds_lt2"], "mid": stats["odds_mid"], "high": stats["odds_high"]}
    )

    profile_code = _profile_code(stats)
    overall_status_code = _overall_status_code(stats)
    trend_code = _trend_code(recent_stats, previous_stats)
    recommendation_code = _recommendation_code(stats)
    risk_codes = _risk_codes(stats, recent_stats, previous_stats)

    strengths = []
    if best_market in stats["markets"] and stats["markets"][best_market]["count"] > 0:
        strengths.append(f"market:{best_market}")
    if best_odds_bucket in ODDS_BUCKETS and stats[f"odds_{best_odds_bucket}"]["count"] > 0:
        strengths.append(f"odds:{best_odds_bucket}")

    return {
        **stats,
        "plan": (plan or "basic").lower(),
        "overall_status_code": overall_status_code,
        "best_type": best_type,
        "weak_type": weak_type,
        "best_market": best_market,
        "weak_market": weak_market,
        "best_odds_bucket": best_odds_bucket,
        "weak_odds_bucket": weak_odds_bucket,
        "recent": {
            "profit": recent_stats["net_profit"],
            "roi": recent_stats["roi"],
            "win_rate": recent_stats["win_rate"],
            "settled_bets": recent_stats["settled_bets"],
        },
        "previous": {
            "profit": previous_stats["net_profit"],
            "roi": previous_stats["roi"],
            "win_rate": previous_stats["win_rate"],
            "settled_bets": previous_stats["settled_bets"],
        },
        "week_current": {
            "profit": week_current["net_profit"],
            "roi": week_current["roi"],
            "win_rate": week_current["win_rate"],
            "settled_bets": week_current["settled_bets"],
        },
        "week_previous": {
            "profit": week_previous["net_profit"],
            "roi": week_previous["roi"],
            "win_rate": week_previous["win_rate"],
            "settled_bets": week_previous["settled_bets"],
        },
        "month_current": {
            "profit": month_current["net_profit"],
            "roi": month_current["roi"],
            "win_rate": month_current["win_rate"],
            "settled_bets": month_current["settled_bets"],
        },
        "month_previous": {
            "profit": month_previous["net_profit"],
            "roi": month_previous["roi"],
            "win_rate": month_previous["win_rate"],
            "settled_bets": month_previous["settled_bets"],
        },
        "trend_code": trend_code,
        "profile_code": profile_code,
        "risk_codes": risk_codes,
        "recommendation_code": recommendation_code,
        "strengths": strengths,
    }
