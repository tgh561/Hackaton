import os
from aiogram import Router, types, F
from aiogram.filters import Text
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import FSInputFile

from database import db
from keyboards.manager_kb import (
    get_schedules_keyboard, 
    get_reports_keyboard, 
    get_back_keyboard,
    get_help_keyboard
)

router = Router()


# Проверка прав менеджера
async def check_manager(user_id: int) -> bool:
    user = db.get_user(user_id)
    if not user:
        return False
    return user['role'] == 'manager'


class ScheduleStates(StatesGroup):
    waiting_view_date = State()
    waiting_upload_date = State()
    waiting_upload_file = State()


class ReportStates(StatesGroup):
    waiting_month = State()
    waiting_daily_date = State()


# ===== ОБРАБОТЧИКИ ГРАФИКОВ =====

@router.message(Text("📊 Графики"))
async def schedules_menu(message: types.Message):
    """Меню графиков"""
    if not await check_manager(message.from_user.id):
        await message.answer("❌ У вас нет прав доступа к этой функции.")
        return

    await message.answer(
        "📊 <b>Управление графиками</b>\n\n"
        "Выберите действие:",
        reply_markup=get_schedules_keyboard()
    )


@router.message(Text("👀 Просмотреть график"))
async def view_schedule_start(message: types.Message, state: FSMContext):
    """Начало просмотра графика"""
    if not await check_manager(message.from_user.id):
        return

    await message.answer(
        "📅 Введите дату графика в формате ГГГГ-ММ-ДД:\n"
        "Например: 2024-01-15",
        reply_markup=get_back_keyboard()
    )
    await state.set_state(ScheduleStates.waiting_view_date)


@router.message(ScheduleStates.waiting_view_date)
async def process_view_date(message: types.Message, state: FSMContext):
    """Обработка даты для просмотра графика"""
    if not await check_manager(message.from_user.id):
        return

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
    if not await check_manager(message.from_user.id):
        return

    await message.answer(
        "📅 Введите дату графика в формате ГГГГ-ММ-ДД:\n"
        "Например: 2024-01-15",
        reply_markup=get_back_keyboard()
    )
    await state.set_state(ScheduleStates.waiting_upload_date)


@router.message(ScheduleStates.waiting_upload_date)
async def process_upload_date(message: types.Message, state: FSMContext):
    """Обработка даты для загрузки графика"""
    if not await check_manager(message.from_user.id):
        return

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
    if not await check_manager(message.from_user.id):
        return

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
    if not await check_manager(message.from_user.id):
        return

    await message.answer("❌ Пожалуйста, отправьте Excel файл с графиком")


# ===== ОБРАБОТЧИКИ ОТЧЕТОВ =====

@router.message(Text("📈 Отчеты"))
async def reports_menu(message: types.Message):
    """Меню отчетов"""
    if not await check_manager(message.from_user.id):
        await message.answer("❌ У вас нет прав доступа к этой функции.")
        return

    await message.answer(
        "📈 <b>Просмотр отчетов</b>\n\n"
        "Выберите тип отчета:",
        reply_markup=get_reports_keyboard()
    )


@router.message(Text("📅 Месячный отчет"))
async def monthly_report_start(message: types.Message, state: FSMContext):
    """Начало просмотра месячного отчета"""
    if not await check_manager(message.from_user.id):
        return

    await message.answer(
        "📅 Введите месяц в формате ГГГГ-ММ:\n"
        "Например: 2024-01",
        reply_markup=get_back_keyboard()
    )
    await state.set_state(ReportStates.waiting_month)


@router.message(ReportStates.waiting_month)
async def process_monthly_report(message: types.Message, state: FSMContext):
    """Обработка месяца для отчета"""
    if not await check_manager(message.from_user.id):
        return

    if message.text == "🔙 Назад":
        await state.clear()
        await reports_menu(message)
        return
    
    month = message.text.strip()
    
    # Валидация формата месяца
    if len(month) != 7 or month[4] != '-':
        await message.answer("❌ Неверный формат месяца. Используйте ГГГГ-ММ")
        return
    
    # Здесь должна быть логика генерации/получения отчета
    # Для примера просто показываем сообщение
    await message.answer(
        f"📊 <b>Месячный отчет за {month}</b>\n\n"
        f"<b>Общая статистика:</b>\n"
        f"• 📈 Продажи: 1,000,000 руб.\n"
        f"• 👥 Клиенты: 150\n"
        f"• 🔄 Конверсия: 25%\n"
        f"• 📦 Заказы: 200\n\n"
        f"<b>Показатели эффективности:</b>\n"
        f"• ✅ Выполнение плана: 95%\n"
        f"• 📞 Обработано заявок: 450\n"
        f"• ⭐ Средняя оценка: 4.7/5\n\n"
        f"<i>Отчет сформирован автоматически</i>"
    )
    await state.clear()
    await reports_menu(message)


@router.message(Text("📊 Ежедневный отчет"))
async def daily_report_start(message: types.Message, state: FSMContext):
    """Начало просмотра ежедневного отчета"""
    if not await check_manager(message.from_user.id):
        return

    await message.answer(
        "📅 Введите дату в формате ГГГГ-ММ-ДД:\n"
        "Например: 2024-01-15",
        reply_markup=get_back_keyboard()
    )
    await state.set_state(ReportStates.waiting_daily_date)


@router.message(ReportStates.waiting_daily_date)
async def process_daily_report(message: types.Message, state: FSMContext):
    """Обработка даты для ежедневного отчета"""
    if not await check_manager(message.from_user.id):
        return

    if message.text == "🔙 Назад":
        await state.clear()
        await reports_menu(message)
        return
    
    date = message.text.strip()
    
    # Валидация формата даты
    if len(date) != 10 or date[4] != '-' or date[7] != '-':
        await message.answer("❌ Неверный формат даты. Используйте ГГГГ-ММ-ДД")
        return
    
    # Здесь должна быть логика генерации/получения отчета
    await message.answer(
        f"📊 <b>Ежедневный отчет за {date}</b>\n\n"
        f"<b>Основные показатели:</b>\n"
        f"• 💰 Продажи: 50,000 руб.\n"
        f"• 🛒 Заказы: 25\n"
        f"• 👥 Новые клиенты: 5\n"
        f"• 📞 Обработано звонков: 30\n\n"
        f"<b>Детализация по времени:</b>\n"
        f"• Утро (9:00-12:00): 12,000 руб.\n"
        f"• День (12:00-18:00): 28,000 руб.\n"
        f"• Вечер (18:00-21:00): 10,000 руб.\n\n"
        f"<b>Эффективность:</b>\n"
        f"• 📈 Конверсия: 22%\n"
        f"• ⭐ Средний чек: 2,000 руб.\n"
        f"• 🕒 Среднее время обработки: 15 мин.\n\n"
        f"<i>Отчет сформирован автоматически</i>"
    )
    await state.clear()
    await reports_menu(message)


# ===== ОБРАБОТЧИК ПОМОЩИ =====

@router.message(Text("ℹ️ Помощь"))
async def manager_help(message: types.Message):
    """Помощь для менеджера"""
    if not await check_manager(message.from_user.id):
        await message.answer("❌ У вас нет прав доступа к этой функции.")
        return

    help_text = (
        "ℹ️ <b>Помощь по боту для менеджера</b>\n\n"
        
        "<b>Основные функции:</b>\n"
        "• <b>📊 Графики</b> - работа с графиками работы\n"
        "• <b>📈 Отчеты</b> - просмотр различных отчетов\n"
        "• <b>👤 Мой профиль</b> - информация о вашем аккаунте\n"
        "• <b>ℹ️ Помощь</b> - эта справка\n\n"
        
        "<b>Работа с графиками:</b>\n"
        "• <b>👀 Просмотреть график</b> - поиск и просмотр существующих графиков\n"
        "• <b>📤 Загрузить график</b> - загрузка новых графиков в формате Excel\n"
        "• Формат даты для поиска: ГГГГ-ММ-ДД (например: 2024-01-15)\n\n"
        
        "<b>Просмотр отчетов:</b>\n"
        "• <b>📅 Месячный отчет</b> - общая статистика за месяц\n"
        "• <b>📊 Ежедневный отчет</b> - детальная информация за день\n"
        "• Формат месяца: ГГГГ-ММ (например: 2024-01)\n"
        "• Формат даты: ГГГГ-ММ-ДД (например: 2024-01-15)\n\n"
        
        "<b>Для навигации используйте кнопки меню.</b>"
    )
    
    await message.answer(help_text, reply_markup=get_help_keyboard())


# ===== ОБРАБОТЧИКИ НАВИГАЦИИ =====

@router.message(Text("🔙 Назад"))
async def go_back_from_schedules(message: types.Message, state: FSMContext):
    """Возврат в главное меню из разделов"""
    if not await check_manager(message.from_user.id):
        return

    await state.clear()
    await message.answer(
        "👨‍💼 Панель менеджера\n\n"
        "Выберите раздел:",
        reply_markup=types.ReplyKeyboardMarkup(
            keyboard=[
                [types.KeyboardButton(text="📊 Графики"), types.KeyboardButton(text="📈 Отчеты")],
                [types.KeyboardButton(text="👤 Мой профиль"), types.KeyboardButton(text="ℹ️ Помощь")]
            ],
            resize_keyboard=True
        )
    )


# ===== ОТЛАДОЧНЫЕ КОМАНДЫ =====

@router.message(F.text == "/debug_manager")
async def debug_manager(message: types.Message):
    """Отладочная информация для менеджера"""
    if not await check_manager(message.from_user.id):
        return

    user = db.get_user(message.from_user.id)
    
    debug_info = (
        "🧪 <b>ДЕБАГ ИНФОРМАЦИЯ МЕНЕДЖЕРА</b>\n\n"
        f"🆔 Ваш ID: {user['telegram_id']}\n"
        f"👤 Ваше имя: {user['first_name']} {user['last_name'] or ''}\n"
        f"🎯 Ваша роль: {user['role']}\n"
        f"📅 Регистрация: {user['created_at']}\n"
        f"📞 Телефон: {user['phone'] or 'Не указан'}\n\n"
        f"<b>Доступные функции:</b>\n"
        f"• Управление графиками\n"
        f"• Просмотр отчетов\n"
        f"• Профиль и настройки"
    )
    
    await message.answer(debug_info)