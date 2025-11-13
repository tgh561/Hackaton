from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

def get_worker_main_keyboard():
    """
    Основная клавиатура для работника
    """
    builder = ReplyKeyboardBuilder()
    
    builder.add(
        KeyboardButton(text="👤 Мой профиль"),
        KeyboardButton(text="📞 Связь с супервайзером"),
        KeyboardButton(text="ℹ️ Помощь")
    )
    
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)

def get_contact_supervisor_keyboard():
    """
    Клавиатура для связи с супервайзером
    """
    builder = ReplyKeyboardBuilder()
    
    builder.add(
        KeyboardButton(text="📞 Позвонить"),
        KeyboardButton(text="✉️ Написать сообщение"),
        KeyboardButton(text="🔙 Назад")
    )
    
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)

def get_back_keyboard():
    """
    Упрощенная клавиатура только с кнопкой Назад
    """
    builder = ReplyKeyboardBuilder()
    
    builder.add(KeyboardButton(text="🔙 Назад"))
    
    return builder.as_markup(resize_keyboard=True)