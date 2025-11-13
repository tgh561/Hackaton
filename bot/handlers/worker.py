from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, StateFilter

from database import db
from keyboards.worker_kb import (
    get_worker_main_keyboard,
    get_contact_supervisor_keyboard,
    get_back_keyboard
)

router = Router()


# Проверка прав работника
async def check_worker(user_id: int) -> bool:
    user = db.get_user(user_id)
    if not user:
        return False
    return user['role'] == 'worker'


@router.message(F.text == "👤 Мой профиль")
async def worker_profile(message: Message):
    """Показать профиль работника"""
    if not await check_worker(message.from_user.id):
        await message.answer("❌ У вас нет прав доступа к этой функции.")
        return

    user = db.get_user(message.from_user.id)
    
    if not user:
        await message.answer("❌ Профиль не найден")
        return

    # Получаем информацию о супервайзере
    supervisor = db.get_supervisor_by_worker(user['telegram_id'])
    
    profile_text = (
        f"👤 <b>Профиль работника</b>\n\n"
        f"🆔 ID: {user['telegram_id']}\n"
        f"👷 Имя: {user['first_name']}\n"
        f"👷 Фамилия: {user['last_name'] or 'Не указана'}\n"
        f"📞 Телефон: {user['phone'] or 'Не указан'}\n"
        f"🎯 Роль: Работник\n"
        f"📅 Регистрация: {user['created_at'][:10] if user['created_at'] else 'Не указана'}\n\n"
    )

    if supervisor:
        profile_text += (
            f"<b>Супервайзер:</b>\n"
            f"👨‍🏫 Имя: {supervisor['first_name']} {supervisor['last_name'] or ''}\n"
            f"📞 Телефон: {supervisor['phone'] or 'Не указан'}\n"
            f"🆔 ID: {supervisor['telegram_id']}\n"
        )
    else:
        profile_text += "❌ Супервайзер не назначен\n"

    await message.answer(profile_text, reply_markup=get_worker_main_keyboard())


@router.message(F.text == "📞 Связь с супервайзером")
async def contact_supervisor_menu(message: Message):
    """Меню связи с супервайзером"""
    if not await check_worker(message.from_user.id):
        await message.answer("❌ У вас нет прав доступа к этой функции.")
        return

    user = db.get_user(message.from_user.id)
    supervisor = db.get_supervisor_by_worker(user['telegram_id'])
    
    if not supervisor:
        await message.answer(
            "❌ Супервайзер не назначен\n"
            "Обратитесь к администратору",
            reply_markup=get_worker_main_keyboard()
        )
        return

    supervisor_info = (
        f"👨‍🏫 <b>Ваш супервайзер</b>\n\n"
        f"👤 Имя: {supervisor['first_name']} {supervisor['last_name'] or ''}\n"
        f"📞 Телефон: {supervisor['phone'] or 'Не указан'}\n"
        f"🆔 ID: {supervisor['telegram_id']}\n\n"
        f"Выберите способ связи:"
    )
    
    await message.answer(supervisor_info, reply_markup=get_contact_supervisor_keyboard())


@router.message(F.text == "📞 Позвонить")
async def call_supervisor(message: Message):
    """Позвонить супервайзеру"""
    if not await check_worker(message.from_user.id):
        return

    user = db.get_user(message.from_user.id)
    supervisor = db.get_supervisor_by_worker(user['telegram_id'])
    
    if supervisor and supervisor['phone']:
        await message.answer(
            f"📞 <b>Контакт супервайзера для звонка</b>\n\n"
            f"👤 {supervisor['first_name']} {supervisor['last_name'] or ''}\n"
            f"📞 Телефон: <code>{supervisor['phone']}</code>\n\n"
            f"<i>Нажмите на номер телефона чтобы позвонить</i>",
            reply_markup=get_contact_supervisor_keyboard()
        )
    else:
        await message.answer(
            "❌ Телефон супервайзера не указан\n"
            "Используйте другие способы связи",
            reply_markup=get_contact_supervisor_keyboard()
        )


@router.message(F.text == "✉️ Написать сообщение")
async def message_supervisor(message: Message):
    """Написать сообщение супервайзеру"""
    if not await check_worker(message.from_user.id):
        return

    user = db.get_user(message.from_user.id)
    supervisor = db.get_supervisor_by_worker(user['telegram_id'])
    
    if supervisor:
        await message.answer(
            f"✉️ <b>Написать сообщение супервайзеру</b>\n\n"
            f"👤 {supervisor['first_name']} {supervisor['last_name'] or ''}\n"
            f"🆔 ID: <code>{supervisor['telegram_id']}</code>\n\n"
            f"<i>Вы можете написать сообщение напрямую в Telegram</i>",
            reply_markup=get_contact_supervisor_keyboard()
        )
    else:
        await message.answer(
            "❌ Супервайзер не найден",
            reply_markup=get_contact_supervisor_keyboard()
        )


@router.message(F.text == "ℹ️ Помощь")
async def worker_help(message: Message):
    """Помощь для работника"""
    if not await check_worker(message.from_user.id):
        await message.answer("❌ У вас нет прав доступа к этой функции.")
        return

    help_text = (
        "ℹ️ <b>Помощь для работника</b>\n\n"
        "<b>Доступные функции:</b>\n"
        "• <b>👤 Мой профиль</b> - информация о вас и вашем супервайзере\n"
        "• <b>📞 Связь с супервайзером</b> - различные способы связи с руководителем\n"
        "• <b>ℹ️ Помощь</b> - эта справка\n\n"
        "<b>Как связаться с супервайзером:</b>\n"
        "• <b>📞 Позвонить</b> - показать номер телефона супервайзера\n"
        "• <b>✉️ Написать сообщение</b> - показать ID для связи в Telegram\n\n"
        "<b>Если возникли проблемы:</b>\n"
        "Обратитесь к администратору системы"
    )
    
    await message.answer(help_text, reply_markup=get_worker_main_keyboard())


# Обработчики навигации
@router.message(F.text == "🔙 Назад")
async def back_to_worker_main(message: Message):
    """Возврат в главное меню"""
    if not await check_worker(message.from_user.id):
        return

    await message.answer(
        "👷 Панель работника\n\n"
        "Выберите действие:",
        reply_markup=get_worker_main_keyboard()
    )


# Отладочные команды (только для разработки)
@router.message(Command("debug_worker"))
async def debug_worker(message: Message):
    """Отладочная информация для работника"""
    if not await check_worker(message.from_user.id):
        return

    user = db.get_user(message.from_user.id)
    supervisor = db.get_supervisor_by_worker(user['telegram_id'])
    
    debug_info = "🧪 <b>ДЕБАГ ИНФОРМАЦИЯ РАБОТНИКА</b>\n\n"
    debug_info += f"🆔 Ваш ID: {user['telegram_id']}\n"
    debug_info += f"👤 Ваше имя: {user['first_name']} {user['last_name'] or ''}\n"
    debug_info += f"🎯 Ваша роль: {user['role']}\n"
    debug_info += f"📅 Регистрация: {user['created_at']}\n\n"
    
    if supervisor:
        debug_info += (
            f"<b>Супервайзер:</b>\n"
            f"🆔 ID супервайзера: {supervisor['telegram_id']}\n"
            f"👤 Имя супервайзера: {supervisor['first_name']} {supervisor['last_name'] or ''}\n"
            f"📞 Телефон супервайзера: {supervisor['phone'] or 'Не указан'}\n"
        )
    else:
        debug_info += "❌ Супервайзер не назначен\n"

    await message.answer(debug_info)


@router.message(Command("worker_info"))
async def worker_info(message: Message):
    """Информация о работнике"""
    if not await check_worker(message.from_user.id):
        return

    user = db.get_user(message.from_user.id)
    workers_count = len(db.get_workers_by_supervisor(user['supervisor_id'])) if user['supervisor_id'] else 0
    
    info_text = (
        f"👷 <b>Информация о работнике</b>\n\n"
        f"🆔 Ваш ID: {user['telegram_id']}\n"
        f"👤 ФИО: {user['first_name']} {user['last_name'] or ''}\n"
        f"📞 Телефон: {user['phone'] or 'Не указан'}\n"
        f"🆔 ID супервайзера: {user['supervisor_id'] or 'Не назначен'}\n"
        f"👥 Работников у вашего супервайзера: {workers_count}\n"
        f"📅 Аккаунт создан: {user['created_at'][:10] if user['created_at'] else 'Неизвестно'}"
    )
    
    await message.answer(info_text, reply_markup=get_worker_main_keyboard())