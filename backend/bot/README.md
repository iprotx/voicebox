# Voicebox Telegram Bot (aiogram)

## Что реализовано

- Главное меню с `InlineKeyboardMarkup` и emoji-иконографикой.
- Разделы: Профили, Сэмплы, Генерация, История, Stories, Транскрипция, Модели, Настройки.
- Общий paginated паттерн с `next/prev`, `refresh`, `back`.
- Versioned callback schema: `v1:section:action:id`.
- FSM-диалоги для:
  - создания профиля,
  - загрузки sample,
  - генерации текста,
  - import/export сценариев.
- Safe edit-message паттерн (обновление текущего сообщения вместо спама новыми).

## Запуск

```bash
export TELEGRAM_BOT_TOKEN=<token>
python -m backend.bot.app
```

## Файлы

- `callbacks.py` — схема callback и парсинг.
- `keyboards.py` — главное меню и пагинация.
- `handlers.py` — роутинг callback-ов и FSM шаги.
- `states.py` — `StatesGroup` для многошаговых операций.
- `ui.py` — безопасный edit-message helper.
