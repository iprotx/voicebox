"""CLI entrypoint for Voicebox Telegram bot."""

from backend.integrations.telegram import start_bot


if __name__ == "__main__":
    start_bot()
