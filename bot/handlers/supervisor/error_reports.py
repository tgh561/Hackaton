from aiogram import Router, types
from aiogram.filters import Text
from datetime import datetime

from database import db
from keyboards.supervisor_kb import get_error_reports_keyboard, get_back_keyboard
from keyboards.main_menu import get_main_menu

router = Router()

@router.message(Text("⚠️ Отчеты об ошибках"))
async def error_reports_menu(message: types.Message):
    """Меню просмотра отчетов об ошибках"""
    await message.answer(
        "⚠️ <b>Просмотр отчетов об ошибках</b>\n\n"
        "Выберите действие:",
        reply_markup=get_error_reports_keyboard()
    )

@router.message(Text("📅 Ошибки за сегодня"))
async def show_today_errors(message: types.Message):
    """Показать ошибки за сегодня"""
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Получаем все отчеты за сегодня
    all_reports = db.get_all_error_reports(limit=100)  # Большой лимит чтобы найти сегодняшние
    today_reports = [report for report in all_reports if report['error_date'] == today]
    
    if not today_reports:
        await message.answer(
            f"📅 <b>Ошибки за сегодня ({today})</b>\n\n"
            "Сегодня ошибок не обнаружено ✅",
            reply_markup=get_error_reports_keyboard()
        )
        return
    
    today_text = (
        f"📅 <b>Ошибки за сегодня ({today})</b>\n"
        f"Всего ошибок: {len(today_reports)}\n\n"
    )
    
    for i, report in enumerate(today_reports, 1):
        author_name = f"{report.get('first_name', 'Неизвестно')} {report.get('last_name', '')}".strip()
        if not author_name:
            author_name = "Неизвестный автор"
        
        today_text += (
            f"<b>{i}. {report['criterion']}</b>\n"
            f"   👤 {author_name}\n"
            f"   📝 {report['description'][:50]}...\n"
            f"   ──────────────────\n"
        )
    
    await message.answer(today_text, reply_markup=get_error_reports_keyboard())

@router.message(Text("📋 Последние 10 ошибок"))
async def show_last_10_errors(message: types.Message):
    """Показать последние 10 ошибок"""
    reports = db.get_all_error_reports(limit=10)
    
    if not reports:
        await message.answer(
            "📋 <b>Последние ошибки</b>\n\n"
            "В системе пока нет отчетов об ошибках",
            reply_markup=get_error_reports_keyboard()
        )
        return
    
    last_errors_text = "📋 <b>Последние 10 ошибок</b>\n\n"
    
    for i, report in enumerate(reports, 1):
        author_name = f"{report.get('first_name', 'Неизвестно')} {report.get('last_name', '')}".strip()
        if not author_name:
            author_name = "Неизвестный автор"
        
        # Форматируем дату создания
        created_date = report['created_at'][:10] if report['created_at'] else report['error_date']
        
        last_errors_text += (
            f"<b>{i}. {report['criterion']}</b>\n"
            f"   📅 {report['error_date']} | 👤 {author_name}\n"
            f"   📝 {report['description'][:60]}...\n"
            f"   🆔 ID: {report['id']}\n"
            f"   ──────────────────\n"
        )
    
    await message.answer(last_errors_text, reply_markup=get_error_reports_keyboard())

@router.message(Text("🔙 Назад"))
async def go_back_from_error_reports(message: types.Message):
    """Возврат в главное меню из раздела отчетов об ошибках"""
    user = db.get_user(message.from_user.id)
    role = user['role'] if user else 'user'
    await message.answer("Главное меню:", reply_markup=get_main_menu(role))