"""Telegram bot application bootstrap and runtime modes."""

from __future__ import annotations

import os
from dataclasses import dataclass
from urllib.parse import urlparse

from telegram.ext import Application, CallbackQueryHandler, CommandHandler

from .client import VoiceboxAPIClient
from .handlers import health_command, menu_callback, profiles_command, start_command


@dataclass
class TelegramRuntimeConfig:
    token: str
    mode: str
    webhook_url: str | None
    listen_host: str
    listen_port: int

    @classmethod
    def from_env(cls) -> "TelegramRuntimeConfig":
        token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
        if not token:
            raise RuntimeError("TELEGRAM_BOT_TOKEN is required")

        mode = os.environ.get("TELEGRAM_MODE", "polling").strip().lower()
        if mode not in {"polling", "webhook"}:
            raise RuntimeError("TELEGRAM_MODE must be polling or webhook")

        webhook_url = os.environ.get("TELEGRAM_WEBHOOK_URL", "").strip() or None
        if mode == "webhook" and not webhook_url:
            raise RuntimeError("TELEGRAM_WEBHOOK_URL is required in webhook mode")

        listen_host = os.environ.get("TELEGRAM_WEBHOOK_LISTEN", "0.0.0.0")
        listen_port = int(os.environ.get("TELEGRAM_WEBHOOK_PORT", "8080"))

        return cls(
            token=token,
            mode=mode,
            webhook_url=webhook_url,
            listen_host=listen_host,
            listen_port=listen_port,
        )


def build_application(config: TelegramRuntimeConfig | None = None) -> Application:
    runtime = config or TelegramRuntimeConfig.from_env()
    application = Application.builder().token(runtime.token).build()

    api_client = VoiceboxAPIClient(
        base_url=os.environ.get("VOICEBOX_API_URL", "http://localhost:17493")
    )
    application.bot_data["voicebox_client"] = api_client

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("health", health_command))
    application.add_handler(CommandHandler("profiles", profiles_command))
    application.add_handler(CallbackQueryHandler(menu_callback))
    return application


def start_bot() -> None:
    runtime = TelegramRuntimeConfig.from_env()
    app = build_application(runtime)

    if runtime.mode == "polling":
        app.run_polling(drop_pending_updates=True)
        return

    parsed = urlparse(runtime.webhook_url or "")
    url_path = parsed.path or f"/{runtime.token}"

    app.run_webhook(
        listen=runtime.listen_host,
        port=runtime.listen_port,
        url_path=url_path,
        webhook_url=runtime.webhook_url,
        drop_pending_updates=True,
    )
