from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove, FSInputFile, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, StateFilter
import os

from database.simple_db import db, UserRole
from utils.states import AdminStates
from keyboards.admin_keyboards import get_admin_main_keyboard, get_cancel_keyboard, get_back_to_admin_keyboard

# Пробуем импортировать PDF генератор
try:
    from utils.smart_pdf_generator import generate_users_pdf
    PDF_AVAILABLE = True
except ImportError:
    try:
        from utils.simple_pdf_generator import generate_users_pdf_simple as generate_users_pdf
        PDF_AVAILABLE = True
    except ImportError:
        PDF_AVAILABLE = False

router = Router()


# Проверка прав администратора
async def check_admin(user_id: int) -> bool:
    user = db.get_user(user_id)
    return user and user['role'] == UserRole.ADMIN.value


@router.message(Command("admin"))
@router.message(F.text == "👨‍💼 Админ панель")
@router.message(F.text == "🔙 В админ панель")
async def cmd_admin(message: Message):
    if not await check_admin(message.from_user.id):
        await message.answer("❌ У вас нет прав доступа к админ панели.")
        return

    await message.answer(
        "👨‍💼 Админ панель\n\n"
        "Выберите действие:",
        reply_markup=get_admin_main_keyboard()
    )

@router.message(F.text == "📋 Список пользователей")
async def list_users(message: Message):
    if not await check_admin(message.from_user.id):
        return

    users = db.get_all_users()
    if not users:
        await message.answer("📭 В базе нет пользователей.", reply_markup=get_admin_main_keyboard())
        return

    # Предлагаем выбор формата
    await message.answer(
        "📋 Выберите формат списка пользователей:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="📄 Показать в чате"), KeyboardButton(text="📊 Скачать PDF")],
                [KeyboardButton(text="❌ Отмена")]
            ],
            resize_keyboard=True
        )
    )


@router.message(F.text == "📄 Показать в чате")
async def show_users_in_chat(message: Message):
    if not await check_admin(message.from_user.id):
        return

    users = db.get_all_users()

    role_names = {
        UserRole.WORKER.value: "👷 Рабочий",
        UserRole.MANAGER.value: "👨‍💼 Руководитель",
        UserRole.INSPECTOR.value: "👁️ Проверяющий",
        UserRole.ADMIN.value: "👨‍💼 Администратор"
    }

    users_list = "📋 Список пользователей:\n\n"
    for user_id, user_data in users.items():
        status = "✅ Активен" if user_data.get('is_active', True) else "❌ Неактивен"
        users_list += (
            f"👤 {user_data['first_name']} {user_data.get('last_name', '')}\n"
            f"ID: {user_data['telegram_id']}\n"
            f"Роль: {role_names[user_data['role']]}\n"
            f"Телефон: {user_data.get('phone', 'Не указан')}\n"
            f"Статус: {status}\n"
            f"---\n"
        )

    # Разбиваем сообщение если слишком длинное
    if len(users_list) > 4000:
        parts = [users_list[i:i + 4000] for i in range(0, len(users_list), 4000)]
        for part in parts:
            await message.answer(part)
    else:
        await message.answer(users_list, reply_markup=get_back_to_admin_keyboard())


@router.message(F.text == "📊 Скачать PDF")
async def generate_users_pdf_handler(message: Message):
    if not await check_admin(message.from_user.id):
        return

    if not PDF_AVAILABLE:
        await message.answer(
            "❌ Генерация PDF недоступна. Установите библиотеки:\n"
            "pip install fpdf\n\n"
            "Показать список в чате?",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="📄 Показать в чате")],
                    [KeyboardButton(text="🔙 В админ панель")]
                ],
                resize_keyboard=True
            )
        )
        return

    users = db.get_all_users()
    if not users:
        await message.answer("📭 В базе нет пользователей.", reply_markup=get_admin_main_keyboard())
        return

    try:
        # Показываем сообщение о генерации
        await message.answer("📊 Генерирую PDF файл...")

        # Генерируем PDF
        filename = "users_list.pdf"
        pdf_path = generate_users_pdf(users, filename)

        # Отправляем файл
        document = FSInputFile(pdf_path, filename="Список_пользователей.pdf")
        await message.answer_document(
            document,
            caption="📊 Список пользователей"
        )

        # Удаляем временный файл
        try:
            os.remove(pdf_path)
        except:
            pass

        await message.answer("✅ PDF файл успешно сгенерирован!", reply_markup=get_back_to_admin_keyboard())

    except Exception as e:
        await message.answer(
            f"❌ Ошибка при генерации PDF: {str(e)}\n\n"
            f"Показать список в чате?",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="📄 Показать в чате")],
                    [KeyboardButton(text="🔙 В админ панель")]
                ],
                resize_keyboard=True
            )
        )

@router.message(F.text == "👤 Добавить пользователя")
async def add_user_start(message: Message, state: FSMContext):
    if not await check_admin(message.from_user.id):
        return

    await message.answer(
        "👤 Добавление нового пользователя\n\n"
        "Введите данные в формате:\n"
        "<b>ID Телеграм, Имя, Фамилия, Роль</b>\n\n"
        "Пример:\n"
        "<code>123456789, Иван, Петров, worker</code>\n\n"
        "Доступные роли:\n"
        "• <code>worker</code> - 👷 Рабочий\n"
        "• <code>manager</code> - 👨‍💼 Руководитель\n"
        "• <code>inspector</code> - 👁️ Проверяющий\n"
        "• <code>admin</code> - 👨‍💼 Администратор",
        parse_mode="HTML",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(AdminStates.waiting_for_user_data)


@router.message(F.text == "⚙️ Изменить роль")
async def change_role_start(message: Message, state: FSMContext):
    if not await check_admin(message.from_user.id):
        return

    await message.answer(
        "⚙️ Изменение роли пользователя\n\n"
        "Введите данные в формате:\n"
        "<b>ID пользователя, Новая роль</b>\n\n"
        "Пример:\n"
        "<code>123456789, manager</code>\n\n"
        "Доступные роли:\n"
        "• <code>worker</code> - 👷 Рабочий\n"
        "• <code>manager</code> - 👨‍💼 Руководитель\n"
        "• <code>inspector</code> - 👁️ Проверяющий\n"
        "• <code>admin</code> - 👨‍💼 Администратор",
        parse_mode="HTML",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(AdminStates.waiting_for_role_change)


@router.message(F.text == "📊 Статистика")
async def show_stats(message: Message):
    if not await check_admin(message.from_user.id):
        return

    users = db.get_all_users()

    stats = {
        UserRole.ADMIN.value: 0,
        UserRole.MANAGER.value: 0,
        UserRole.INSPECTOR.value: 0,
        UserRole.WORKER.value: 0
    }

    active_users = 0
    for user_data in users.values():
        stats[user_data['role']] += 1
        if user_data.get('is_active', True):
            active_users += 1

    role_names = {
        UserRole.WORKER.value: "👷 Рабочие",
        UserRole.MANAGER.value: "👨‍💼 Руководители",
        UserRole.INSPECTOR.value: "👁️ Проверяющие",
        UserRole.ADMIN.value: "👨‍💼 Администраторы"
    }

    stats_text = "📊 Статистика пользователей:\n\n"
    for role, count in stats.items():
        stats_text += f"{role_names[role]}: {count}\n"

    stats_text += f"\n✅ Активных: {active_users}\n"
    stats_text += f"📊 Всего пользователей: {len(users)}"

    await message.answer(stats_text, reply_markup=get_back_to_admin_keyboard())


# Обработчики для состояний FSM
@router.message(AdminStates.waiting_for_user_data, F.text)
async def add_user_process(message: Message, state: FSMContext):
    if message.text == "❌ Отмена":
        await message.answer("❌ Добавление пользователя отменено.", reply_markup=get_admin_main_keyboard())
        await state.clear()
        return

    try:
        parts = [part.strip() for part in message.text.split(',')]
        if len(parts) != 4:
            await message.answer("❌ Неверный формат. Нужно: ID, Имя, Фамилия, Роль\n\nПопробуйте еще раз:",
                                 reply_markup=get_cancel_keyboard())
            return

        telegram_id = int(parts[0])
        first_name = parts[1]
        last_name = parts[2]
        role_str = parts[3].lower()

        # Проверяем корректность роли
        role_mapping = {
            'worker': UserRole.WORKER,
            'manager': UserRole.MANAGER,
            'inspector': UserRole.INSPECTOR,
            'admin': UserRole.ADMIN
        }

        if role_str not in role_mapping:
            await message.answer(
                "❌ Неверная роль. Доступные роли: worker, manager, inspector, admin\n\nПопробуйте еще раз:",
                reply_markup=get_cancel_keyboard()
            )
            return

        role = role_mapping[role_str]

        # Проверяем, существует ли пользователь
        existing_user = db.get_user(telegram_id)
        if existing_user:
            await message.answer(
                f"❌ Пользователь с ID {telegram_id} уже существует!",
                reply_markup=get_admin_main_keyboard()
            )
            await state.clear()
            return

        # Создаем пользователя
        user = db.create_user(
            telegram_id=telegram_id,
            username="",  # Будет заполнено при первом входе
            first_name=first_name,
            last_name=last_name,
            role=role,
            phone="Не указан"
        )

        role_names = {
            UserRole.WORKER: "👷 Рабочий",
            UserRole.MANAGER: "👨‍💼 Руководитель",
            UserRole.INSPECTOR: "👁️ Проверяющий",
            UserRole.ADMIN: "👨‍💼 Администратор"
        }

        await message.answer(
            f"✅ Пользователь успешно добавлен!\n\n"
            f"👤 {user['first_name']} {user['last_name']}\n"
            f"ID: {user['telegram_id']}\n"
            f"Роль: {role_names[role]}\n"
            f"Статус: ✅ Активен",
            reply_markup=get_admin_main_keyboard()
        )
        await state.clear()

    except ValueError:
        await message.answer("❌ Ошибка: ID должен быть числом\n\nПопробуйте еще раз:",
                             reply_markup=get_cancel_keyboard())
    except Exception as e:
        await message.answer(f"❌ Ошибка при добавлении пользователя: {str(e)}\n\nПопробуйте еще раз:",
                             reply_markup=get_cancel_keyboard())


@router.message(AdminStates.waiting_for_role_change, F.text)
async def change_role_process(message: Message, state: FSMContext):
    if message.text == "❌ Отмена":
        await message.answer("❌ Изменение роли отменено.", reply_markup=get_admin_main_keyboard())
        await state.clear()
        return

    try:
        parts = [part.strip() for part in message.text.split(',')]
        if len(parts) != 2:
            await message.answer("❌ Неверный формат. Нужно: ID, НоваяРоль\n\nПопробуйте еще раз:",
                                 reply_markup=get_cancel_keyboard())
            return

        telegram_id = int(parts[0])
        new_role_str = parts[1].lower()

        # Проверяем корректность роли
        role_mapping = {
            'worker': UserRole.WORKER,
            'manager': UserRole.MANAGER,
            'inspector': UserRole.INSPECTOR,
            'admin': UserRole.ADMIN
        }

        if new_role_str not in role_mapping:
            await message.answer(
                "❌ Неверная роль. Доступные роли: worker, manager, inspector, admin\n\nПопробуйте еще раз:",
                reply_markup=get_cancel_keyboard()
            )
            return

        new_role = role_mapping[new_role_str]

        # Проверяем, существует ли пользователь
        existing_user = db.get_user(telegram_id)
        if not existing_user:
            await message.answer(
                f"❌ Пользователь с ID {telegram_id} не найден!",
                reply_markup=get_admin_main_keyboard()
            )
            await state.clear()
            return

        # Меняем роль
        success = db.update_user_role(telegram_id, new_role)

        if success:
            role_names = {
                UserRole.WORKER: "👷 Рабочий",
                UserRole.MANAGER: "👨‍💼 Руководитель",
                UserRole.INSPECTOR: "👁️ Проверяющий",
                UserRole.ADMIN: "👨‍💼 Администратор"
            }

            await message.answer(
                f"✅ Роль пользователя успешно изменена!\n\n"
                f"👤 {existing_user['first_name']} {existing_user.get('last_name', '')}\n"
                f"ID: {existing_user['telegram_id']}\n"
                f"Новая роль: {role_names[new_role]}",
                reply_markup=get_admin_main_keyboard()
            )
        else:
            await message.answer("❌ Ошибка при изменении роли", reply_markup=get_admin_main_keyboard())

        await state.clear()

    except ValueError:
        await message.answer("❌ Ошибка: ID должен быть числом\n\nПопробуйте еще раз:",
                             reply_markup=get_cancel_keyboard())
    except Exception as e:
        await message.answer(f"❌ Ошибка при изменении роли: {str(e)}\n\nПопробуйте еще раз:",
                             reply_markup=get_cancel_keyboard())


# Обработка кнопки "В главное меню"
@router.message(F.text == "🔙 В главное меню")
async def back_to_main_menu(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("🔙 Возврат в главное меню", reply_markup=ReplyKeyboardRemove())
    # Здесь можно добавить вызов команды start или другого обработчика главного меню


# Обработка отмены для всех состояний
@router.message(StateFilter(AdminStates), F.text == "❌ Отмена")
async def cancel_handler(message: Message, state: FSMContext):
    await message.answer("❌ Операция отменена.", reply_markup=get_admin_main_keyboard())
    await state.clear()