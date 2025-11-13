from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, StateFilter

from database.simple_db import db, UserRole
from database.places_db import places_db
from utils.states import InspectorStates
from utils.inspection_service import inspection_service
from keyboards.inspector_keyboards import (
    get_inspector_main_keyboard,
    get_inspections_keyboard,
    get_back_to_inspections_keyboard,
    get_available_inspections_keyboard, get_help_keyboard
)

router = Router()


# Проверка прав проверяющего
async def check_inspector(user_id: int) -> bool:
    user = db.get_user(user_id)
    if not user:
        return False
    return user['role'] == UserRole.INSPECTOR.value


@router.message(F.text == "📋 Мои проверки")
async def my_inspections(message: Message):
    if not await check_inspector(message.from_user.id):
        await message.answer("❌ У вас нет прав доступа к этой функции.")
        return

    inspections = places_db.get_inspections_by_inspector(message.from_user.id)

    if not inspections:
        await message.answer(
            "📭 У вас нет назначенных проверок.",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text="🔙 Назад")]],
                resize_keyboard=True
            )
        )
        return

    inspections_list = "📋 Ваши проверки:\n\n"

    for place_id, inspection_data in inspections.items():
        info = inspection_service.get_inspection_info(place_id)

        inspections_list += (
            f"🔹 Место: {place_id}\n"
            f"📍 Адрес: {info['address']}\n"
            f"👷 Бригадир: {info['supervisor_name']}\n"
            f"📞 Телефон: {info['supervisor_phone']}\n"
            f"🆔 ID бригадира: {info['supervisor_id']}\n"
            f"📅 Дата проверки: {info['date']}\n"
        )

        if info['date'] == "Не назначена":
            inspections_list += "⚠️ Дата не назначена - свяжитесь с бригадиром\n"

        inspections_list += f"────────────────────\n"

    # Отправляем список и клавиатуру с кнопками для каждой проверки
    if len(inspections_list) > 4000:
        parts = [inspections_list[i:i + 4000] for i in range(0, len(inspections_list), 4000)]
        for part in parts:
            await message.answer(part)
        await message.answer("Выберите проверку для связи с бригадиром:",
                             reply_markup=get_inspections_keyboard(inspections))
    else:
        await message.answer(
            inspections_list + "\nВыберите проверку для связи с бригадиром:",
            reply_markup=get_inspections_keyboard(inspections)
        )


@router.message(F.text.startswith("📞 Связаться #"))
async def contact_manager_from_list(message: Message, state: FSMContext):
    """Обработчик кнопки связи с бригадиром из списка"""
    if not await check_inspector(message.from_user.id):
        return

    try:
        # Извлекаем ID места из текста кнопки
        place_id = message.text.split('#')[1].split(' -')[0]

        inspection_data = places_db.search.get(place_id)
        if not inspection_data or inspection_data.get('inspector') != str(message.from_user.id):
            await message.answer("❌ Проверка не найдена или не принадлежит вам.")
            return

        info = inspection_service.get_inspection_info(place_id)

        await message.answer(
            f"📞 Связь с бригадиром\n\n"
            f"🏢 Место: {place_id}\n"
            f"📍 Адрес: {info['address']}\n"
            f"👷 Бригадир: {info['supervisor_name']}\n"
            f"📞 Телефон: {info['supervisor_phone']}\n"
            f"🆔 ID бригадира: {info['supervisor_id']}\n"
            f"📅 Текущая дата: {info['date']}\n\n"
            f"Введите предложенное время для проверки:\n"
            f"<i>Пример: 25.12.2023 14:30</i>",
            parse_mode="HTML",
            reply_markup=get_back_to_inspections_keyboard()
        )

        await state.update_data(place_id=place_id, supervisor_id=info['supervisor_id'])
        await state.set_state(InspectorStates.waiting_for_proposed_time)

    except (ValueError, IndexError):
        await message.answer("❌ Ошибка при обработке запроса.")


@router.message(F.text == "📍 Доступные проверки")
async def available_inspections(message: Message):
    if not await check_inspector(message.from_user.id):
        await message.answer("❌ У вас нет прав доступа к этой функции.")
        return

    inspections = places_db.get_available_inspections()

    if not inspections:
        await message.answer(
            "📭 Нет доступных проверок.",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text="🔙 Назад")]],
                resize_keyboard=True
            )
        )
        return

    inspections_list = "📍 Доступные проверки:\n\n"

    for place_id, inspection_data in inspections.items():
        info = inspection_service.get_inspection_info(place_id)

        inspections_list += (
            f"🔹 Место: {place_id}\n"
            f"📍 Адрес: {info['address']}\n"
            f"👷 Бригадир: {info['supervisor_name']}\n"
            f"📞 Телефон: {info['supervisor_phone']}\n"
            f"🆔 ID бригадира: {info['supervisor_id']}\n"
            f"────────────────────\n"
        )

    # Отправляем список с кнопками для взятия проверок
    if len(inspections_list) > 4000:
        parts = [inspections_list[i:i + 4000] for i in range(0, len(inspections_list), 4000)]
        for part in parts:
            await message.answer(part)
        await message.answer("Выберите проверку для взятия:",
                             reply_markup=get_available_inspections_keyboard(inspections))
    else:
        await message.answer(
            inspections_list + "\nВыберите проверку для взятия:",
            reply_markup=get_available_inspections_keyboard(inspections)
        )


@router.message(F.text.startswith("✅ Взять проверку #"))
async def take_inspection_from_list(message: Message):
    """Обработчик кнопки взятия проверки из списка"""
    if not await check_inspector(message.from_user.id):
        return

    try:
        # Извлекаем ID места из текста кнопки
        place_id = message.text.split('#')[1].split(' -')[0]

        success = places_db.assign_inspector_to_inspection(place_id, str(message.from_user.id))

        if success:
            info = inspection_service.get_inspection_info(place_id)

            await message.answer(
                f"✅ Вы взяли проверку!\n\n"
                f"🏢 Место: {place_id}\n"
                f"📍 Адрес: {info['address']}\n"
                f"👷 Бригадир: {info['supervisor_name']}\n"
                f"📞 Телефон: {info['supervisor_phone']}\n\n"
                f"Теперь она появится в вашем списке проверок!",
                reply_markup=get_inspector_main_keyboard()
            )
        else:
            await message.answer("❌ Ошибка: проверка не найдена или уже назначена")

    except (ValueError, IndexError):
        await message.answer("❌ Ошибка при обработке запроса.")


@router.message(InspectorStates.waiting_for_proposed_time, F.text)
async def process_proposed_time(message: Message, state: FSMContext, bot: Bot):
    """Обработчик ввода предложенного времени"""
    if message.text == "🔙 К списку проверок":
        await message.answer("Возвращаемся к списку проверок...")
        await state.clear()
        return

    proposed_time = message.text.strip()
    user_data = await state.get_data()
    place_id = user_data['place_id']
    supervisor_id = user_data['supervisor_id']

    # Обновляем дату проверки
    success = places_db.update_inspection_date(place_id, proposed_time)

    if success:
        # Отправляем уведомление бригадиру через сервис
        await inspection_service.send_proposal_to_supervisor(
            bot, place_id, supervisor_id, message.from_user.first_name, proposed_time
        )

        await message.answer(
            f"✅ Предложение отправлено бригадиру!\n\n"
            f"⏰ Ваше предложение: {proposed_time}\n"
            f"Ожидайте подтверждения.",
            reply_markup=get_inspector_main_keyboard()
        )
    else:
        await message.answer(
            "❌ Ошибка при отправке предложения.",
            reply_markup=get_inspector_main_keyboard()
        )

    await state.clear()


# Обработчики навигации
@router.message(F.text == "🔙 Назад")
async def back_to_inspector_panel(message: Message):
    if not await check_inspector(message.from_user.id):
        return

    await message.answer(
        "👁️ Панель проверяющего\n\n"
        "Выберите действие:",
        reply_markup=get_inspector_main_keyboard()
    )


@router.message(F.text == "🔙 К списку проверок")
async def back_to_inspections_list(message: Message):
    if not await check_inspector(message.from_user.id):
        return

    await my_inspections(message)


# Отладочные команды
@router.message(Command("debug_places"))
async def debug_places(message: Message):
    """Отладочная информация о местах и проверках"""
    if not await check_inspector(message.from_user.id):
        return

    all_places = places_db.get_all_places()
    all_inspections = places_db.get_all_inspections()

    debug_info = "🧪 ДЕБАГ ИНФОРМАЦИЯ:\n\n"
    debug_info += f"📍 Всего мест: {len(all_places)}\n"
    debug_info += f"📋 Всего проверок: {len(all_inspections)}\n\n"

    for place_id, supervisor_id in all_places.items():
        inspection = all_inspections.get(place_id, {})
        debug_info += (
            f"🏢 {place_id}\n"
            f"👷 Бригадир: {supervisor_id}\n"
            f"👁️ Проверяющий: {inspection.get('inspector', 'Нет')}\n"
            f"📅 Дата: {inspection.get('date', 'Нет')}\n"
            f"────────────────────\n"
        )
@router.message(F.text == "ℹ️ Помощь")
async def inspector_help(message: Message):
    """Помощь для инспектора"""
    if not await check_inspector(message.from_user.id):
        await message.answer("❌ У вас нет прав доступа к этой функции.")
        return

    help_text = (
        "ℹ️ <b>Помощь по боту для проверяющего</b>\n\n"
        
        "<b>Основные функции:</b>\n"
        "• <b>📋 Мои проверки</b> - просмотр назначенных вам проверок\n"
        "• <b>📍 Доступные проверки</b> - взятие новых проверок из общего списка\n"
        "• <b>👤 Мой профиль</b> - информация о вашем аккаунте\n"
        "• <b>ℹ️ Помощь</b> - эта справка\n\n"
        
        "<b>Как работать с проверками:</b>\n"
        "1. Просмотрите <b>📋 Мои проверки</b> - там ваши текущие задания\n"
        "2. Для каждой проверки можно <b>📞 Связаться</b> с бригадиром\n"
        "3. Предложите удобное время для проведения проверки\n"
        "4. Ожидайте подтверждения от бригадира\n\n"
        
        "<b>Доступные проверки:</b>\n"
        "• В разделе <b>📍 Доступные проверки</b> можно взять новые задания\n"
        "• Нажмите <b>✅ Взять проверку</b> для назначения\n\n"
        
        "<b>Для навигации используйте кнопки меню.</b>"
    )
    
    await message.answer(help_text, reply_markup=get_help_keyboard())
    await message.answer(debug_info)