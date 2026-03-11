"""Keyboard builders for Telegram bot interactions."""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup


def main_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🩺 Health", callback_data="health")],
            [InlineKeyboardButton("👤 Profiles", callback_data="profiles")],
        ]
    )


def quick_actions_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [[KeyboardButton("/health"), KeyboardButton("/profiles")]],
        resize_keyboard=True,
        one_time_keyboard=False,
    )
