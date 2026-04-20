# -*- coding: utf-8 -*-
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
    get_basic_bet_day_subscribers,
    get_vip_bet_day_subscribers,
)
from services.promo_service import generate_promo_code

from services.broadcast_service import (
    parse_broadcast_text,
    broadcast_help_text,
    send_broadcast,
    send_photo_broadcast,
)


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

async def send_basic_bet_day(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return

    text = update.message.text.partition(" ")[2].strip()
    if not text:
        await update.message.reply_text("Формат: /sendbasicday текст ставки")
        return

    user_ids = get_basic_bet_day_subscribers()
    sent = 0
    for user_id in user_ids:
        try:
            await context.bot.send_message(chat_id=user_id, text=f"🎯 Basic ставка дня\n\n{text}")
            sent += 1
        except Exception:
            pass

    await update.message.reply_text(f"✅ Відправлено Basic ставку дня: {sent}")


async def admin_basic_bet_day_photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.photo:
        return

    if not is_admin(update.effective_user.id):
        return

    caption = update.message.caption or ""
    if not caption.strip().lower().startswith("/sendbasicday"):
        return

    text = caption.split(maxsplit=1)[1].strip() if len(caption.split(maxsplit=1)) > 1 else ""
    final_caption = f"🎯 Basic ставка дня\n\n{text}" if text else "🎯 Basic ставка дня"

    photo_file_id = update.message.photo[-1].file_id
    user_ids = get_basic_bet_day_subscribers()

    sent = 0
    for user_id in user_ids:
        try:
            await context.bot.send_photo(
                chat_id=user_id,
                photo=photo_file_id,
                caption=final_caption,
            )
            sent += 1
        except Exception:
            pass

    await update.message.reply_text(f"✅ Відправлено Basic ставку дня: {sent}")


async def send_vip_bet_day(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return

    text = update.message.text.partition(" ")[2].strip()
    if not text:
        await update.message.reply_text("Формат: /sendvipday текст ставки")
        return

    user_ids = get_vip_bet_day_subscribers()
    sent = 0
    for user_id in user_ids:
        try:
            await context.bot.send_message(chat_id=user_id, text=f"🔥 VIP ставка дня\n\n{text}")
            sent += 1
        except Exception:
            pass

    await update.message.reply_text(f"✅ Відправлено VIP ставку дня: {sent}")


async def admin_vip_bet_day_photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.photo:
        return

    if not is_admin(update.effective_user.id):
        return

    caption = update.message.caption or ""
    if not caption.strip().lower().startswith("/sendvipday"):
        return

    text = caption.split(maxsplit=1)[1].strip() if len(caption.split(maxsplit=1)) > 1 else ""
    final_caption = f"🔥 VIP ставка дня\n\n{text}" if text else "🔥 VIP ставка дня"

    photo_file_id = update.message.photo[-1].file_id
    user_ids = get_vip_bet_day_subscribers()

    sent = 0
    for user_id in user_ids:
        try:
            await context.bot.send_photo(
                chat_id=user_id,
                photo=photo_file_id,
                caption=final_caption,
            )
            sent += 1
        except Exception:
            pass

    await update.message.reply_text(f"✅ Відправлено VIP ставку дня: {sent}")


async def sendposthelp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    await update.message.reply_text(broadcast_help_text())


async def sendpost(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return

    raw_text = update.message.text or ""
    clean_text, lang_tag, audience_tag = parse_broadcast_text(raw_text)

    if not clean_text:
        await update.message.reply_text("❌ Немає тексту для розсилки.\n\n/sendposthelp")
        return

    sent, failed = await send_broadcast(
        bot=context.bot,
        text=clean_text,
        lang_tag=lang_tag,
        audience_tag=audience_tag,
    )

    await update.message.reply_text(
        f"✅ Розсилка завершена\n\n"
        f"Мова: {lang_tag}\n"
        f"Аудиторія: {audience_tag}\n"
        f"Відправлено: {sent}\n"
        f"Помилки: {failed}"
    )


async def admin_broadcast_photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.photo:
        return

    if not is_admin(update.effective_user.id):
        return

    caption = update.message.caption or ""
    if not caption.strip().lower().startswith("/sendpost"):
        return

    clean_text, lang_tag, audience_tag = parse_broadcast_text(caption)

    if not clean_text:
        await update.message.reply_text("❌ Немає тексту в caption для розсилки.\n\n/sendposthelp")
        return

    photo_file_id = update.message.photo[-1].file_id

    sent, failed = await send_photo_broadcast(
        bot=context.bot,
        photo_file_id=photo_file_id,
        caption=clean_text,
        lang_tag=lang_tag,
        audience_tag=audience_tag,
    )

    await update.message.reply_text(
        f"✅ Фото-розсилка завершена\n\n"
        f"Мова: {lang_tag}\n"
        f"Аудиторія: {audience_tag}\n"
        f"Відправлено: {sent}\n"
        f"Помилки: {failed}"
    )


from services.tools_service import send_day_bet

async def senddaybet(update, context):
    if not is_admin(update.effective_user.id):
        return

    raw = update.message.text or ""
    text = raw.replace("/senddaybet", "").strip()

    lang = "alllangs"
    audience = "basic"

    if "/ua" in text:
        lang = "ua"
    elif "/ru" in text:
        lang = "ru"
    elif "/en" in text:
        lang = "en"

    if "/vip" in text:
        audience = "vip"
    elif "/basic" in text:
        audience = "basic"

    for tag in ["/ua","/ru","/en","/alllangs","/basic","/vip"]:
        text = text.replace(tag, "")

    text = text.strip()

    if not text:
        await update.message.reply_text("❌ Немає тексту")
        return

    sent, errors = await send_day_bet(context.bot, text, lang, audience)

    await update.message.reply_text(
        f"✅ Ставка дня відправлена\n\n"
        f"Мова: {lang}\n"
        f"Аудиторія: {audience}\n"
        f"Відправлено: {sent}\n"
        f"Помилки: {errors}"
    )
