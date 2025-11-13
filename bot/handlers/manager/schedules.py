import os
from aiogram import Router, types, F
from aiogram.filters import Text
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import FSInputFile

from database import db
from keyboards.manager_kb import get_schedules_keyboard, get_back_keyboard
from keyboards.main_menu import get_main_menu

router = Router()

class ScheduleStates(StatesGroup):
    waiting_view_date = State()
    waiting_upload_date = State()
    waiting_upload_file = State()

@router.message(Text("📊 Графики"))
async def schedules_menu(message: types.Message):
    """Меню графиков"""
    await message.answer(
        "📊 <b>Управление графиками</b>\n\n"
        "Выберите действие:",
        reply_markup=get_schedules_keyboard()
    )

@router.message(Text("👀 Просмотреть график"))
async def view_schedule_start(message: types.Message, state: FSMContext):
    """Начало просмотра графика"""
    await message.answer(
        "📅 Введите дату графика в формате ГГГГ-ММ-ДД:\n"
        "Например: 2024-01-15",
        reply_markup=get_back_keyboard()
    )
    await state.set_state(ScheduleStates.waiting_view_date)

@router.message(ScheduleStates.waiting_view_date)
async def process_view_date(message: types.Message, state: FSMContext):
    """Обработка даты для просмотра графика"""
    if message.text == "🔙 Назад":
        await state.clear()
        await schedules_menu(message)
        return
    
    date = message.text.strip()
    
    # Простая валидация даты
    if len(date) != 10 or date[4] != '-' or date[7] != '-':
        await message.answer("❌ Неверный формат даты. Используйте ГГГГ-ММ-ДД")
        return
    
    # Поиск графика в базе данных
    schedule = db.get_schedule(message.from_user.id, date)
    
    if not schedule:
        await message.answer(f"❌ График на дату {date} не найден")
        return
    
    try:
        # Отправка файла
        file = FSInputFile(schedule['file_path'])
        await message.answer_document(
            file,
            caption=f"📊 График на {date}"
        )
        await state.clear()
        await message.answer("Выберите действие:", reply_markup=get_schedules_keyboard())
    except Exception as e:
        await message.answer("❌ Ошибка при загрузке файла")
        await state.clear()

@router.message(Text("📤 Загрузить график"))
async def upload_schedule_start(message: types.Message, state: FSMContext):
    """Начало загрузки графика"""
    await message.answer(
        "📅 Введите дату графика в формате ГГГГ-ММ-ДД:\n"
        "Например: 2024-01-15",
        reply_markup=get_back_keyboard()
    )
    await state.set_state(ScheduleStates.waiting_upload_date)

@router.message(ScheduleStates.waiting_upload_date)
async def process_upload_date(message: types.Message, state: FSMContext):
    """Обработка даты для загрузки графика"""
    if message.text == "🔙 Назад":
        await state.clear()
        await schedules_menu(message)
        return
    
    date = message.text.strip()
    
    if len(date) != 10 or date[4] != '-' or date[7] != '-':
        await message.answer("❌ Неверный формат даты. Используйте ГГГГ-ММ-ДД")
        return
    
    await state.update_data(schedule_date=date)
    await message.answer("📎 Теперь отправьте Excel файл с графиком")
    await state.set_state(ScheduleStates.waiting_upload_file)

@router.message(ScheduleStates.waiting_upload_file, F.document)
async def process_upload_file(message: types.Message, state: FSMContext):
    """Обработка загружаемого файла"""
    data = await state.get_data()
    date = data['schedule_date']
    
    # Проверяем, что это Excel файл
    if not message.document.mime_type or 'excel' not in message.document.mime_type and 'sheet' not in message.document.mime_type:
        await message.answer("❌ Пожалуйста, отправьте файл в формате Excel (.xlsx, .xls)")
        return
    
    # Создаем папку для файлов если не существует
    os.makedirs("schedules", exist_ok=True)
    
    file_id = message.document.file_id
    file = await message.bot.get_file(file_id)
    file_path = f"schedules/{message.from_user.id}_{date}.xlsx"
    
    # Скачиваем файл
    await message.bot.download_file(file.file_path, file_path)
    
    # Сохраняем в базу данных
    db.add_schedule(message.from_user.id, date, file_path)
    
    await message.answer("✅ График успешно загружен!")
    await state.clear()
    await schedules_menu(message)

@router.message(ScheduleStates.waiting_upload_file)
async def process_wrong_file_type(message: types.Message):
    """Обработка некорректного типа файла"""
    await message.answer("❌ Пожалуйста, отправьте Excel файл с графиком")

@router.message(Text("🔙 Назад"))
async def go_back_from_schedules(message: types.Message, state: FSMContext):
    """Возврат в главное меню из раздела графиков"""
    await state.clear()
    user = db.get_user(message.from_user.id)
    role = user['role'] if user else 'user'
    await message.answer("Главное меню:", reply_markup=get_main_menu(role))