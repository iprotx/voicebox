"""Inline keyboard builders for main menu and paginated views."""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from .callbacks import build_callback


def main_menu_keyboard() -> InlineKeyboardMarkup:
    """Main bot menu with section shortcuts."""
    rows = [
        [
            InlineKeyboardButton(text="👤 Профили", callback_data=build_callback("profiles", "open")),
            InlineKeyboardButton(text="🎙 Сэмплы", callback_data=build_callback("samples", "open")),
        ],
        [
            InlineKeyboardButton(text="✨ Генерация", callback_data=build_callback("generate", "open")),
            InlineKeyboardButton(text="🕘 История", callback_data=build_callback("history", "open")),
        ],
        [
            InlineKeyboardButton(text="📚 Stories", callback_data=build_callback("stories", "open")),
            InlineKeyboardButton(text="📝 Транскрипция", callback_data=build_callback("transcribe", "open")),
        ],
        [
            InlineKeyboardButton(text="🧠 Модели", callback_data=build_callback("models", "open")),
            InlineKeyboardButton(text="⚙️ Настройки", callback_data=build_callback("settings", "open")),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def paginated_keyboard(section: str, page: int, has_next: bool) -> InlineKeyboardMarkup:
    """Common controls with prev/next/refresh/back actions."""
    prev_page = max(page - 1, 0)
    next_page = page + 1

    nav_row = [
        InlineKeyboardButton(
            text="⬅️ Prev",
            callback_data=build_callback(section, "page", str(prev_page)),
        ),
        InlineKeyboardButton(
            text=f"📄 {page + 1}",
            callback_data=build_callback(section, "noop", str(page)),
        ),
    ]

    if has_next:
        nav_row.append(
            InlineKeyboardButton(
                text="Next ➡️",
                callback_data=build_callback(section, "page", str(next_page)),
            )
        )

    action_row = [
        InlineKeyboardButton(
            text="🔄 Refresh",
            callback_data=build_callback(section, "refresh", str(page)),
        ),
        InlineKeyboardButton(
            text="🏠 Back",
            callback_data=build_callback("menu", "open", "_"),
        ),
    ]

    return InlineKeyboardMarkup(inline_keyboard=[nav_row, action_row])
