from aiogram.fsm.state import State, StatesGroup

class RegistrationStates(StatesGroup):
    waiting_for_phone = State()
    waiting_for_role = State()

class AdminStates(StatesGroup):
    waiting_for_user_data = State()
    waiting_for_role_change = State()
    waiting_for_full_name = State()
    waiting_for_phone = State()
    waiting_for_role_selection = State()

class InspectorStates(StatesGroup):
    waiting_for_proposed_time = State()

class SupervisorStates(StatesGroup):
    waiting_for_rejection_reason = State()