"""Callback data schema helpers for Telegram inline buttons."""

from dataclasses import dataclass

CALLBACK_VERSION = "v1"


@dataclass(frozen=True)
class CallbackPayload:
    """Structured callback payload: v1:section:action:id."""

    section: str
    action: str
    item_id: str = "_"

    def pack(self) -> str:
        return f"{CALLBACK_VERSION}:{self.section}:{self.action}:{self.item_id}"


class CallbackError(ValueError):
    """Raised when callback payload is malformed."""


def build_callback(section: str, action: str, item_id: str = "_") -> str:
    """Create versioned callback data string."""
    return CallbackPayload(section=section, action=action, item_id=item_id).pack()


def parse_callback(raw: str) -> CallbackPayload:
    """Parse callback data string into structured payload."""
    parts = raw.split(":", maxsplit=3)
    if len(parts) != 4:
        raise CallbackError("Expected 4 callback parts")

    version, section, action, item_id = parts
    if version != CALLBACK_VERSION:
        raise CallbackError(f"Unsupported callback version: {version}")

    if not section or not action:
        raise CallbackError("Section and action are required")

    return CallbackPayload(section=section, action=action, item_id=item_id or "_")
