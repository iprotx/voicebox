"""UI helper utilities for safe message updates."""

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message


async def safe_edit_message(
    message: Message,
    text: str,
    reply_markup: InlineKeyboardMarkup | None = None,
) -> None:
    """Edit message when possible, avoiding duplicated spam messages."""
    try:
        await message.edit_text(text=text, reply_markup=reply_markup)
    except TelegramBadRequest as exc:
        # "message is not modified" and similar edit-only errors are safe to ignore.
        if "message is not modified" not in str(exc).lower():
            raise


async def safe_edit_callback(
    query: CallbackQuery,
    text: str,
    reply_markup: InlineKeyboardMarkup | None = None,
) -> None:
    """Edit callback message and answer callback safely."""
    if query.message:
        await safe_edit_message(query.message, text=text, reply_markup=reply_markup)
    await query.answer()
