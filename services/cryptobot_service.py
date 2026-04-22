import hashlib
import hmac
import json
from datetime import datetime

import aiohttp

from config import CRYPTOBOT_API_URL, CRYPTOBOT_TOKEN, WEBHOOK_SECRET


async def create_invoice(
    user_id: int,
    plan_key: str,
    amount_usd: float,
    plan_name: str,
    lang: str = "ua",
) -> dict:
    """
    Create a CryptoBot invoice.
    Returns {ok, pay_url, invoice_id} or {ok: False, error}.
    """
    if not CRYPTOBOT_TOKEN:
        return {"ok": False, "error": "CRYPTOBOT_TOKEN not set"}

    descriptions = {
        "ua": f"Bet Tracker Bot - {plan_name}",
        "ru": f"Bet Tracker Bot - {plan_name}",
        "en": f"Bet Tracker Bot - {plan_name}",
    }

    payload_data = json.dumps({
        "user_id": user_id,
        "plan_key": plan_key,
        "amount": amount_usd,
    })

    try:
        async with aiohttp.ClientSession() as session:
            response = await session.post(
                f"{CRYPTOBOT_API_URL}/createInvoice",
                headers={"Crypto-Pay-API-Token": CRYPTOBOT_TOKEN},
                json={
                    "asset": "USDT",
                    "amount": str(amount_usd),
                    "description": descriptions.get(lang, descriptions["en"]),
                    "payload": payload_data,
                    "paid_btn_name": "openBot",
                    "paid_btn_url": "https://t.me/bet_tracker_stats_bot",
                    "expires_in": 3600,
                    "allow_comments": False,
                    "allow_anonymous": False,
                },
            )
            data = await response.json()

        if data.get("ok"):
            result = data["result"]
            return {
                "ok": True,
                "pay_url": result["pay_url"],
                "invoice_id": result["invoice_id"],
                "bot_invoice_url": result.get("bot_invoice_url", result["pay_url"]),
            }

        return {"ok": False, "error": str(data.get("error", {}))}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


async def get_invoice_status(invoice_id: int) -> dict:
    """
    Check invoice status.
    Returns {ok, status, paid} where status is active/paid/expired.
    """
    if not CRYPTOBOT_TOKEN:
        return {"ok": False, "error": "CRYPTOBOT_TOKEN not set"}

    try:
        async with aiohttp.ClientSession() as session:
            response = await session.get(
                f"{CRYPTOBOT_API_URL}/getInvoices",
                headers={"Crypto-Pay-API-Token": CRYPTOBOT_TOKEN},
                params={"invoice_ids": str(invoice_id)},
            )
            data = await response.json()

        if data.get("ok") and data["result"]["items"]:
            invoice = data["result"]["items"][0]
            payload_raw = invoice.get("payload") or "{}"
            try:
                payload = json.loads(payload_raw)
            except Exception:
                payload = {}
            return {
                "ok": True,
                "status": invoice["status"],
                "paid": invoice["status"] == "paid",
                "amount": invoice.get("amount"),
                "paid_at": invoice.get("paid_at"),
                "payload": payload,
                "plan_key": payload.get("plan_key"),
                "user_id": payload.get("user_id"),
            }
        return {"ok": False, "error": "Invoice not found"}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def verify_webhook_signature(body: bytes, signature: str) -> bool:
    """Verify CryptoBot webhook signature."""
    if not CRYPTOBOT_TOKEN or not signature:
        return False

    secret = hashlib.sha256(CRYPTOBOT_TOKEN.encode()).digest()
    expected = hmac.new(secret, body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


def parse_webhook_payload(body: bytes) -> dict:
    """
    Parse CryptoBot webhook body.
    Returns {user_id, plan_key, amount, invoice_id}.
    """
    try:
        data = json.loads(body)

        if data.get("update_type") != "invoice_paid":
            return {"ok": False, "reason": "not_paid"}

        invoice = data.get("payload", {})
        raw_payload = invoice.get("payload", "{}")
        payload = json.loads(raw_payload)

        return {
            "ok": True,
            "user_id": int(payload["user_id"]),
            "plan_key": payload["plan_key"],
            "amount": float(payload["amount"]),
            "invoice_id": invoice.get("invoice_id"),
            "paid_at": invoice.get("paid_at", datetime.now().isoformat()),
            "webhook_secret": WEBHOOK_SECRET,
        }
    except Exception as exc:
        return {"ok": False, "error": str(exc)}
