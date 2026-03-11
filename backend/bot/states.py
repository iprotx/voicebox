"""FSM states for bot multi-step dialogs."""

from aiogram.fsm.state import State, StatesGroup


class ProfileCreateStates(StatesGroup):
    name = State()
    description = State()
    language = State()


class SampleUploadStates(StatesGroup):
    profile_id = State()
    audio = State()
    reference_text = State()


class GenerateStates(StatesGroup):
    profile_id = State()
    text = State()
    language = State()
    model_size = State()


class ImportExportStates(StatesGroup):
    import_profile = State()
    import_history = State()
    export_target = State()
