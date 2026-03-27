from datetime import datetime
import json

from db import get_conn


def add_column_if_not_exists(table_name: str, column_name: str, column_def: str):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = ? AND column_name = ?
    """, (table_name, column_name))
    exists = cur.fetchone()

    if not exists:
        cur.execute(f'ALTER TABLE "{table_name}" ADD COLUMN "{column_name}" {column_def}')
        conn.commit()

    conn.close()


def init_bets_table():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
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
    """)

    conn.commit()
    conn.close()

    add_column_if_not_exists("bets", "bet_type", "TEXT")
    add_column_if_not_exists("bets", "bet_subtype", "TEXT")
    add_column_if_not_exists("bets", "is_trial", "INTEGER DEFAULT 0")


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
    is_trial: bool = False,
):
    conn = get_conn()
    cur = conn.cursor()

    raw_json_value = json.dumps(raw_json, ensure_ascii=False) if raw_json is not None else None

    cur.execute("""
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
            is_trial,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        RETURNING id
    """, (
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
        1 if is_trial else 0,
        datetime.now().isoformat(),
    ))

    row = cur.fetchone()
    conn.commit()
    conn.close()
    return row["id"] if row else None


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


def _calc_stats(rows):
    total_bets = 0
    wins = 0
    losses = 0
    refunds = 0
    total_stake = 0.0
    total_profit = 0.0
    odds_values = []
    win_streak = 0
    best_win_streak = 0
    current_streak = 0

    total_type_count = 0
    result_type_count = 0
    total_type_profit = 0.0
    result_type_profit = 0.0

    under_2_count = 0
    over_2_count = 0
    under_2_profit = 0.0
    over_2_profit = 0.0

    last_results_list = []

    for row in rows:
        if row["parse_status"] != "parsed":
            continue
        if row["bet_result"] not in ("win", "lose", "refund", "pending"):
            continue

        stake = float(row["stake_amount"] or 0)
        odds = float(row["odds"] or 0)
        bet_result = row["bet_result"]
        bet_type = row.get("bet_type")
        total_bets += 1

        if odds > 0:
            odds_values.append(odds)

        if bet_result == "win":
            wins += 1
            profit = stake * (odds - 1)
            current_streak += 1
            if current_streak > best_win_streak:
                best_win_streak = current_streak
        elif bet_result == "lose":
            losses += 1
            profit = -stake
            current_streak = 0
        elif bet_result == "refund":
            refunds += 1
            profit = 0
            current_streak = 0
        else:
            profit = 0

        total_stake += stake
        total_profit += profit

        if bet_result != "pending":
            last_results_list.append(_result_to_symbol(bet_result))

        if bet_type == "total":
            total_type_count += 1
            total_type_profit += profit
        elif bet_type == "result":
            result_type_count += 1
            result_type_profit += profit

        if odds > 0:
            if odds < 2:
                under_2_count += 1
                under_2_profit += profit
            else:
                over_2_count += 1
                over_2_profit += profit

    settled_bets = wins + losses
    win_rate = round((wins / settled_bets) * 100, 2) if settled_bets > 0 else 0.0
    avg_odds = round(sum(odds_values) / len(odds_values), 2) if odds_values else 0.0
    roi = round((total_profit / total_stake) * 100, 2) if total_stake > 0 else 0.0
    win_streak = current_streak

    return {
        "total_bets": total_bets,
        "wins": wins,
        "losses": losses,
        "refunds": refunds,
        "win_rate": win_rate,
        "avg_odds": avg_odds,
        "total_stake": round(total_stake, 2),
        "net_profit": round(total_profit, 2),
        "roi": roi,
        "win_streak": win_streak,
        "best_win_streak": best_win_streak,
        "total_type_count": total_type_count,
        "result_type_count": result_type_count,
        "total_type_profit": round(total_type_profit, 2),
        "result_type_profit": round(result_type_profit, 2),
        "under_2_count": under_2_count,
        "over_2_count": over_2_count,
        "under_2_profit": round(under_2_profit, 2),
        "over_2_profit": round(over_2_profit, 2),
        "last_results": " ".join(last_results_list[-5:]) if last_results_list else "-",
    }


def _get_rows_between(user_id: int, start_dt, end_dt, include_trial: bool = False):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT *
        FROM bets
        WHERE user_id = ?
          AND created_at >= ?
          AND created_at <= ?
          AND COALESCE(is_trial, 0) = ?
        ORDER BY created_at ASC
    """, (
        user_id,
        start_dt.isoformat(),
        end_dt.isoformat(),
        1 if include_trial else 0,
    ))
    rows = cur.fetchall()

    conn.close()
    return rows


def get_basic_stats_between(user_id: int, start_dt, end_dt, include_trial: bool = False):
    rows = _get_rows_between(user_id, start_dt, end_dt, include_trial=include_trial)
    stats = _calc_stats(rows)
    return {
        "net_profit": stats["net_profit"],
        "roi": stats["roi"],
        "win_rate": stats["win_rate"],
        "avg_odds": stats["avg_odds"],
        "win_streak": stats["win_streak"],
    }


def get_full_stats_between(user_id: int, start_dt, end_dt, include_trial: bool = False):
    rows = _get_rows_between(user_id, start_dt, end_dt, include_trial=include_trial)
    return _calc_stats(rows)


def get_analytics_between(user_id: int, start_dt, end_dt, include_trial: bool = False):
    rows = _get_rows_between(user_id, start_dt, end_dt, include_trial=include_trial)
    stats = _calc_stats(rows)

    best_type = "total" if stats["total_type_profit"] >= stats["result_type_profit"] else "result"
    worst_type = "result" if best_type == "total" else "total"

    recent_profit = stats["net_profit"]
    previous_profit = 0.0

    if stats["win_rate"] >= 60:
        conclusion_code = "good"
    elif stats["win_rate"] >= 45:
        conclusion_code = "neutral"
    else:
        conclusion_code = "bad"

    if stats["avg_odds"] < 2:
        coeff_code = "coeff_under_2"
    else:
        coeff_code = "coeff_over_2"

    losing_streak = 0
    if stats["last_results"] != "-":
        parts = stats["last_results"].split()
        for item in reversed(parts):
            if item == "❌":
                losing_streak += 1
            else:
                break

    risk_code = ""
    if losing_streak >= 3:
        risk_code = "losing_streak"
    elif stats["roi"] < -15:
        risk_code = "roi_drop"

    if stats["total_type_count"] > stats["result_type_count"]:
        profile_code = "system"
    else:
        profile_code = "mixed"

    return {
        **stats,
        "best_type": best_type,
        "worst_type": worst_type,
        "conclusion_code": conclusion_code,
        "coeff_code": coeff_code,
        "risk_code": risk_code,
        "losing_streak": losing_streak,
        "recent_profit": recent_profit,
        "previous_profit": previous_profit,
        "profile_code": profile_code,
    }
