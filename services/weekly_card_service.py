# -*- coding: utf-8 -*-
from datetime import datetime, timedelta


def get_user_rank_percentile(user_id: int) -> int:
    """
    Порівнює ROI юзера з усіма активними юзерами.
    Повертає відсоток юзерів з нижчим ROI.
    """
    try:
        from bets_db import get_full_stats_between
        from db import get_conn

        end_dt = datetime.now()
        start_dt = end_dt - timedelta(days=30)

        conn = get_conn()
        cur = conn.cursor()
        cur.execute(
            "SELECT user_id FROM users "
            "WHERE is_active = 1 AND user_id != %s",
            (user_id,)
        )
        other_users = cur.fetchall()
        conn.close()

        if not other_users:
            return 50

        my_stats = get_full_stats_between(
            user_id, start_dt, end_dt
        )
        my_roi = my_stats.get("roi", 0)

        lower_count = 0
        total_count = 0
        for u in other_users:
            try:
                uid = u["user_id"] if isinstance(u, dict) else u[0]
                stats = get_full_stats_between(
                    uid, start_dt, end_dt
                )
                if stats["total_bets"] > 0:
                    total_count += 1
                    if stats["roi"] < my_roi:
                        lower_count += 1
            except Exception:
                pass

        if total_count == 0:
            return 50
        return round((lower_count / total_count) * 100)

    except Exception:
        return 50
