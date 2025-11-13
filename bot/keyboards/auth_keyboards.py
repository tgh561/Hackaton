from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def get_phone_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[
            KeyboardButton(text="📱 Отправить телефон", request_contact=True)
        ]],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def get_role_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="👷 Рабочий")],
            [KeyboardButton(text="👨‍💼 Руководитель")],
            [KeyboardButton(text="👁️ Проверяющий")],
            [KeyboardButton(text="👨‍💼 Администратор")],
            [KeyboardButton(text="❌ Отмена")]
        ],
        resize_keyboard=True
    )