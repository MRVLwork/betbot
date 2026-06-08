# -*- coding: utf-8 -*-
from config import TRC20_WALLET


USDT_PLANS = {
    "usdt_basic_month": {
        "plan_name_ua": "Basic 1 місяць",
        "plan_name_ru": "Basic 1 месяц",
        "plan_name_en": "Basic 1 month",
        "plan_type": "basic",
        "duration_days": 30,
        "amount_usd": 7.0,
        "full_amount_usd": 7.0,
        "is_promo": False,
        "first_payment_only": False,
        "wallet_address": TRC20_WALLET,
    },
    "usdt_vip_month": {
        "plan_name_ua": "VIP 1 місяць",
        "plan_name_ru": "VIP 1 месяц",
        "plan_name_en": "VIP 1 month",
        "plan_type": "vip",
        "duration_days": 30,
        "amount_usd": 19.99,
        "full_amount_usd": 19.99,
        "is_promo": False,
        "first_payment_only": False,
        "wallet_address": TRC20_WALLET,
    },
    "usdt_basic_6m_promo": {
        "plan_name_ua": "Basic 6 місяців (-29%)",
        "plan_name_ru": "Basic 6 месяцев (-29%)",
        "plan_name_en": "Basic 6 months (-29%)",
        "plan_type": "basic",
        "duration_days": 180,
        "amount_usd": 30.0,
        "full_amount_usd": 42.0,
        "is_promo": True,
        "first_payment_only": True,
        "discount_percent": 29,
        "wallet_address": TRC20_WALLET,
    },
    "usdt_vip_3m_promo": {
        "plan_name_ua": "VIP 3 місяці (-17%)",
        "plan_name_ru": "VIP 3 месяца (-17%)",
        "plan_name_en": "VIP 3 months (-17%)",
        "plan_type": "vip",
        "duration_days": 90,
        "amount_usd": 50.0,
        "full_amount_usd": 59.97,
        "is_promo": True,
        "first_payment_only": True,
        "discount_percent": 17,
        "wallet_address": TRC20_WALLET,
    },
    "usdt_vip_6m_promo": {
        "plan_name_ua": "VIP 6 місяців (-25%)",
        "plan_name_ru": "VIP 6 месяцев (-25%)",
        "plan_name_en": "VIP 6 months (-25%)",
        "plan_type": "vip",
        "duration_days": 180,
        "amount_usd": 89.99,
        "full_amount_usd": 119.94,
        "is_promo": True,
        "first_payment_only": True,
        "discount_percent": 25,
        "wallet_address": TRC20_WALLET,
    },
    "usdt_vip_signals_10d": {
        "plan_name_ua": "VIP Сигнали 10 днів",
        "plan_name_ru": "VIP Сигналы 10 дней",
        "plan_name_en": "VIP Signals 10 days",
        "plan_type": "vip_signals",
        "duration_days": 10,
        "amount_usd": 5.0,
        "full_amount_usd": 5.0,
        "is_promo": False,
        "first_payment_only": False,
        "wallet_address": TRC20_WALLET,
    },
}


def get_usdt_plan(plan_key: str):
    return USDT_PLANS.get(plan_key)


def get_default_usdt_plan_keys():
    return ["usdt_basic_month", "usdt_vip_month"]


def get_renewal_usdt_plan_key(plan_type: str, duration_days: int = 30):
    if plan_type == "vip":
        return "usdt_vip_month"
    return "usdt_basic_month"
