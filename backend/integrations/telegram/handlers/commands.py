"""Telegram command handlers."""

from __future__ import annotations

from telegram import Message, Update
from telegram.ext import ContextTypes

from ..client import VoiceboxAPIClient
from ..keyboards import main_menu_keyboard, quick_actions_keyboard


def _client(context: ContextTypes.DEFAULT_TYPE) -> VoiceboxAPIClient:
    return context.application.bot_data["voicebox_client"]


async def _send_health(message: Message, context: ContextTypes.DEFAULT_TYPE) -> None:
    client = _client(context)
    health = await client.health()
    status = health.get("status", "unknown")
    model_loaded = health.get("model_loaded", False)
    backend_type = health.get("backend_type", "n/a")
    await message.reply_text(
        f"status: {status}\nmodel_loaded: {model_loaded}\nbackend: {backend_type}"
    )


async def _send_profiles(message: Message, context: ContextTypes.DEFAULT_TYPE) -> None:
    client = _client(context)
    profiles = await client.list_profiles()

    if not profiles:
        await message.reply_text("Профили не найдены.")
        return

    lines = [f"• {item['name']} ({item['id']})" for item in profiles[:20]]
    await message.reply_text("Доступные профили:\n" + "\n".join(lines))


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    await update.message.reply_text(
        "Voicebox Telegram bot готов. Выберите действие:",
        reply_markup=main_menu_keyboard(),
    )
    await update.message.reply_text(
        "Быстрые команды:",
        reply_markup=quick_actions_keyboard(),
    )


async def health_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message:
        await _send_health(update.message, context)


async def profiles_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message:
        await _send_profiles(update.message, context)
