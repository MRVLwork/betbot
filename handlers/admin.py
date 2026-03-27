from telegram import Update
from telegram.ext import ContextTypes

from config import ADMIN_ID
from db import (
    create_promo,
    get_all_promos,
    get_all_users,
    get_users_by_promo,
    delete_user_by_id,
    delete_user_by_username,
    get_conn,
)
from services.promo_service import generate_promo_code


def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID


async def addpromo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Немає доступу.")
        return

    if len(context.args) < 4:
        await update.message.reply_text(
            "Формат:\n/addpromo CODE DAYS USES PLAN\n\n"
            "Приклад:\n/addpromo BASIC30 30 1 basic"
        )
        return

    code = context.args[0].strip()
    days = int(context.args[1])
    uses = int(context.args[2])
    plan_type = context.args[3].strip().lower()

    if plan_type not in ("basic", "vip"):
        await update.message.reply_text("PLAN має бути: basic або vip")
        return

    create_promo(code, days, uses, plan_type)

    await update.message.reply_text(
        f"✅ Промокод створено\n\n"
        f"Код: {code}\n"
        f"Днів: {days}\n"
        f"Використань: {uses}\n"
        f"Тариф: {plan_type}"
    )


async def genbasicweek(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    code = generate_promo_code("BASIC7")
    create_promo(code, 7, 1, "basic")
    await update.message.reply_text(f"✅ {code}")


async def genbasicmonth(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    code = generate_promo_code("BASIC30")
    create_promo(code, 30, 1, "basic")
    await update.message.reply_text(f"✅ {code}")


async def genvipweek(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    code = generate_promo_code("VIP7")
    create_promo(code, 7, 1, "vip")
    await update.message.reply_text(f"✅ {code}")


async def genvipmonth(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    code = generate_promo_code("VIP30")
    create_promo(code, 30, 1, "vip")
    await update.message.reply_text(f"✅ {code}")


async def promos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return

    rows = get_all_promos()

    if not rows:
        await update.message.reply_text("Немає промокодів")
        return

    text = "📌 Промокоди:\n\n"
    for row in rows:
        text += (
            f"{row['code']} | {row['plan_type']} | {row['days']} дн | "
            f"{row['uses_left']}/{row['total_uses']}\n"
        )

    await update.message.reply_text(text)


async def users_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return

    rows = get_all_users()

    if not rows:
        await update.message.reply_text("Користувачів немає")
        return

    text = "👥 Користувачі:\n\n"
    for row in rows:
        username = f"@{row['username']}" if row["username"] else "-"
        text += (
            f"{row['user_id']} | {username} | {row['plan']} | "
            f"{row['access_until']}\n"
        )

    await update.message.reply_text(text)


async def promo_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return

    if len(context.args) < 1:
        await update.message.reply_text("Формат: /statspromo CODE")
        return

    code = context.args[0]
    rows = get_users_by_promo(code)

    if not rows:
        await update.message.reply_text("Немає активацій")
        return

    text = f"📊 {code}:\n\n"
    for row in rows:
        username = f"@{row['username']}" if row["username"] else "-"
        text += (
            f"{row['user_id']} | {username} | "
            f"{row['activated_at']} | {row['access_until']}\n"
        )

    await update.message.reply_text(text)


async def delete_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Немає доступу.")
        return

    if len(context.args) < 1:
        await update.message.reply_text(
            "Формат:\n"
            "/deluser user_id\n"
            "/deluser @username"
        )
        return

    target = context.args[0].strip()

    if target.isdigit():
        deleted = delete_user_by_id(int(target))
        if deleted:
            await update.message.reply_text(f"✅ Видалено {target}")
        else:
            await update.message.reply_text("❌ Не знайдено")
        return

    deleted = delete_user_by_username(target)
    if deleted:
        await update.message.reply_text(f"✅ Видалено {target}")
    else:
        await update.message.reply_text("❌ Не знайдено")


async def stars_revenue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT 
            COUNT(*) as total_payments,
            COALESCE(SUM(amount_xtr), 0) as total_stars,
            COALESCE(SUM(CASE WHEN plan_type = 'vip' THEN amount_xtr ELSE 0 END), 0) as vip_stars,
            COALESCE(SUM(CASE WHEN plan_type = 'basic' THEN amount_xtr ELSE 0 END), 0) as basic_stars
        FROM star_payments
    """)
    row = cur.fetchone()

    conn.close()

    await update.message.reply_text(
        f"⭐ Доход зі Stars\n\n"
        f"Платежів: {row['total_payments']}\n"
        f"Всього: {row['total_stars']} ⭐\n\n"
        f"Basic: {row['basic_stars']} ⭐\n"
        f"VIP: {row['vip_stars']} ⭐"
    )