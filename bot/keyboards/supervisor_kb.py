from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

# Клавиатура для раздела отчетов об ошибках (упрощенная)
def get_error_reports_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.add(
        KeyboardButton(text="📅 Ошибки за сегодня"),
        KeyboardButton(text="📋 Последние 10 ошибок"),
        KeyboardButton(text="🔙 Назад")
    )
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)

# Клавиатура назад
def get_back_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="🔙 Назад"))
    return builder.as_markup(resize_keyboard=True)