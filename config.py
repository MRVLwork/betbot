# -*- coding: utf-8 -*-
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()

_admin_raw = os.getenv("ADMIN_ID", "0").strip()
ADMIN_ID = int(_admin_raw) if _admin_raw.isdigit() else 0

TRC20_WALLET = os.getenv("TRC20_WALLET", "").strip()

# PostgreSQL only
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost").strip()
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", "5432").strip())
POSTGRES_DB = os.getenv("POSTGRES_DB", "betbot").strip()
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres").strip()
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "").strip()

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
OPENAI_MODEL_BASIC = os.getenv("OPENAI_MODEL_BASIC", "gpt-4.1-mini").strip()
OPENAI_MODEL_ANALYSIS = os.getenv("OPENAI_MODEL_ANALYSIS", "gpt-5.4-mini").strip()


def _int_env(name: str, default: int) -> int:
    raw = (os.getenv(name, str(default)) or str(default)).strip()
    try:
        return int(raw)
    except ValueError:
        return default


# Match analysis limits
ANALYSIS_LIMIT_BASIC = _int_env("ANALYSIS_LIMIT_BASIC", 3)
ANALYSIS_LIMIT_VIP = _int_env("ANALYSIS_LIMIT_VIP", 10)
ANALYSIS_LIMIT_TRIAL = _int_env("ANALYSIS_LIMIT_TRIAL", 3)

CRYPTOBOT_TOKEN = os.getenv("CRYPTOBOT_TOKEN", "").strip()
CRYPTOBOT_API_URL = "https://pay.crypt.bot/api"
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "").strip()
