from aiogram import Router, types, F
from aiogram.filters import Text
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database import db
from keyboards.manager_kb import get_reports_keyboard, get_back_keyboard
from keyboards.main_menu import get_main_menu

router = Router()

class ReportStates(StatesGroup):
    waiting_month = State()
    waiting_daily_date = State()

@router.message(Text("📈 Отчеты"))
async def reports_menu(message: types.Message):
    """Меню отчетов"""
    await message.answer(
        "📈 <b>Просмотр отчетов</b>\n\n"
        "Выберите тип отчета:",
        reply_markup=get_reports_keyboard()
    )

@router.message(Text("📅 Месячный отчет"))
async def monthly_report_start(message: types.Message, state: FSMContext):
    """Начало просмотра месячного отчета"""
    await message.answer(
        "📅 Введите месяц в формате ГГГГ-ММ:\n"
        "Например: 2024-01",
        reply_markup=get_back_keyboard()
    )
    await state.set_state(ReportStates.waiting_month)

@router.message(ReportStates.waiting_month)
async def process_monthly_report(message: types.Message, state: FSMContext):
    """Обработка месяца для отчета"""
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
    await message.answer(
        "📅 Введите дату в формате ГГГГ-ММ-ДД:\n"
        "Например: 2024-01-15",
        reply_markup=get_back_keyboard()
    )
    await state.set_state(ReportStates.waiting_daily_date)

@router.message(ReportStates.waiting_daily_date)
async def process_daily_report(message: types.Message, state: FSMContext):
    """Обработка даты для ежедневного отчета"""
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

@router.message(Text("🔙 Назад"))
async def go_back_from_reports(message: types.Message, state: FSMContext):
    """Возврат в главное меню из раздела отчетов"""
    await state.clear()
    user = db.get_user(message.from_user.id)
    role = user['role'] if user else 'user'
    await message.answer("Главное меню:", reply_markup=get_main_menu(role))