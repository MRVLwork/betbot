STARS_PLANS = {
    "stars_basic_week": {
        "title_ua": "Basic 7 днів",
        "title_ru": "Basic 7 дней",
        "title_en": "Basic 7 days",
        "plan_type": "basic",
        "duration_days": 7,
        "amount_xtr": 99,
        "is_promo": True,
        "full_price_xtr": 99,
    },
    "stars_basic_month": {
        "title_ua": "Basic 1 місяць",
        "title_ru": "Basic 1 месяц",
        "title_en": "Basic 1 month",
        "plan_type": "basic",
        "duration_days": 30,
        "amount_xtr": 399,
        "is_promo": True,
        "full_price_xtr": 399,
    },
    "stars_vip_month_promo": {
        "title_ua": "VIP 1 місяць",
        "title_ru": "VIP 1 месяц",
        "title_en": "VIP 1 month",
        "plan_type": "vip",
        "duration_days": 30,
        "amount_xtr": 999,
        "is_promo": True,
        "full_price_xtr": 1500,
    },
    "stars_vip_month_full": {
        "title_ua": "VIP 1 місяць",
        "title_ru": "VIP 1 месяц",
        "title_en": "VIP 1 month",
        "plan_type": "vip",
        "duration_days": 30,
        "amount_xtr": 1500,
        "is_promo": False,
        "full_price_xtr": 1500,
    },
}


def get_stars_plan(plan_key: str):
    return STARS_PLANS.get(plan_key)


def get_default_stars_plan_keys():
    return ["stars_basic_week", "stars_basic_month", "stars_vip_month_promo"]


def get_renewal_stars_plan_key(plan_type: str, duration_days: int = 30):
    if plan_type == "vip":
        return "stars_vip_month_full"
    if duration_days == 7:
        return "stars_basic_week"
    return "stars_basic_month"
