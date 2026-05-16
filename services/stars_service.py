# -*- coding: utf-8 -*-
STARS_PLANS = {
    "stars_vip_1m": {
        "title_ua": "VIP 1 місяць",
        "title_ru": "VIP 1 месяц",
        "title_en": "VIP 1 month",
        "plan_type": "vip",
        "duration_days": 30,
        "amount_xtr": 1500,
        "is_promo": False,
        "full_price_xtr": 1500,
    },
    "stars_vip_3m": {
        "title_ua": "VIP 3 місяці (-17%)",
        "title_ru": "VIP 3 месяца (-17%)",
        "title_en": "VIP 3 months (-17%)",
        "plan_type": "vip",
        "duration_days": 90,
        "amount_xtr": 3750,
        "is_promo": False,
        "full_price_xtr": 3750,
    },
    "stars_vip_6m": {
        "title_ua": "VIP 6 місяців (-25%)",
        "title_ru": "VIP 6 месяцев (-25%)",
        "title_en": "VIP 6 months (-25%)",
        "plan_type": "vip",
        "duration_days": 180,
        "amount_xtr": 6750,
        "is_promo": False,
        "full_price_xtr": 6750,
    },
    "stars_vip_signals_10d": {
        "title_ua": "VIP Сигнали 10 днів",
        "title_ru": "VIP Сигналы 10 дней",
        "title_en": "VIP Signals 10 days",
        "plan_type": "vip_signals",
        "duration_days": 10,
        "amount_xtr": 399,
        "is_promo": False,
        "full_price_xtr": 399,
    },
    "stars_basic_month": {
        "title_ua": "Basic 1 місяць",
        "title_ru": "Basic 1 месяц",
        "title_en": "Basic 1 month",
        "plan_type": "basic",
        "duration_days": 30,
        "amount_xtr": 399,
        "is_promo": False,
        "full_price_xtr": 399,
    },
}


def get_stars_plan(plan_key: str):
    return STARS_PLANS.get(plan_key)


def get_default_stars_plan_keys():
    return ["stars_basic_month", "stars_vip_1m"]


def get_renewal_stars_plan_key(plan_type, duration_days=30):
    if plan_type == "vip":
        return "stars_vip_1m"
    return "stars_basic_month"
