"""Telegram callback handlers."""

from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from .commands import _send_health, _send_profiles


async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.message:
        return

    await query.answer()

    if query.data == "health":
        await _send_health(query.message, context)
    elif query.data == "profiles":
        await _send_profiles(query.message, context)
    else:
        await query.message.reply_text("Неизвестное действие.")
