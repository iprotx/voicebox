# Telegram bot ↔ backend endpoint matrix

Матрица соответствия endpoint-ов из `backend/main.py` и сценариев Telegram-бота.

## 1) Профили / сэмплы

| Сценарий бота | Endpoint | Метод | Назначение |
|---|---|---|---|
| Список профилей | `/profiles` | `GET` | Получить страницу профилей (для paginated списка). |
| Создать профиль | `/profiles` | `POST` | Создание профиля (FSM: name → description → language). |
| Открыть профиль | `/profiles/{profile_id}` | `GET` | Детальный просмотр профиля. |
| Обновить профиль | `/profiles/{profile_id}` | `PUT` | Редактирование параметров профиля. |
| Удалить профиль | `/profiles/{profile_id}` | `DELETE` | Удаление профиля. |
| Импорт профиля | `/profiles/import` | `POST` | Импорт profile zip (FSM import/export). |
| Экспорт профиля | `/profiles/{profile_id}/export` | `GET` | Экспорт profile zip (FSM import/export). |
| Список sample профиля | `/profiles/{profile_id}/samples` | `GET` | Пагинируемый список sample-ов профиля. |
| Добавить sample | `/profiles/{profile_id}/samples` | `POST` | Загрузка audio + reference text (FSM upload sample). |
| Изменить sample | `/profiles/samples/{sample_id}` | `PUT` | Обновить reference text sample-а. |
| Удалить sample | `/profiles/samples/{sample_id}` | `DELETE` | Удалить sample. |
| Получить sample audio | `/samples/{sample_id}` | `GET` | Проигрывание/скачивание sample. |

## 2) Генерация

| Сценарий бота | Endpoint | Метод | Назначение |
|---|---|---|---|
| Синхронная генерация | `/generate` | `POST` | Основной workflow TTS генерации. |
| Потоковая генерация | `/generate/stream` | `POST` | Streaming сценарий для длинного текста/реалтайма. |

## 3) История

| Сценарий бота | Endpoint | Метод | Назначение |
|---|---|---|---|
| Список истории | `/history` | `GET` | Пагинируемый список генераций. |
| Статистика истории | `/history/stats` | `GET` | Summary для карточки раздела. |
| Деталь записи | `/history/{generation_id}` | `GET` | Просмотр конкретной генерации. |
| Удалить запись | `/history/{generation_id}` | `DELETE` | Удаление элемента истории. |
| Экспорт записи (json) | `/history/{generation_id}/export` | `GET` | Экспорт метаданных записи. |
| Экспорт аудио | `/history/{generation_id}/export-audio` | `GET` | Экспорт wav/mp3 результата. |
| Импорт истории | `/history/import` | `POST` | Импорт истории из файла (FSM import/export). |

## 4) Stories

| Сценарий бота | Endpoint | Метод | Назначение |
|---|---|---|---|
| Список stories | `/stories` | `GET` | Пагинация stories. |
| Создать story | `/stories` | `POST` | Создать story. |
| Деталь story | `/stories/{story_id}` | `GET` | Просмотр story и item-ов. |
| Обновить story | `/stories/{story_id}` | `PUT` | Редактирование meta story. |
| Удалить story | `/stories/{story_id}` | `DELETE` | Удаление story. |
| Добавить item | `/stories/{story_id}/items` | `POST` | Добавление сегмента в story. |
| Удалить item | `/stories/{story_id}/items/{item_id}` | `DELETE` | Удаление item. |
| Обновить тайминги item-ов | `/stories/{story_id}/items/times` | `PUT` | Массовое обновление времени. |
| Reorder item-ов | `/stories/{story_id}/items/reorder` | `PUT` | Изменение порядка item-ов. |
| Move item | `/stories/{story_id}/items/{item_id}/move` | `PUT` | Перемещение item на позицию. |
| Trim item | `/stories/{story_id}/items/{item_id}/trim` | `PUT` | Обрезка аудио item-а. |
| Split item | `/stories/{story_id}/items/{item_id}/split` | `POST` | Разбиение item-а. |
| Duplicate item | `/stories/{story_id}/items/{item_id}/duplicate` | `POST` | Дублирование item-а. |
| Экспорт story audio | `/stories/{story_id}/export-audio` | `GET` | Экспорт готовой истории. |

## 5) Транскрипция

| Сценарий бота | Endpoint | Метод | Назначение |
|---|---|---|---|
| Транскрибация файла | `/transcribe` | `POST` | Загрузка аудио и получение текста. |

## 6) Модели

| Сценарий бота | Endpoint | Метод | Назначение |
|---|---|---|---|
| Статус моделей | `/models/status` | `GET` | Показать список и статус загрузки/загрузки в память. |
| Загрузить модель в память | `/models/load` | `POST` | Активировать модель. |
| Выгрузить модель | `/models/unload` | `POST` | Освободить память. |
| Скачать модель | `/models/download` | `POST` | Запуск скачивания модели. |
| Прогресс скачивания | `/models/progress/{model_name}` | `GET` | Показ прогресса download. |
| Удалить модель из кэша | `/models/{model_name}` | `DELETE` | Очистка скачанной модели. |

## Callback data schema

Для inline-кнопок используется versioned формат:

- `v1:section:action:id`
- примеры:
  - `v1:profiles:open:_`
  - `v1:history:page:2`
  - `v1:models:refresh:0`
  - `v1:menu:open:_`
