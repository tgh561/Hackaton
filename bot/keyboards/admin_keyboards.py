from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_admin_main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📋 Список пользователей"), KeyboardButton(text="👤 Добавить пользователя")],
            [KeyboardButton(text="⚙️ Изменить роль"), KeyboardButton(text="📊 Статистика")],
            [KeyboardButton(text="🔙 В главное меню")]
        ],
        resize_keyboard=True
    )

def get_cancel_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Отмена")]],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def get_back_to_admin_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🔙 В админ панель")]],
        resize_keyboard=True
    )

def get_users_format_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📄 Показать в чате"), KeyboardButton(text="📊 Скачать PDF")],
            [KeyboardButton(text="❌ Отмена")]
        ],
        resize_keyboard=True
    )