from aiogram import Router, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from utils.states import RegistrationStates
from keyboards.auth_keyboards import get_phone_keyboard, get_role_keyboard
from keyboards.inspector_keyboards import get_inspector_main_keyboard
from database.simple_db import db, UserRole

# Добавляем импорт для бригадира
try:
    from keyboards.supervisor_keyboards import get_supervisor_main_keyboard
except ImportError:
    # Если файла нет, создаем функцию здесь
    def get_supervisor_main_keyboard():
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="📋 Мои объекты"), KeyboardButton(text="👁️ Просмотр чек-листов")],
                [KeyboardButton(text="📊 Статистика"), KeyboardButton(text="ℹ️ Помощь")],
                [KeyboardButton(text="🔙 В главное меню")]
            ],
            resize_keyboard=True
        )

router = Router()


def get_main_keyboard(user_role: UserRole):
    keyboard = []

    if user_role == UserRole.ADMIN:
        keyboard.append([KeyboardButton(text="👨‍💼 Админ панель")])
    elif user_role == UserRole.INSPECTOR:
        keyboard.append([KeyboardButton(text="👁️ Панель проверяющего")])
    elif user_role == UserRole.MANAGER:
        keyboard.append([KeyboardButton(text="👷 Панель бригадира")])  # ← ДОБАВЬТЕ ЭТУ СТРОКУ!

    # Общие кнопки для всех ролей
    keyboard.extend([
        [KeyboardButton(text="👤 Мой профиль")],
        [KeyboardButton(text="🔄 Сменить роль")],
        [KeyboardButton(text="ℹ️ Помощь")]
    ])

    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

@router.message(F.text == "🔄 Сменить роль")
async def cmd_change_role(message: Message, state: FSMContext):
    user = db.get_user(message.from_user.id)

    if not user:
        await message.answer("❌ Вы не зарегистрированы в системе.")
        return

    await message.answer(
        "Выберите новую роль:",
        reply_markup=get_role_keyboard()
    )
    await state.set_state(RegistrationStates.waiting_for_role_change)


@router.message(RegistrationStates.waiting_for_role_change,
                F.text.in_(["👷 Рабочий", "👨‍💼 Руководитель", "👁️ Проверяющий"]))
async def process_role_change(message: Message, state: FSMContext):
    role_mapping = {
        "👷 Рабочий": UserRole.WORKER,
        "👨‍💼 Руководитель": UserRole.MANAGER,
        "👁️ Проверяющий": UserRole.INSPECTOR
    }

    new_role = role_mapping[message.text]
    user = db.get_user(message.from_user.id)

    if not user:
        await message.answer("❌ Пользователь не найден.")
        await state.clear()
        return

    # Сохраняем старую роль для сообщения
    old_role_name = {
        UserRole.WORKER: "👷 Рабочий",
        UserRole.MANAGER: "👨‍💼 Руководитель",
        UserRole.INSPECTOR: "👁️ Проверяющий",
        UserRole.ADMIN: "👨‍💼 Администратор"
    }[UserRole(user['role'])]

    # Обновляем роль пользователя
    success = db.update_user_role(message.from_user.id, new_role)

    if success:
        new_user_data = db.get_user(message.from_user.id)
        user_role = UserRole(new_user_data['role'])

        await message.answer(
            f"✅ Роль успешно изменена!\n"
            f"Старая роль: {old_role_name}\n"
            f"Новая роль: {message.text}",
            reply_markup=get_main_keyboard(user_role)
        )
    else:
        await message.answer(
            "❌ Не удалось изменить роль. Попробуйте позже.",
            reply_markup=get_main_keyboard(UserRole(user['role']))
        )

    await state.clear()


@router.message(RegistrationStates.waiting_for_role_change, F.text == "❌ Отмена")
async def cancel_role_change(message: Message, state: FSMContext):
    user = db.get_user(message.from_user.id)
    if user:
        user_role = UserRole(user['role'])
        await message.answer(
            "Смена роли отменена.",
            reply_markup=get_main_keyboard(user_role)
        )
    else:
        await message.answer("Смена роли отменена.", reply_markup=ReplyKeyboardRemove())
    await state.clear()

@router.message(Command("start"))
@router.message(F.text == "🔙 В главное меню")
async def cmd_start(message: Message):
    user = db.get_user(message.from_user.id)

    if not user:
        keyboard = []

        keyboard.extend([[
            KeyboardButton(text="Пройти регистрацию")
        ]])

        await message.answer(
            "👋 Добро пожаловать!\n\n"
            "❌ Вы не зарегистрированы в системе.\n",
            reply_markup=ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
        )
        return

    user_role = UserRole(user['role'])

    greeting = f"👋 Добро пожаловать, {message.from_user.first_name}!"

    if user_role == UserRole.ADMIN:
        greeting += "\n\nВы вошли как 👨‍💼 Администратор"
    elif user_role == UserRole.MANAGER:
        greeting += "\n\nВы вошли как 👨‍💼 Руководитель"
    elif user_role == UserRole.INSPECTOR:
        greeting += "\n\nВы вошли как 👁️ Проверяющий"
    else:
        greeting += "\n\nВы вошли как 👷 Рабочий"

    await message.answer(
        greeting,
        reply_markup=get_main_keyboard(user_role)
    )



@router.message(F.text == "Пройти регистрацию")
async def cmd_register(message: Message, state: FSMContext):
    print(message.from_user.id)
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
        f"Телефон: {user_data.get('phone')}\n"
        f"Для запуска меню пропишите команду /start",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.clear()


@router.message(RegistrationStates.waiting_for_role, F.text == "❌ Отмена")
async def cancel_registration(message: Message, state: FSMContext):
    await message.answer("Регистрация отменена.", reply_markup=ReplyKeyboardRemove())
    await state.clear()

@router.message(F.text == "👤 Мой профиль")
async def cmd_profile(message: Message):
    user = db.get_user(message.from_user.id)

    if not user:
        await message.answer("❌ Вы не зарегистрированы в системе.")
        return

    role_names = {
        UserRole.WORKER: "👷 Рабочий",
        UserRole.MANAGER: "👨‍💼 Руководитель",
        UserRole.INSPECTOR: "👁️ Проверяющий",
        UserRole.ADMIN: "👨‍💼 Администратор"
    }

    status = "✅ Активен" if user.get('is_active', True) else "❌ Неактивен"

    await message.answer(
        f"👤 Ваш профиль:\n"
        f"ID: {user['telegram_id']}\n"
        f"Имя: {user['first_name']} {user.get('last_name', '')}\n"
        f"Роль: {role_names[UserRole(user['role'])]}\n"
        f"Телефон: {user.get('phone', 'Не указан')}\n"
        f"Статус: {status}\n"
    )


@router.message(F.text == "ℹ️ Помощь")
async def cmd_help(message: Message):
    user = db.get_user(message.from_user.id)

    if not user:
        await message.answer("❌ Вы не зарегистрированы в системе.")
        return

    help_text = "ℹ️ Помощь по боту:\n\n"

    user_role = UserRole(user['role'])

    if user_role == UserRole.ADMIN:
        help_text += (
            "👨‍💼 Администратор имеет доступ к:\n"
            "• 📋 Просмотр списка пользователей\n"
            "• 👤 Добавление новых пользователей\n"
            "• ⚙️ Изменение ролей пользователей\n"
            "• 📊 Просмотр статистики\n\n"
        )

    help_text += (
        "Общие функции:\n"
        "• 👤 Просмотр своего профиля\n"
        "• ℹ️ Просмотр справки\n\n"
        "Для навигации используйте кнопки меню."
    )

    await message.answer(help_text)

@router.message(F.text == "👷 Панель бригадира")
async def supervisor_panel(message: Message):
    user = db.get_user(message.from_user.id)

    if not user or UserRole(user['role']) != UserRole.MANAGER:
        await message.answer("❌ У вас нет прав доступа к панели бригадира.")
        return

    await message.answer(
        "👷 Панель бригадира\n\n"
        "Выберите действие:",
        reply_markup=get_supervisor_main_keyboard()
    )

@router.message(F.text == "👁️ Панель проверяющего")
async def inspector_panel(message: Message):
    user = db.get_user(message.from_user.id)

    if not user or UserRole(user['role']) != UserRole.INSPECTOR:
        await message.answer("❌ У вас нет прав доступа к панели проверяющего.")
        return

    await message.answer(
        "👁️ Панель проверяющего\n\n"
        "Выберите действие:",
        reply_markup=get_inspector_main_keyboard()
    )