from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

def get_main_menu(role: str):
    """Главное меню в зависимости от роли"""
    builder = ReplyKeyboardBuilder()
    
    if role == 'manager':
        builder.add(
            KeyboardButton(text="👤 Мой профиль"),
            KeyboardButton(text="📊 Графики"),
            KeyboardButton(text="📈 Отчеты"),
            KeyboardButton(text="ℹ️ Помощь")
        )
    elif role == 'supervisor':
        builder.add(
            KeyboardButton(text="👤 Мой профиль"),
            KeyboardButton(text="⚠️ Отчеты об ошибках"),
            KeyboardButton(text="ℹ️ Помощь")
        )
    else:
        builder.add(
            KeyboardButton(text="👤 Мой профиль"),
            KeyboardButton(text="ℹ️ Помощь")
        )
    
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)