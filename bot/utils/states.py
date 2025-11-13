from aiogram.fsm.state import State, StatesGroup

class RegistrationStates(StatesGroup):
    waiting_for_phone = State()
    waiting_for_role = State()
    waiting_for_role_change = State()

class AdminStates(StatesGroup):
    waiting_for_user_data = State()
    waiting_for_role_change = State()
    waiting_for_full_name = State()
    waiting_for_phone = State()
    waiting_for_role_selection = State()

class InspectorStates(StatesGroup):
    waiting_for_proposed_time = State()
    waiting_for_inspection_confirmation = State()

class ChecklistStates(StatesGroup):
    """Состояния для работы с чек-листами"""
    waiting_for_section_selection = State()  # Ожидание выбора раздела
    waiting_for_criterion_response = State()  # Ожидание ответа по критерию
    waiting_for_comment = State()  # Ожидание комментария
    filling_section = State()  # В процессе заполнения раздела

    waiting_for_photo = State()

class SupervisorStates(StatesGroup):
    waiting_for_rejection_reason = State()