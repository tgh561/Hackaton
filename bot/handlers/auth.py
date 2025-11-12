from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

from database.simple_db import db, UserRole
from utils.states import RegistrationStates
from keyboards.auth_keyboards import get_phone_keyboard, get_role_keyboard

router = Router()


@router.message(Command("register"))
async def cmd_register(message: Message, state: FSMContext):
    user = db.get_user(message.from_user.id)
    if user:
        await message.answer("Вы уже зарегистрированы!")
        return

    await message.answer(
        "Для регистрации нам нужен ваш номер телефона.\n"
        "Нажмите кнопку ниже, чтобы поделиться им:",
        reply_markup=get_phone_keyboard()
    )
    await state.set_state(RegistrationStates.waiting_for_phone)


@router.message(RegistrationStates.waiting_for_phone, F.contact)
async def process_phone(message: Message, state: FSMContext):
    contact = message.contact
    if contact.user_id != message.from_user.id:
        await message.answer("Пожалуйста, поделитесь своим номером телефона.")
        return

    await state.update_data(phone=contact.phone_number)
    await message.answer(
        "Отлично! Теперь выберите вашу роль:",
        reply_markup=get_role_keyboard()
    )
    await state.set_state(RegistrationStates.waiting_for_role)


@router.message(RegistrationStates.waiting_for_role, F.text.in_(["👷 Рабочий", "👨‍💼 Руководитель", "👁️ Проверяющий"]))
async def process_role(message: Message, state: FSMContext):
    role_mapping = {
        "👷 Рабочий": UserRole.WORKER,
        "👨‍💼 Руководитель": UserRole.MANAGER,
        "👁️ Проверяющий": UserRole.INSPECTOR
    }

    role = role_mapping[message.text]
    user_data = await state.get_data()

    user = db.create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
        phone=user_data.get('phone'),
        role=role
    )

    await message.answer(
        f"✅ Регистрация завершена!\n"
        f"Роль: {message.text}\n"
        f"Телефон: {user_data.get('phone')}",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.clear()


@router.message(RegistrationStates.waiting_for_role, F.text == "❌ Отмена")
async def cancel_registration(message: Message, state: FSMContext):
    await message.answer("Регистрация отменена.", reply_markup=ReplyKeyboardRemove())
    await state.clear()