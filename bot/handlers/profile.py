from aiogram import Router, types
from aiogram.filters import Text

from database import db
from keyboards.main_menu import get_main_menu

router = Router()

@router.message(Text("👤 Мой профиль"))
async def show_profile(message: types.Message):
    """Показать профиль пользователя"""
    user = db.get_user(message.from_user.id)
    
    if not user:
        await message.answer("❌ Профиль не найден")
        return
    
    # Определяем описание роли
    role_descriptions = {
        'manager': '👨‍💼 Менеджер',
        'supervisor': '👨‍🏫 Супервайзер',
        'user': '👤 Пользователь'
    }
    
    role_description = role_descriptions.get(user['role'], user['role'])
    
    # Формируем текст профиля в зависимости от роли
    if user['role'] == 'manager':
        profile_text = (
            f"👤 <b>Профиль менеджера</b>\n\n"
            f"🆔 ID: {user['telegram_id']}\n"
            f"👨‍💼 Имя: {user['first_name']}\n"
            f"👨‍💼 Фамилия: {user['last_name'] or 'Не указана'}\n"
            f"📞 Телефон: {user['phone'] or 'Не указан'}\n"
            f"🎯 Роль: {role_description}\n"
            f"📅 Регистрация: {user['created_at'][:10] if user['created_at'] else 'Не указана'}\n\n"
            f"<b>Доступные функции:</b>\n"
            f"• 📊 Управление графиками\n"
            f"• 📈 Просмотр отчетов\n"
            f"• 📋 Работа с документами"
        )
    elif user['role'] == 'supervisor':
        # Получаем статистику для супервайзера
        stats = db.get_supervisor_stats(user['telegram_id'])
        
        profile_text = (
            f"👤 <b>Профиль супервайзера</b>\n\n"
            f"🆔 ID: {user['telegram_id']}\n"
            f"👨‍🏫 Имя: {user['first_name']}\n"
            f"👨‍🏫 Фамилия: {user['last_name'] or 'Не указана'}\n"
            f"📞 Телефон: {user['phone'] or 'Не указан'}\n"
            f"🎯 Роль: {role_description}\n"
            f"📅 Регистрация: {user['created_at'][:10] if user['created_at'] else 'Не указана'}\n\n"
            f"<b>Статистика системы:</b>\n"
            f"• 📊 Всего ошибок: {stats['total_reports']}\n"
            f"• 📅 Ошибок сегодня: {stats['today_reports']}\n\n"
            f"<b>Доступные функции:</b>\n"
            f"• 📅 Просмотр ошибок за сегодня\n"
            f"• 📋 Просмотр последних 10 ошибок"
        )
        
    else:
        profile_text = (
            f"👤 <b>Профиль пользователя</b>\n\n"
            f"🆔 ID: {user['telegram_id']}\n"
            f"👤 Имя: {user['first_name']}\n"
            f"👤 Фамилия: {user['last_name'] or 'Не указана'}\n"
            f"📞 Телефон: {user['phone'] or 'Не указан'}\n"
            f"🎯 Роль: {role_description}\n"
            f"📅 Регистрация: {user['created_at'][:10] if user['created_at'] else 'Не указана'}"
        )
    
    await message.answer(profile_text, reply_markup=get_main_menu(user['role']))