"""Bot handlers with section navigation, pagination and FSM entrypoints."""

from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from .callbacks import CallbackError, build_callback, parse_callback
from .keyboards import main_menu_keyboard, paginated_keyboard
from .states import GenerateStates, ImportExportStates, ProfileCreateStates, SampleUploadStates
from .ui import safe_edit_callback

router = Router()
PAGE_SIZE = 5

SECTION_TITLES = {
    "profiles": "👤 Профили",
    "samples": "🎙 Сэмплы",
    "generate": "✨ Генерация",
    "history": "🕘 История",
    "stories": "📚 Stories",
    "transcribe": "📝 Транскрипция",
    "models": "🧠 Модели",
    "settings": "⚙️ Настройки",
}


@router.message(CommandStart())
async def start_handler(message: Message) -> None:
    await message.answer(
        "Главное меню Voicebox Bot. Выберите раздел:",
        reply_markup=main_menu_keyboard(),
    )


@router.callback_query(F.data.startswith("v1:"))
async def callback_router(query: CallbackQuery, state: FSMContext) -> None:
    try:
        payload = parse_callback(query.data or "")
    except CallbackError:
        await query.answer("Некорректный callback", show_alert=True)
        return

    if payload.section == "menu":
        await safe_edit_callback(
            query,
            "Главное меню Voicebox Bot. Выберите раздел:",
            reply_markup=main_menu_keyboard(),
        )
        return

    if payload.action in {"open", "refresh", "page"}:
        page = int(payload.item_id) if payload.action == "page" and payload.item_id.isdigit() else 0
        await render_section(query, payload.section, page)
        return

    if payload.action == "create_profile":
        await state.set_state(ProfileCreateStates.name)
        await safe_edit_callback(query, "Введите название нового профиля:")
        return

    if payload.action == "upload_sample":
        await state.set_state(SampleUploadStates.profile_id)
        await safe_edit_callback(query, "Введите ID профиля для загрузки sample:")
        return

    if payload.action == "generate_text":
        await state.set_state(GenerateStates.profile_id)
        await safe_edit_callback(query, "Введите ID профиля для генерации:")
        return

    if payload.action == "import_export":
        await state.set_state(ImportExportStates.export_target)
        await safe_edit_callback(query, "Выберите import/export сценарий (profiles/history).")
        return

    await query.answer("Действие пока не поддерживается")


async def render_section(query: CallbackQuery, section: str, page: int) -> None:
    title = SECTION_TITLES.get(section, "Раздел")
    offset = page * PAGE_SIZE
    header = f"{title}\nСтраница: {page + 1} (offset={offset}, limit={PAGE_SIZE})"

    context_rows = [
        f"• {title} → список/обновление/пагинация",
        f"• callback schema: {build_callback(section, 'open', '_')}",
    ]

    context_actions = [
        ("➕ Создать", build_callback(section, "create_profile", str(page))),
        ("📤 Import/Export", build_callback(section, "import_export", str(page))),
        ("🎛 Действие", build_callback(section, "generate_text", str(page))),
    ]

    from aiogram.types import InlineKeyboardButton

    custom_row = [
        InlineKeyboardButton(text=label, callback_data=data)
        for label, data in context_actions
    ]

    base_markup = paginated_keyboard(section=section, page=page, has_next=True)
    composed_keyboard = [custom_row]
    composed_keyboard.extend(base_markup.inline_keyboard)
    base_markup.inline_keyboard = composed_keyboard

    await safe_edit_callback(query, f"{header}\n" + "\n".join(context_rows), reply_markup=base_markup)


@router.message(ProfileCreateStates.name)
async def profile_name_step(message: Message, state: FSMContext) -> None:
    await state.update_data(name=(message.text or "").strip())
    await state.set_state(ProfileCreateStates.description)
    await message.answer("Введите описание профиля (или '-' чтобы пропустить):")


@router.message(ProfileCreateStates.description)
async def profile_description_step(message: Message, state: FSMContext) -> None:
    text = (message.text or "").strip()
    await state.update_data(description=None if text == "-" else text)
    await state.set_state(ProfileCreateStates.language)
    await message.answer("Введите язык профиля (en/ru/zh/...):")


@router.message(ProfileCreateStates.language)
async def profile_language_step(message: Message, state: FSMContext) -> None:
    await state.update_data(language=(message.text or "en").strip())
    data = await state.get_data()
    await state.clear()
    await message.answer(f"Профиль подготовлен к созданию: {data}")


@router.message(SampleUploadStates.profile_id)
async def sample_profile_step(message: Message, state: FSMContext) -> None:
    await state.update_data(profile_id=(message.text or "").strip())
    await state.set_state(SampleUploadStates.audio)
    await message.answer("Отправьте аудио-файл sample.")


@router.message(SampleUploadStates.audio)
async def sample_audio_step(message: Message, state: FSMContext) -> None:
    await state.update_data(audio_file_id=(message.audio.file_id if message.audio else None))
    await state.set_state(SampleUploadStates.reference_text)
    await message.answer("Введите reference text для sample:")


@router.message(SampleUploadStates.reference_text)
async def sample_text_step(message: Message, state: FSMContext) -> None:
    await state.update_data(reference_text=(message.text or "").strip())
    data = await state.get_data()
    await state.clear()
    await message.answer(f"Sample готов к отправке в /profiles/{{id}}/samples: {data}")


@router.message(GenerateStates.profile_id)
async def generate_profile_step(message: Message, state: FSMContext) -> None:
    await state.update_data(profile_id=(message.text or "").strip())
    await state.set_state(GenerateStates.text)
    await message.answer("Введите текст для генерации:")


@router.message(GenerateStates.text)
async def generate_text_step(message: Message, state: FSMContext) -> None:
    await state.update_data(text=(message.text or "").strip())
    await state.set_state(GenerateStates.language)
    await message.answer("Введите язык (en/ru/zh/...):")


@router.message(GenerateStates.language)
async def generate_language_step(message: Message, state: FSMContext) -> None:
    await state.update_data(language=(message.text or "en").strip())
    await state.set_state(GenerateStates.model_size)
    await message.answer("Введите размер модели (1.7B/0.6B):")


@router.message(GenerateStates.model_size)
async def generate_model_step(message: Message, state: FSMContext) -> None:
    await state.update_data(model_size=(message.text or "1.7B").strip())
    data = await state.get_data()
    await state.clear()
    await message.answer(f"Запрос готов к /generate или /generate/stream: {data}")


@router.message(ImportExportStates.export_target)
async def import_export_step(message: Message, state: FSMContext) -> None:
    target = (message.text or "").strip().lower()
    if target == "profiles":
        await state.set_state(ImportExportStates.import_profile)
        await message.answer("Отправьте zip для /profiles/import.")
        return
    if target == "history":
        await state.set_state(ImportExportStates.import_history)
        await message.answer("Отправьте json/csv для /history/import.")
        return

    await message.answer("Неизвестный target. Введите profiles или history.")


@router.message(ImportExportStates.import_profile)
async def import_profile_step(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Импорт профиля поставлен в очередь.")


@router.message(ImportExportStates.import_history)
async def import_history_step(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Импорт истории поставлен в очередь.")
