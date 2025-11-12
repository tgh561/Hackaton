from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command

from database.simple_db import db, UserRole

router = Router()


def get_main_keyboard(user_role: UserRole):
    keyboard = []

    if user_role == UserRole.ADMIN:
        keyboard.append([KeyboardButton(text="👨‍💼 Админ панель")])

    # Общие кнопки для всех ролей
    keyboard.extend([
        [KeyboardButton(text="👤 Мой профиль")],
        [KeyboardButton(text="ℹ️ Помощь")]
    ])

    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


@router.message(Command("start"))
@router.message(F.text == "🔙 В главное меню")
async def cmd_start(message: Message):
    user = db.get_user(message.from_user.id)

    if not user:
        await message.answer(
            "👋 Добро пожаловать!\n\n"
            "❌ Вы не зарегистрированы в системе.\n"
            "Обратитесь к администратору для получения доступа."
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
        f"Регистрация: {user['registered_at'][:16].replace('T', ' ')}"
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