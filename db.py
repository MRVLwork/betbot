import os
from datetime import datetime, timedelta

import psycopg2
from psycopg2.extras import RealDictCursor

TRIAL_SCREEN_LIMIT = 3


class PostgresCursorWrapper:
    def __init__(self, cursor):
        self.cursor = cursor

    def _adapt_query(self, query: str) -> str:
        return query.replace("?", "%s")

    def execute(self, query, params=None):
        query = self._adapt_query(query)
        if params is None:
            return self.cursor.execute(query)
        return self.cursor.execute(query, params)

    def executemany(self, query, params_seq):
        query = self._adapt_query(query)
        return self.cursor.executemany(query, params_seq)

    def fetchone(self):
        return self.cursor.fetchone()

    def fetchall(self):
        return self.cursor.fetchall()

    @property
    def rowcount(self):
        return self.cursor.rowcount

    def __getattr__(self, item):
        return getattr(self.cursor, item)


class PostgresConnectionWrapper:
    def __init__(self, conn):
        self.conn = conn

    def cursor(self):
        return PostgresCursorWrapper(self.conn.cursor(cursor_factory=RealDictCursor))

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def close(self):
        self.conn.close()

    def __getattr__(self, item):
        return getattr(self.conn, item)


def get_conn():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is not set")

    raw_conn = psycopg2.connect(database_url)
    return PostgresConnectionWrapper(raw_conn)


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


def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id BIGINT PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            is_active INTEGER DEFAULT 0,
            access_until TEXT,
            activated_by TEXT,
            activated_at TEXT,
            created_at TEXT NOT NULL,
            plan TEXT DEFAULT 'basic',
            daily_usage_reset_at TEXT,
            lang TEXT DEFAULT 'ua',
            trial_started_at TEXT,
            trial_used_count INTEGER DEFAULT 0,
            trial_completed INTEGER DEFAULT 0,
            promo_offer_used INTEGER DEFAULT 0
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS promo_codes (
            id SERIAL PRIMARY KEY,
            code TEXT UNIQUE NOT NULL,
            days INTEGER NOT NULL DEFAULT 30,
            plan_type TEXT NOT NULL DEFAULT 'basic',
            uses_left INTEGER NOT NULL DEFAULT 1,
            total_uses INTEGER NOT NULL DEFAULT 1,
            is_active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL,
            plan_key TEXT NOT NULL,
            plan_name TEXT NOT NULL,
            plan_type TEXT NOT NULL,
            duration_days INTEGER NOT NULL,
            amount_usd DOUBLE PRECISION NOT NULL,
            network TEXT NOT NULL DEFAULT 'TRC20',
            wallet_address TEXT,
            screenshot_file_id TEXT,
            status TEXT NOT NULL DEFAULT 'pending',
            tx_hash TEXT,
            admin_note TEXT,
            admin_message_id BIGINT,
            promo_sent_text TEXT,
            created_at TEXT NOT NULL,
            submitted_at TEXT,
            paid_at TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS star_payments (
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL,
            plan_key TEXT NOT NULL,
            plan_type TEXT NOT NULL,
            title TEXT NOT NULL,
            duration_days INTEGER NOT NULL,
            amount_xtr INTEGER NOT NULL,
            telegram_charge_id TEXT,
            provider_charge_id TEXT,
            status TEXT NOT NULL DEFAULT 'paid',
            created_at TEXT NOT NULL,
            paid_at TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS photo_logs (
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL,
            file_id TEXT,
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()

    add_column_if_not_exists("users", "plan", "TEXT DEFAULT 'basic'")
    add_column_if_not_exists("users", "daily_usage_reset_at", "TEXT")
    add_column_if_not_exists("users", "lang", "TEXT DEFAULT 'ua'")
    add_column_if_not_exists("users", "trial_started_at", "TEXT")
    add_column_if_not_exists("users", "trial_used_count", "INTEGER DEFAULT 0")
    add_column_if_not_exists("users", "trial_completed", "INTEGER DEFAULT 0")
    add_column_if_not_exists("users", "promo_offer_used", "INTEGER DEFAULT 0")

    add_column_if_not_exists("promo_codes", "plan_type", "TEXT DEFAULT 'basic'")

    add_column_if_not_exists("payments", "screenshot_file_id", "TEXT")
    add_column_if_not_exists("payments", "admin_message_id", "BIGINT")
    add_column_if_not_exists("payments", "promo_sent_text", "TEXT")
    add_column_if_not_exists("payments", "submitted_at", "TEXT")


def create_user_if_not_exists(user):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT user_id FROM users WHERE user_id = ?", (user.id,))
    row = cur.fetchone()

    tg_lang = (user.language_code or "").lower()
    if tg_lang.startswith("uk") or tg_lang.startswith("ua"):
        lang = "ua"
    elif tg_lang.startswith("ru"):
        lang = "ru"
    else:
        lang = "en"
    #lang = "ua" if tg_lang.startswith("ua") else "ru"

    if not row:
        cur.execute("""
            INSERT INTO users (
                user_id,
                username,
                first_name,
                is_active,
                access_until,
                activated_by,
                activated_at,
                created_at,
                plan,
                daily_usage_reset_at,
                lang,
                trial_started_at,
                trial_used_count,
                trial_completed,
                promo_offer_used
            )
            VALUES (?, ?, ?, 0, NULL, NULL, NULL, ?, 'basic', NULL, ?, NULL, 0, 0, 0)
        """, (
            user.id,
            user.username,
            user.first_name,
            datetime.now().isoformat(),
            lang,
        ))
    else:
        cur.execute("""
            UPDATE users
            SET username = ?, first_name = ?
            WHERE user_id = ?
        """, (
            user.username,
            user.first_name,
            user.id,
        ))

    conn.commit()
    conn.close()


def get_user(user_id: int):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    row = cur.fetchone()

    conn.close()
    return row


def has_used_promo_offer(user_id: int) -> bool:
    user = get_user(user_id)
    if not user:
        return False
    return int(user.get("promo_offer_used") or 0) == 1


def mark_promo_offer_used(user_id: int):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        UPDATE users
        SET promo_offer_used = 1
        WHERE user_id = ?
    """, (user_id,))

    conn.commit()
    conn.close()


def set_user_language(user_id: int, lang: str):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        UPDATE users
        SET lang = ?
        WHERE user_id = ?
    """, (lang, user_id))

    conn.commit()
    conn.close()


def user_has_access(user_id: int) -> bool:
    user = get_user(user_id)

    if not user:
        return False
    if not user["is_active"]:
        return False
    if not user["access_until"]:
        return False

    try:
        return datetime.fromisoformat(user["access_until"]) > datetime.now()
    except Exception:
        return False


def activate_user_access(user_id: int, days: int, plan_type: str, source: str):
    conn = get_conn()
    cur = conn.cursor()

    user = get_user(user_id)
    now = datetime.now()

    if user and user["access_until"]:
        try:
            current_until = datetime.fromisoformat(user["access_until"])
            base_time = current_until if current_until > now else now
        except Exception:
            base_time = now
    else:
        base_time = now

    new_until = base_time + timedelta(days=days)

    cur.execute("""
        UPDATE users
        SET is_active = 1,
            access_until = ?,
            activated_by = ?,
            activated_at = ?,
            plan = ?,
            daily_usage_reset_at = ?
        WHERE user_id = ?
    """, (
        new_until.isoformat(),
        source,
        now.isoformat(),
        plan_type,
        now.isoformat(),
        user_id
    ))

    conn.commit()
    conn.close()


def create_promo(code: str, days: int, uses: int, plan_type: str):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO promo_codes (
            code, days, plan_type, uses_left, total_uses, is_active, created_at
        )
        VALUES (?, ?, ?, ?, ?, 1, ?)
        RETURNING id
    """, (
        code,
        days,
        plan_type,
        uses,
        uses,
        datetime.now().isoformat()
    ))
    cur.fetchone()

    conn.commit()
    conn.close()


def validate_promo(code: str):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT * FROM promo_codes
        WHERE code = ? AND is_active = 1 AND uses_left > 0
    """, (code.strip(),))

    row = cur.fetchone()
    conn.close()
    return row


def activate_user_by_promo(user_id: int, promo_code: str, days: int, plan_type: str):
    conn = get_conn()
    cur = conn.cursor()

    now = datetime.now()

    cur.execute("SELECT access_until FROM users WHERE user_id = ?", (user_id,))
    user_row = cur.fetchone()

    if user_row and user_row["access_until"]:
        try:
            current_until = datetime.fromisoformat(user_row["access_until"])
            base_time = current_until if current_until > now else now
        except Exception:
            base_time = now
    else:
        base_time = now

    new_until = base_time + timedelta(days=days)

    cur.execute("""
        UPDATE users
        SET is_active = 1,
            access_until = ?,
            activated_by = ?,
            activated_at = ?,
            plan = ?,
            daily_usage_reset_at = ?
        WHERE user_id = ?
    """, (
        new_until.isoformat(),
        promo_code,
        now.isoformat(),
        plan_type,
        now.isoformat(),
        user_id
    ))

    cur.execute("""
        UPDATE promo_codes
        SET uses_left = uses_left - 1
        WHERE code = ?
    """, (promo_code,))

    conn.commit()
    conn.close()


def get_all_promos():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT code, days, plan_type, uses_left, total_uses, is_active, created_at
        FROM promo_codes
        ORDER BY id DESC
    """)
    rows = cur.fetchall()

    conn.close()
    return rows


def get_all_users(limit: int = 100):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT user_id, username, first_name, is_active, access_until, activated_by, plan
        FROM users
        ORDER BY created_at DESC
        LIMIT ?
    """, (limit,))
    rows = cur.fetchall()

    conn.close()
    return rows


def get_users_by_promo(code: str):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT user_id, username, first_name, access_until, activated_at, plan
        FROM users
        WHERE activated_by = ?
        ORDER BY activated_at DESC
    """, (code,))
    rows = cur.fetchall()

    conn.close()
    return rows


def create_payment(user_id: int, plan_key: str, plan_name: str, plan_type: str,
                   duration_days: int, amount_usd: float, wallet_address: str):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO payments (
            user_id,
            plan_key,
            plan_name,
            plan_type,
            duration_days,
            amount_usd,
            wallet_address,
            status,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, 'pending', ?)
        RETURNING id
    """, (
        user_id,
        plan_key,
        plan_name,
        plan_type,
        duration_days,
        amount_usd,
        wallet_address,
        datetime.now().isoformat()
    ))

    payment_id = cur.fetchone()["id"]

    conn.commit()
    conn.close()
    return payment_id


def get_payment_by_id(payment_id: int):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT * FROM payments WHERE id = ?", (payment_id,))
    row = cur.fetchone()

    conn.close()
    return row


def get_last_pending_payment(user_id: int):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT * FROM payments
        WHERE user_id = ? AND status IN ('pending', 'screenshot_received', 'submitted')
        ORDER BY id DESC
        LIMIT 1
    """, (user_id,))
    row = cur.fetchone()

    conn.close()
    return row


def set_payment_screenshot(payment_id: int, file_id: str):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        UPDATE payments
        SET screenshot_file_id = ?,
            status = 'screenshot_received'
        WHERE id = ?
    """, (file_id, payment_id))

    conn.commit()
    conn.close()


def mark_payment_submitted(payment_id: int):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        UPDATE payments
        SET status = 'submitted',
            submitted_at = ?
        WHERE id = ?
    """, (datetime.now().isoformat(), payment_id))

    conn.commit()
    conn.close()


def set_payment_admin_message(payment_id: int, admin_message_id: int):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        UPDATE payments
        SET admin_message_id = ?
        WHERE id = ?
    """, (admin_message_id, payment_id))

    conn.commit()
    conn.close()


def mark_payment_promo_sent(payment_id: int, promo_text: str):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        UPDATE payments
        SET status = 'promo_sent',
            promo_sent_text = ?,
            paid_at = ?
        WHERE id = ?
    """, (promo_text, datetime.now().isoformat(), payment_id))

    conn.commit()
    conn.close()


def save_star_payment(user_id: int, plan_key: str, plan_type: str, title: str,
                      duration_days: int, amount_xtr: int,
                      telegram_charge_id: str, provider_charge_id: str):
    conn = get_conn()
    cur = conn.cursor()

    now = datetime.now().isoformat()

    cur.execute("""
        INSERT INTO star_payments (
            user_id,
            plan_key,
            plan_type,
            title,
            duration_days,
            amount_xtr,
            telegram_charge_id,
            provider_charge_id,
            status,
            created_at,
            paid_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'paid', ?, ?)
        RETURNING id
    """, (
        user_id,
        plan_key,
        plan_type,
        title,
        duration_days,
        amount_xtr,
        telegram_charge_id,
        provider_charge_id,
        now,
        now
    ))
    cur.fetchone()

    conn.commit()
    conn.close()


def get_user_daily_limit(user_id: int) -> int:
    user = get_user(user_id)

    if not user:
        return 0

    return 30 if (user["plan"] or "basic").lower() == "vip" else 10


def count_user_photos_today(user_id: int) -> int:
    conn = get_conn()
    cur = conn.cursor()

    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    cur.execute("""
        SELECT daily_usage_reset_at
        FROM users
        WHERE user_id = ?
    """, (user_id,))
    user_row = cur.fetchone()

    reset_point = today_start

    if user_row and user_row["daily_usage_reset_at"]:
        try:
            reset_at = datetime.fromisoformat(user_row["daily_usage_reset_at"])
            if reset_at > reset_point:
                reset_point = reset_at
        except Exception:
            pass

    cur.execute("""
        SELECT COUNT(*) as total
        FROM photo_logs
        WHERE user_id = ? AND created_at >= ?
    """, (user_id, reset_point.isoformat()))
    row = cur.fetchone()

    conn.close()
    return row["total"] if row else 0


def log_user_photo(user_id: int, file_id: str | None = None):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO photo_logs (user_id, file_id, created_at)
        VALUES (?, ?, ?)
        RETURNING id
    """, (
        user_id,
        file_id,
        datetime.now().isoformat()
    ))
    cur.fetchone()

    conn.commit()
    conn.close()


def get_user_remaining_photos_today(user_id: int) -> int:
    daily_limit = get_user_daily_limit(user_id)
    used = count_user_photos_today(user_id)
    remaining = daily_limit - used
    return remaining if remaining > 0 else 0


def count_user_photos_between(user_id: int, start_dt: datetime, end_dt: datetime) -> int:
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT COUNT(*) as total
        FROM photo_logs
        WHERE user_id = ?
          AND created_at >= ?
          AND created_at < ?
    """, (
        user_id,
        start_dt.isoformat(),
        end_dt.isoformat()
    ))
    row = cur.fetchone()

    conn.close()
    return row["total"] if row else 0


def start_trial_mode(user_id: int):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        UPDATE users
        SET trial_started_at = COALESCE(trial_started_at, ?)
        WHERE user_id = ?
    """, (datetime.now().isoformat(), user_id))

    conn.commit()
    conn.close()


def is_trial_available(user_id: int) -> bool:
    user = get_user(user_id)
    if not user:
        return False

    if int(user.get("trial_completed") or 0) == 1:
        return False

    return int(user.get("trial_used_count") or 0) < TRIAL_SCREEN_LIMIT


def get_trial_used_count(user_id: int) -> int:
    user = get_user(user_id)
    if not user:
        return 0
    return int(user.get("trial_used_count") or 0)


def get_trial_remaining(user_id: int) -> int:
    remaining = TRIAL_SCREEN_LIMIT - get_trial_used_count(user_id)
    return remaining if remaining > 0 else 0


def get_trial_start(user_id: int):
    user = get_user(user_id)
    if not user:
        return None

    trial_started_at = user.get("trial_started_at")
    if not trial_started_at:
        return None

    try:
        return datetime.fromisoformat(trial_started_at)
    except Exception:
        return None


def increment_trial_usage(user_id: int):
    conn = get_conn()
    cur = conn.cursor()

    user = get_user(user_id)
    if not user:
        conn.close()
        return

    used = int(user.get("trial_used_count") or 0)
    now_iso = datetime.now().isoformat()

    if not user.get("trial_started_at"):
        cur.execute("""
            UPDATE users
            SET trial_started_at = ?,
                trial_used_count = trial_used_count + 1
            WHERE user_id = ?
        """, (now_iso, user_id))
    else:
        cur.execute("""
            UPDATE users
            SET trial_used_count = trial_used_count + 1
            WHERE user_id = ?
        """, (user_id,))

    used_after = used + 1
    if used_after >= TRIAL_SCREEN_LIMIT:
        cur.execute("""
            UPDATE users
            SET trial_completed = 1
            WHERE user_id = ?
        """, (user_id,))

    conn.commit()
    conn.close()


def complete_trial(user_id: int):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        UPDATE users
        SET trial_completed = 1
        WHERE user_id = ?
    """, (user_id,))

    conn.commit()
    conn.close()


def has_completed_trial(user_id: int) -> bool:
    user = get_user(user_id)
    if not user:
        return False
    return int(user.get("trial_completed") or 0) == 1


def get_active_trial_session(user_id: int):
    return None


def get_or_create_trial_session(user_id: int):
    return None


def count_trial_session_bets(trial_session_id: int) -> int:
    return 0


def add_bet_to_trial_session(trial_session_id: int, user_id: int, bet_id: int):
    return None


def complete_trial_session(trial_session_id: int):
    return None


def get_trial_stats(trial_session_id: int) -> dict:
    return {
        "total_bets": 0,
        "wins": 0,
        "losses": 0,
        "refunds": 0,
        "win_rate": 0.0,
        "avg_odds": 0.0,
        "total_stake": 0.0,
        "net_profit": 0.0,
        "roi": 0.0,
    }


def delete_user_by_id(user_id: int):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        UPDATE users
        SET is_active = 0,
            access_until = NULL,
            trial_started_at = NULL,
            trial_used_count = 0,
            trial_completed = 0,
            promo_offer_used = 0
        WHERE user_id = ?
    """, (user_id,))

    affected = cur.rowcount

    conn.commit()
    conn.close()
    return affected


def delete_user_by_username(username: str):
    conn = get_conn()
    cur = conn.cursor()

    clean_username = username.replace("@", "")

    cur.execute("""
        UPDATE users
        SET is_active = 0,
            access_until = NULL,
            trial_started_at = NULL,
            trial_used_count = 0,
            trial_completed = 0,
            promo_offer_used = 0
        WHERE username = ?
    """, (clean_username,))

    affected = cur.rowcount

    conn.commit()
    conn.close()
    return affected
