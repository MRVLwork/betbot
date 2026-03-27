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