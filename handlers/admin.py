# -*- coding: utf-8 -*-
import asyncio
from datetime import datetime, timedelta

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
from keyboards import main_menu_keyboard
from services.promo_service import generate_promo_code


def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID


async def commands_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /commands shows the current admin command list.
    Admin only.
    """
    if not is_admin(update.effective_user.id):
        return

    text = (
        "📋 *АДМІН КОМАНДИ*\n\n"
        "📣 *РОЗСИЛКА ПОВІДОМЛЕНЬ*\n"
        "_Фото можна надсилати як зображення з підписом-командою._\n\n"
        "`/sendbasic /ua <текст>`\n"
        "Розсилка активним Basic юзерам обраної мови.\n\n"
        "`/sendvip /ua <текст>`\n"
        "Розсилка активним VIP юзерам обраної мови.\n\n"
        "`/sendtrial /ua <текст>`\n"
        "Розсилка активним Trial юзерам обраної мови.\n\n"
        "`/sendall /ua <текст>`\n"
        "Розсилка всім юзерам обраної мови, включно без підписки.\n\n"
        "_Мовні теги: /ua /ru /en. Також приймаються /uk, /ukr, /rus, /eng._\n\n"
        "👥 *КОРИСТУВАЧІ*\n\n"
        "`/users`\n"
        "Повний список юзерів: TG ID, нік, підписка, trial статус, витрати, реферал, активність.\n\n"
        "`/deluser <user_id або @username>`\n"
        "Видалити конкретного юзера з БД.\n\n"
        "`/cleanup`\n"
        "Видалити порожніх неактивних юзерів: без trial, оплат, скрінів і ставок.\n\n"
        "🎟 *ПРОМОКОДИ*\n\n"
        "`/addpromo <код> <дні> <кількість> <basic|vip>`\n"
        "Створити промокод. Приклад: `/addpromo BASIC30 30 1 basic`.\n\n"
        "`/promos`\n"
        "Список усіх промокодів.\n\n"
        "`/statspromo <код>`\n"
        "Статистика використання конкретного промокоду.\n\n"
        "`/genbasicweek` `/genbasicmonth`\n"
        "Згенерувати Basic промокод на тиждень або місяць.\n\n"
        "`/genvipweek` `/genvipmonth`\n"
        "Згенерувати VIP промокод на тиждень або місяць.\n\n"
        "🔗 *РЕФЕРАЛЬНІ ПОСИЛАННЯ*\n\n"
        "`/genref <ключ> [опис]`\n"
        "Створити реферальне посилання. Приклад: `/genref tiktok TikTok трафік`.\n\n"
        "`/refs`\n"
        "Список усіх реферальних джерел з кліками.\n\n"
        "`/refstats <ключ>`\n"
        "Детальна статистика по джерелу: юзери, конверсія, дохід.\n\n"
        "💰 *ФІНАНСИ*\n\n"
        "`/stars`\n"
        "Дохід від Telegram Stars.\n\n"
        "⚙️ *СИСТЕМА*\n\n"
        "`/updatemenu`\n"
        "Оновити меню у всіх юзерів.\n\n"
        "`/commands`\n"
        "Показати цей список команд."
    )

    await update.message.reply_text(text, parse_mode="Markdown")


async def update_menu_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Надсилає оновлену клавіатуру всім активним юзерам.
    Використовувати після деплою з новим меню.
    """
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Немає доступу.")
        return

    users = get_all_users()
    sent = 0
    errors = 0

    for user in users:
        try:
            lang = (user.get("lang") or "ua").lower()
            plan = (user.get("plan") or "basic").lower()

            await context.bot.send_message(
                chat_id=user["user_id"],
                text="🔄 Бот оновлено! Нові функції вже доступні.",
                reply_markup=main_menu_keyboard(lang, plan),
            )
            sent += 1
        except Exception:
            errors += 1

    await update.message.reply_text(
        f"✅ Оновлено: {sent}\n❌ Помилок: {errors}"
    )


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


async def _users_list_legacy(update: Update, context: ContextTypes.DEFAULT_TYPE):
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


async def cleanup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /cleanup deletes only empty inactive users:
    no trial, no paid records, no screenshots, no parsed bets.
    """
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Немає доступу.")
        return

    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT u.user_id, u.username, u.first_name
            FROM users u
            WHERE COALESCE(u.is_active, 0) = 0
              AND u.trial_started_at IS NULL
              AND u.activated_at IS NULL
              AND u.activated_by IS NULL
              AND u.access_until IS NULL
              AND NOT EXISTS (
                  SELECT 1 FROM photo_logs pl WHERE pl.user_id = u.user_id
              )
              AND NOT EXISTS (
                  SELECT 1 FROM bets b WHERE b.user_id = u.user_id
              )
              AND NOT EXISTS (
                  SELECT 1 FROM payments p WHERE p.user_id = u.user_id
              )
              AND NOT EXISTS (
                  SELECT 1 FROM star_payments sp WHERE sp.user_id = u.user_id
              )
            ORDER BY u.created_at ASC
        """)
        candidates = cur.fetchall()
    finally:
        conn.close()

    deleted = 0
    errors = 0
    for user in candidates:
        try:
            deleted += 1 if delete_user_by_id(user["user_id"]) else 0
        except Exception as exc:
            errors += 1
            print(f"cleanup delete error for {user['user_id']}: {exc}")

    await update.message.reply_text(
        "✅ Cleanup завершено\n\n"
        f"Знайдено кандидатів: {len(candidates)}\n"
        f"Видалено: {deleted}\n"
        f"Помилок: {errors}\n\n"
        "Умова: без trial, без оплат, без скрінів, без ставок."
    )


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

async def gen_ref(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/genref <key> [description] creates a referral link."""
    if not is_admin(update.effective_user.id):
        return

    if not context.args:
        await update.message.reply_text(
            "Використання:\n"
            "/genref <ключ> [опис]\n\n"
            "Приклад:\n"
            "/genref tiktok\n"
            "/genref caper_x Каппер X\n"
            "/genref insta_ad Реклама в Instagram\n\n"
            "Ключ: тільки латиниця, цифри, _ і -"
        )
        return

    source_key = context.args[0].lower()
    clean_key = source_key.replace("_", "").replace("-", "")
    if not clean_key.isascii() or not clean_key.isalnum():
        await update.message.reply_text(
            "Неправильний ключ.\n"
            "Дозволено тільки латиниця, цифри, _ і -"
        )
        return

    description = " ".join(context.args[1:]) if len(context.args) > 1 else ""

    from db import create_referral_source

    created = create_referral_source(source_key, description)
    bot_username = context.bot.username
    link = f"https://t.me/{bot_username}?start=ref_{source_key}"

    if created:
        msg = (
            "Реферальне посилання створено\n\n"
            f"Ключ: `{source_key}`\n"
            f"Опис: {description or ''}\n\n"
            f"Посилання:\n`{link}`\n\n"
            f"Статистика: /refstats {source_key}"
        )
    else:
        msg = (
            "Посилання вже існує\n\n"
            f"`{link}`\n\n"
            f"Статистика: /refstats {source_key}"
        )

    await update.message.reply_text(msg, parse_mode="Markdown")


async def list_refs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/refs shows all referral sources."""
    if not is_admin(update.effective_user.id):
        return

    from db import get_all_referral_sources

    sources = get_all_referral_sources()
    if not sources:
        await update.message.reply_text(
            "Ще немає реферальних посилань.\n"
            "Створи перше: /genref tiktok"
        )
        return

    lines = ["*Реферальні джерела:*\n"]
    for source in sources:
        key = source["source_key"]
        clicks = source.get("clicks") or 0
        desc = source.get("description") or ""
        lines.append(
            f"`{key}`  {clicks} кліків\n"
            f"{desc}\n"
            f"/refstats {key}"
        )

    await update.message.reply_text("\n\n".join(lines), parse_mode="Markdown")


async def ref_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/refstats <key> shows detailed referral source stats."""
    if not is_admin(update.effective_user.id):
        return

    if not context.args:
        await update.message.reply_text(
            "Використання: /refstats <ключ>\n"
            "Приклад: /refstats tiktok"
        )
        return

    source_key = context.args[0].lower()

    from db import get_referral_source_stats

    stats = get_referral_source_stats(source_key)
    if stats["total_users"] == 0:
        await update.message.reply_text(
            f"Джерело: `{source_key}`\n\n"
            "Поки немає юзерів з цього джерела.",
            parse_mode="Markdown",
        )
        return

    paid_total = stats["basic_active"] + stats["vip_active"]
    conv_rate = round(paid_total / stats["total_users"] * 100, 1)

    summary = (
        f"*Статистика: {source_key}*\n\n"
        f"Всього юзерів: *{stats['total_users']}*\n"
        f"Платних: *{paid_total}* ({conv_rate}%)\n\n"
        "Розподіл:\n"
        f"VIP активні: {stats['vip_active']}\n"
        f"Basic активні: {stats['basic_active']}\n"
        f"Trial активні: {stats['trial_active']}\n"
        f"Trial завершено: {stats['trial_completed_no_paid']}\n"
        f"Не активовано: {stats['no_access']}\n\n"
        "Дохід:\n"
        f"Stars: {stats['stars_total']}\n"
        f"USDT: ${stats['usdt_total']:.2f}"
    )
    await update.message.reply_text(summary, parse_mode="Markdown")

    users_list = stats["users_list"]
    if not users_list:
        return

    chunks = []
    current = []
    for index, user_row in enumerate(users_list, 1):
        username = user_row.get("username")
        if username:
            user_str = f"@{username}"
        elif user_row.get("first_name"):
            user_str = user_row["first_name"]
        else:
            user_str = f"#{user_row['user_id']}"

        line = f"{index}. {user_str} - {user_row['status']}"
        if user_row["stars_spent"] > 0:
            line += f" | {user_row['stars_spent']} Stars"
        if user_row["usdt_spent"] > 0:
            line += f" | ${user_row['usdt_spent']:.2f}"

        current.append(line)
        if len(current) >= 20:
            chunks.append("\n".join(current))
            current = []

    if current:
        chunks.append("\n".join(current))

    for index, chunk in enumerate(chunks, 1):
        prefix = f"Юзери ({index}/{len(chunks)}):\n\n" if len(chunks) > 1 else "Юзери:\n\n"
        await update.message.reply_text(prefix + chunk)


def _parse_broadcast_command(text: str):
    """
    Parse broadcast command with one or more language tags.
    Formats:
    /sendvip /ua message text
    /sendvip /ua /ru message text
    /sendvip /ua /ru /en message text
    Returns (lang, message_text) or (None, None) on error.
    """
    parts = (text or "").strip().split()
    if len(parts) < 2:
        return None, None

    lang_map = {
        "ua": "ua",
        "uk": "ua",
        "ukr": "ua",
        "ru": "ru",
        "rus": "ru",
        "en": "en",
        "eng": "en",
    }

    langs = []
    text_start_idx = 1
    for index in range(1, len(parts)):
        token = parts[index].lower().lstrip("/")
        if parts[index].startswith("/") and token in lang_map:
            mapped = lang_map[token]
            if mapped not in langs:
                langs.append(mapped)
            text_start_idx = index + 1
        else:
            break

    if not langs:
        return None, None

    message_text = " ".join(parts[text_start_idx:]).strip()
    if not message_text:
        return None, None

    return langs, message_text


async def _do_broadcast(
    context,
    sub_filter: str,
    langs: list,
    message_text: str,
    photo_file_id: str = None,
) -> tuple:
    """Send broadcast for multiple languages and return (success, errors, total_users)."""
    from db import get_users_by_subscription_and_lang

    all_user_ids = set()
    for lang in langs:
        user_ids = get_users_by_subscription_and_lang(sub_filter, lang)
        all_user_ids.update(user_ids)

    success = 0
    errors = 0

    for user_id in all_user_ids:
        try:
            if photo_file_id:
                await context.bot.send_photo(
                    chat_id=user_id,
                    photo=photo_file_id,
                    caption=message_text,
                )
            else:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=message_text,
                )
            success += 1
            await asyncio.sleep(0.05)
        except Exception as e:
            errors += 1
            print(f"Broadcast error to {user_id}: {e}")

    return success, errors, len(all_user_ids)


async def _handle_broadcast(update, context, sub_filter: str):
    """Common handler for text and photo broadcasts."""
    if not is_admin(update.effective_user.id):
        return

    message = update.message
    if not message:
        return

    raw_text = message.text or message.caption or ""
    photo_file_id = message.photo[-1].file_id if message.photo else None

    langs, message_text = _parse_broadcast_command(raw_text)
    if not langs or not message_text:
        await message.reply_text(
            "Format:\n"
            "/sendvip /ua <text>\n\n"
            "/sendvip /ua /ru <text>\n"
            "/sendvip /ua /ru /en <text>\n\n"
            "Language tags: /ua /ru /en\n\n"
            "You can specify several tags separated by spaces.\n\n"
            "Examples:\n"
            "/sendvip /ua Hello VIP users!\n"
            "/sendall /ua /ru Message for two languages\n\n"
            "For photo broadcasts, attach an image and put the command in the caption."
        )
        return

    audience_names = {
        "basic": "Basic",
        "vip": "VIP",
        "trial": "Trial",
        "all": "All",
    }
    audience = audience_names.get(sub_filter, sub_filter)
    langs_str = "/".join(lang.upper() for lang in langs)

    status_msg = await message.reply_text(
        f"Broadcast {audience} ({langs_str})...\n"
        f"{'With photo' if photo_file_id else 'Text only'}"
    )

    success, errors, total = await _do_broadcast(
        context,
        sub_filter,
        langs,
        message_text,
        photo_file_id,
    )

    await status_msg.edit_text(
        f"Broadcast completed\n\n"
        f"Audience: {audience} ({langs_str})\n"
        f"Total recipients: {total}\n"
        f"Delivered: {success}\n"
        f"Errors: {errors}"
    )


async def send_basic_broadcast(update, context):
    await _handle_broadcast(update, context, "basic")


async def send_vip_broadcast(update, context):
    await _handle_broadcast(update, context, "vip")


async def send_trial_broadcast(update, context):
    await _handle_broadcast(update, context, "trial")


async def send_all_broadcast(update, context):
    await _handle_broadcast(update, context, "all")

async def users_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /users full users list:
    TG ID | Username | Subscription | Trial | Spent | Referral
    """
    if not is_admin(update.effective_user.id):
        return

    from db import get_users_with_full_info

    users = get_users_with_full_info()

    if not users:
        await update.message.reply_text("Користувачів немає")
        return

    total = len(users)
    cnt_vip = 0
    cnt_basic = 0
    cnt_trial = 0
    cnt_none = 0
    cnt_trial_used = 0
    cnt_referrals = 0
    total_usdt = 0.0
    total_stars = 0
    total_photos = 0
    total_bets = 0

    lines = []
    now = datetime.now()

    for user_row in users:
        uid = user_row["user_id"]
        username = user_row.get("username")
        first_name = user_row.get("first_name")
        plan = (user_row.get("plan") or "").lower()
        is_active = int(user_row.get("is_active") or 0) == 1
        trial_started = user_row.get("trial_started_at")
        trial_expires_at = user_row.get("trial_expires_at")
        trial_completed = int(user_row.get("trial_completed") or 0) == 1
        ref_source = user_row.get("ref_source") or ""
        usdt_total = float(user_row.get("usdt_total") or 0)
        stars_total = int(user_row.get("stars_total") or 0)
        photos_total = int(user_row.get("photos_total") or 0)
        bets_total = int(user_row.get("bets_total") or 0)
        screenshot_status = "✅" if user_row.get("first_screenshot_sent_at") else "—"
        first_bet_status = "✅" if user_row.get("first_bet_saved_at") else "—"

        access_until = user_row.get("access_until") or user_row.get("plan_expires_at")
        has_access = False
        if is_active and access_until:
            try:
                has_access = datetime.fromisoformat(access_until) > now
            except Exception:
                has_access = False

        trial_active = False
        if trial_started and not trial_completed:
            try:
                if trial_expires_at:
                    trial_expires = datetime.fromisoformat(trial_expires_at)
                else:
                    trial_expires = datetime.fromisoformat(trial_started) + timedelta(days=3)
                trial_active = trial_expires > now
            except Exception:
                trial_active = False

        if has_access and plan == "vip":
            subscription = "VIP"
            cnt_vip += 1
        elif has_access:
            subscription = "Basic"
            cnt_basic += 1
        elif trial_active:
            subscription = "Trial"
            cnt_trial += 1
        else:
            subscription = "none"
            cnt_none += 1

        if trial_started:
            trial_status = "trial_active"
            cnt_trial_used += 1
        else:
            trial_status = "trial_none"

        if ref_source:
            ref_str = f"ref: {ref_source}"
            cnt_referrals += 1
        else:
            ref_str = "ref: ні"

        if username:
            user_name = f"@{username}"
        elif first_name:
            user_name = first_name
        else:
            user_name = ""

        spent_parts = []
        if usdt_total > 0:
            spent_parts.append(f"${usdt_total:.2f}")
            total_usdt += usdt_total
        if stars_total > 0:
            spent_parts.append(f"{stars_total} Stars")
            total_stars += stars_total
        spent_str = " + ".join(spent_parts) if spent_parts else "0"
        total_photos += photos_total
        total_bets += bets_total

        line = (
            f"{uid} | {user_name} | {subscription} | "
            f"{trial_status} | Скрін {screenshot_status} | Ставка {first_bet_status} | "
            f"📸 {photos_total}/{bets_total} | "
            f"{spent_str} | {ref_str}"
        )
        lines.append(line)

    summary = (
        f"👥 *Всього юзерів: {total}*\n"
        f"{'-' * 25}\n"
        f"VIP: {cnt_vip}\n"
        f"Basic: {cnt_basic}\n"
        f"Trial: {cnt_trial}\n"
        f"None: {cnt_none}\n\n"
        f"Активували trial: {cnt_trial_used}\n"
        f"Прийшли по рефке: {cnt_referrals}\n\n"
        f"💰 Загальні витрати:\n"
        f"USDT: ${total_usdt:.2f}\n"
        f"Stars: {total_stars}\n\n"
        f"📸 Активність:\n"
        f"Скрінів: {total_photos}\n"
        f"Ставок збережено: {total_bets}\n"
        f"Конверсія: {round(total_bets / total_photos * 100, 1) if total_photos else 0}%\n"
    )

    await update.message.reply_text(summary, parse_mode="Markdown")

    chunk_size = 25
    chunks = [
        lines[i:i + chunk_size]
        for i in range(0, len(lines), chunk_size)
    ]

    for index, chunk in enumerate(chunks, 1):
        prefix = (
            f"📋 Юзери ({index}/{len(chunks)}):\n\n"
            if len(chunks) > 1
            else "📋 Юзери:\n\n"
        )
        text = prefix + "\n".join(chunk)

        if len(text) > 4000:
            text = text[:3997] + "..."

        await update.message.reply_text(text)
