# -*- coding: utf-8 -*-
from config import ADMIN_ID
from db import get_user_display_info


def _escape_markdown(text: str) -> str:
    return str(text or "").replace("\\", "\\\\").replace("_", "\\_").replace("*", "\\*").replace("`", "\\`").replace("[", "\\[")


def _activation_text(user_id: int, plan_label: str, payment_method: str = "") -> str:
    user_info = _escape_markdown(get_user_display_info(user_id))
    plan = _escape_markdown(plan_label)
    method_part = f"\n💳 Спосіб: {_escape_markdown(payment_method)}" if payment_method else ""
    return (
        "✅ *Нова активація*\n\n"
        f"👤 Користувач: {user_info}\n"
        f"📦 Підписка: {plan}"
        f"{method_part}"
    )


async def notify_admin_activation(context, user_id: int, plan_label: str, payment_method: str = ""):
    """
    Надсилає адміну сповіщення про активацію підписки.
    plan_label: "Trial 3 дні" / "VIP 1 місяць" / "Basic" тощо.
    payment_method: "Stars" / "USDT" / "Промокод" / "" для trial.
    """
    if not ADMIN_ID:
        return

    try:
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=_activation_text(user_id, plan_label, payment_method),
            parse_mode="Markdown",
        )
    except Exception as e:
        print(f"notify_admin_activation error: {e}")


async def notify_admin_activation_with_bot(bot, user_id: int, plan_label: str, payment_method: str = ""):
    """Webhook-friendly variant when there is no telegram.ext context."""
    if not ADMIN_ID or not bot:
        return

    try:
        await bot.send_message(
            chat_id=ADMIN_ID,
            text=_activation_text(user_id, plan_label, payment_method),
            parse_mode="Markdown",
        )
    except Exception as e:
        print(f"notify_admin_activation_with_bot error: {e}")