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
            promo_offer_used INTEGER DEFAULT 0,
            bet_day_basic_subscribed INTEGER DEFAULT 0,
            bet_day_vip_subscribed INTEGER DEFAULT 0,
            vip_bet_day_until TEXT,
            ai_daily_used INTEGER DEFAULT 0,
            ai_daily_reset_at TEXT
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
    add_column_if_not_exists("users", "bet_day_basic_subscribed", "INTEGER DEFAULT 0")
    add_column_if_not_exists("users", "bet_day_vip_subscribed", "INTEGER DEFAULT 0")
    add_column_if_not_exists("users", "vip_bet_day_until", "TEXT")
    add_column_if_not_exists("users", "ai_daily_used", "INTEGER DEFAULT 0")
    add_column_if_not_exists("users", "ai_daily_reset_at", "TEXT")

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
                promo_offer_used,
                bet_day_basic_subscribed,
                bet_day_vip_subscribed,
                vip_bet_day_until,
                ai_daily_used,
                ai_daily_reset_at
            )
            VALUES (?, ?, ?, 0, NULL, NULL, NULL, ?, 'basic', NULL, ?, NULL, 0, 0, 0, 0, 0, NULL, 0, NULL)
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
            SET username = ?, first_name = ?, lang = ?
            WHERE user_id = ?
        """, (
            user.username,
            user.first_name,
            lang,
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




def subscribe_bet_day_basic(user_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        UPDATE users
        SET bet_day_basic_subscribed = 1
        WHERE user_id = ?
    """, (user_id,))
    conn.commit()
    conn.close()


def subscribe_bet_day_vip(user_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        UPDATE users
        SET bet_day_vip_subscribed = 1
        WHERE user_id = ?
    """, (user_id,))
    conn.commit()
    conn.close()


def is_subscribed_bet_day_basic(user_id: int) -> bool:
    user = get_user(user_id)
    if not user:
        return False
    return int(user.get("bet_day_basic_subscribed") or 0) == 1


def is_subscribed_bet_day_vip(user_id: int) -> bool:
    user = get_user(user_id)
    if not user:
        return False
    return int(user.get("bet_day_vip_subscribed") or 0) == 1


def activate_vip_bet_day_access(user_id: int, days: int = 30):
    conn = get_conn()
    cur = conn.cursor()
    user = get_user(user_id)
    now = datetime.now()

    base_time = now
    if user and user.get("vip_bet_day_until"):
        try:
            current_until = datetime.fromisoformat(user["vip_bet_day_until"])
            if current_until > now:
                base_time = current_until
        except Exception:
            pass

    new_until = base_time + timedelta(days=days)

    cur.execute("""
        UPDATE users
        SET vip_bet_day_until = ?
        WHERE user_id = ?
    """, (new_until.isoformat(), user_id))
    conn.commit()
    conn.close()


def has_vip_bet_day_access(user_id: int) -> bool:
    user = get_user(user_id)
    if not user:
        return False

    if (user.get("plan") or "").lower() == "vip" and user_has_access(user_id):
        return True

    vip_bet_day_until = user.get("vip_bet_day_until")
    if not vip_bet_day_until:
        return False

    try:
        return datetime.fromisoformat(vip_bet_day_until) > datetime.now()
    except Exception:
        return False


def get_basic_bet_day_subscribers():
    conn = get_conn()
    cur = conn.cursor()
    now_iso = datetime.now().isoformat()

    cur.execute("""
        SELECT user_id
        FROM users
        WHERE bet_day_basic_subscribed = 1
          AND is_active = 1
          AND access_until IS NOT NULL
          AND access_until > ?
    """, (now_iso,))
    rows = cur.fetchall()
    conn.close()
    return [row["user_id"] for row in rows]


def get_vip_bet_day_subscribers():
    conn = get_conn()
    cur = conn.cursor()
    now_iso = datetime.now().isoformat()

    cur.execute("""
        SELECT user_id
        FROM users
        WHERE bet_day_vip_subscribed = 1
          AND (
              (is_active = 1 AND plan = 'vip' AND access_until IS NOT NULL AND access_until > ?)
              OR
              (vip_bet_day_until IS NOT NULL AND vip_bet_day_until > ?)
          )
    """, (now_iso, now_iso))
    rows = cur.fetchall()
    conn.close()
    return [row["user_id"] for row in rows]


def reset_ai_usage_if_needed(user_id: int):
    user = get_user(user_id)
    if not user:
        return

    now = datetime.now()
    reset_at_raw = user.get("ai_daily_reset_at")
    if reset_at_raw:
        try:
            reset_at = datetime.fromisoformat(reset_at_raw)
            if reset_at.date() == now.date():
                return
        except Exception:
            pass

    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        UPDATE users
        SET ai_daily_used = 0,
            ai_daily_reset_at = ?
        WHERE user_id = ?
    """, (now.isoformat(), user_id))
    conn.commit()
    conn.close()


def get_ai_daily_remaining(user_id: int) -> int:
    user = get_user(user_id)
    if not user:
        return 0

    if (user.get("plan") or "").lower() == "vip":
        return 999999

    reset_ai_usage_if_needed(user_id)
    user = get_user(user_id)
    used = int(user.get("ai_daily_used") or 0)
    remaining = 1 - used
    return remaining if remaining > 0 else 0


def increment_ai_daily_usage(user_id: int):
    reset_ai_usage_if_needed(user_id)
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        UPDATE users
        SET ai_daily_used = COALESCE(ai_daily_used, 0) + 1,
            ai_daily_reset_at = COALESCE(ai_daily_reset_at, ?)
        WHERE user_id = ?
    """, (datetime.now().isoformat(), user_id))
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


def _resolve_user_sub_type(row: dict) -> str:
    plan = (row.get("plan") or "").lower()
    has_active_access = _row_has_active_access(row)
    stars_spent = int(row.get("stars_spent") or 0)
    usdt_spent = float(row.get("usdt_spent") or 0)
    had_any_paid_access = bool(
        stars_spent > 0
        or usdt_spent > 0
        or row.get("activated_by")
        or row.get("activated_at")
        or row.get("access_until")
    )

    if has_active_access and plan == "vip":
        return "vip"
    if has_active_access and plan == "basic":
        return "basic"
    if had_any_paid_access:
        return "endsub"
    return "trial"


def get_all_users(limit: int = 100):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            u.user_id,
            u.username,
            u.first_name,
            u.is_active,
            u.access_until,
            u.activated_by,
            u.activated_at,
            u.plan,
            u.lang,
            COALESCE((
                SELECT SUM(sp.amount_xtr)
                FROM star_payments sp
                WHERE sp.user_id = u.user_id
                  AND COALESCE(sp.status, 'paid') = 'paid'
            ), 0) AS stars_spent,
            COALESCE((
                SELECT SUM(p.amount_usd)
                FROM payments p
                WHERE p.user_id = u.user_id
                  AND p.status = 'promo_sent'
            ), 0) AS usdt_spent
        FROM users u
        ORDER BY u.created_at DESC
        LIMIT ?
    """, (limit,))
    rows = cur.fetchall()
    conn.close()

    prepared = []
    for row in rows:
        row["lang"] = _normalize_lang_code(row.get("lang"))
        row["sub_type"] = _resolve_user_sub_type(row)
        prepared.append(row)

    return prepared


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
            promo_offer_used = 0,
            bet_day_basic_subscribed = 0,
            bet_day_vip_subscribed = 0,
            vip_bet_day_until = NULL,
            ai_daily_used = 0,
            ai_daily_reset_at = NULL
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
            promo_offer_used = 0,
            bet_day_basic_subscribed = 0,
            bet_day_vip_subscribed = 0,
            vip_bet_day_until = NULL,
            ai_daily_used = 0,
            ai_daily_reset_at = NULL
        WHERE username = ?
    """, (clean_username,))

    affected = cur.rowcount

    conn.commit()
    conn.close()
    return affected


def _normalize_lang_code(lang: str) -> str:
    lang = (lang or "en").lower()
    if lang.startswith("uk") or lang.startswith("ua"):
        return "ua"
    if lang.startswith("ru"):
        return "ru"
    return "en"


def _row_has_active_access(user_row: dict) -> bool:
    if not user_row:
        return False
    if not user_row.get("is_active"):
        return False
    if not user_row.get("access_until"):
        return False
    try:
        return datetime.fromisoformat(user_row["access_until"]) > datetime.now()
    except Exception:
        return False


def get_broadcast_recipients(lang_tag: str = "alllangs", audience_tag: str = "all") -> list[int]:
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT user_id, lang, plan, is_active, access_until
        FROM users
    """)
    rows = cur.fetchall()
    conn.close()

    recipients = []
    lang_tag = (lang_tag or "alllangs").lower()
    audience_tag = (audience_tag or "all").lower()

    for row in rows:
        user_id = row["user_id"]
        user_lang = (row.get("lang") or "en").lower()
        plan = (row.get("plan") or "").lower()
        is_active = row.get("is_active")
        access_until = row.get("access_until")

        # перевірка активності
        has_active_access = False
        if is_active and access_until:
            try:
                from datetime import datetime
                has_active_access = datetime.fromisoformat(access_until) > datetime.now()
            except:
                has_active_access = False

        # фільтр по мові
        if lang_tag != "alllangs" and user_lang != lang_tag:
            continue

        # фільтр по аудиторії
        if audience_tag == "trial":
            if has_active_access:
                continue

        elif audience_tag == "basic":
            if not has_active_access or plan != "basic":
                continue

        elif audience_tag == "vip":
            if not has_active_access or plan != "vip":
                continue

        elif audience_tag == "all":
            if not has_active_access:
                continue

        recipients.append(user_id)

    return recipients
