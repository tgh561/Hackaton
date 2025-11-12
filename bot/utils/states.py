from aiogram.fsm.state import State, StatesGroup

class RegistrationStates(StatesGroup):
    waiting_for_phone = State()
    waiting_for_role = State()

class AdminStates(StatesGroup):
    waiting_for_user_data = State()
    waiting_for_role_change = State()