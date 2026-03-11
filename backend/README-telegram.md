# Telegram интеграция для Voicebox

Этот модуль добавляет Telegram-бота, который работает поверх локального Voicebox API (`http://localhost:17493`).

## Что реализовано

- Модуль `backend/integrations/telegram/`:
  - `bot.py` — инициализация приложения и запуск polling/webhook.
  - `client.py` — async-обертка над локальным API.
  - `keyboards.py` — builders для `InlineKeyboardMarkup` и `ReplyKeyboardMarkup`.
  - `handlers/commands.py` и `handlers/callbacks.py` — команды и callback-обработчики.
- Точка входа: `backend/telegram_main.py`.
- Зависимость Bot API: `python-telegram-bot>=21.0`.

## Переменные окружения

- `TELEGRAM_BOT_TOKEN` *(обязательно)* — токен бота.
- `TELEGRAM_MODE` — `polling` (по умолчанию) или `webhook`.
- `TELEGRAM_WEBHOOK_URL` — обязателен в `webhook` режиме, публичный URL Telegram webhook.
- `TELEGRAM_WEBHOOK_LISTEN` — хост для bind в webhook режиме (по умолчанию `0.0.0.0`).
- `TELEGRAM_WEBHOOK_PORT` — порт для bind в webhook режиме (по умолчанию `8080`).
- `VOICEBOX_API_URL` — URL backend API (по умолчанию `http://localhost:17493`).

## Локальный запуск (polling)

1. Запустите backend API:

```bash
uvicorn backend.main:app --reload --port 17493
```

2. Экспортируйте переменные и запустите бота:

```bash
export TELEGRAM_BOT_TOKEN=<your_bot_token>
export TELEGRAM_MODE=polling
python -m backend.telegram_main
```

Альтернатива из корня репозитория:

```bash
bun run dev:telegram
```

## Запуск в webhook режиме

```bash
export TELEGRAM_BOT_TOKEN=<your_bot_token>
export TELEGRAM_MODE=webhook
export TELEGRAM_WEBHOOK_URL=https://your-domain.tld/telegram/webhook
export TELEGRAM_WEBHOOK_LISTEN=0.0.0.0
export TELEGRAM_WEBHOOK_PORT=8080
python -m backend.telegram_main
```

> Важно: URL должен быть доступен Telegram извне и с корректным TLS-сертификатом.

## Деплой (рекомендации)

- Разверните backend API и Telegram процесс как отдельные сервисы (или процессы в одном окружении).
- Для webhook режима используйте reverse proxy (Nginx/Caddy/Traefik), пробрасывающий HTTPS на `TELEGRAM_WEBHOOK_PORT`.
- Храните токены и URL в секретах платформы (Docker secrets, GitHub Actions secrets, Railway/Render variables и т.д.).
- Для observability добавьте process manager (`systemd`, `supervisord`, PM2, Docker restart policy).

## Проверка

- В Telegram: `/start`, `/health`, `/profiles`.
- Через inline-кнопки меню: `Health` и `Profiles`.
