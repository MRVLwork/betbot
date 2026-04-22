# -*- coding: utf-8 -*-
from config import TRC20_WALLET


USDT_PLANS = {
    "usdt_basic_month": {
        "plan_name_ua": "Basic 1 місяць",
        "plan_name_ru": "Basic 1 месяц",
        "plan_name_en": "Basic 1 month",
        "plan_type": "basic",
        "duration_days": 30,
        "amount_usd": 5.0,
        "full_amount_usd": 5.0,
        "is_promo": False,
        "wallet_address": TRC20_WALLET,
    },
    "usdt_vip_month_promo": {
        "plan_name_ua": "VIP 1 місяць",
        "plan_name_ru": "VIP 1 месяц",
        "plan_name_en": "VIP 1 month",
        "plan_type": "vip",
        "duration_days": 30,
        "amount_usd": 14.99,
        "full_amount_usd": 19.99,
        "is_promo": True,
        "wallet_address": TRC20_WALLET,
    },
    "usdt_vip_month_full": {
        "plan_name_ua": "VIP 1 місяць",
        "plan_name_ru": "VIP 1 месяц",
        "plan_name_en": "VIP 1 month",
        "plan_type": "vip",
        "duration_days": 30,
        "amount_usd": 19.99,
        "full_amount_usd": 19.99,
        "is_promo": False,
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
        "wallet_address": TRC20_WALLET,
    },
    "usdt_vip_bet_day_month": {
        "plan_name_ua": "VIP ставка дня 1 місяць",
        "plan_name_ru": "VIP ставка дня 1 месяц",
        "plan_name_en": "VIP bet of the day 1 month",
        "plan_type": "vip_bet_day",
        "duration_days": 30,
        "amount_usd": 4.99,
        "full_amount_usd": 4.99,
        "is_promo": False,
        "wallet_address": TRC20_WALLET,
    },
}


def get_usdt_plan(plan_key: str):
    return USDT_PLANS.get(plan_key)


def get_default_usdt_plan_keys():
    return ["usdt_basic_month", "usdt_vip_month_promo"]


def get_renewal_usdt_plan_key(plan_type: str, duration_days: int = 30):
    if plan_type == "vip":
        return "usdt_vip_month_full"
    return "usdt_basic_month"
