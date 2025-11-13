from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


def get_inspector_main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📋 Мои проверки")],
            [KeyboardButton(text="📍 Доступные проверки")],
            [KeyboardButton(text="👤 Мой профиль"), KeyboardButton(text="ℹ️ Помощь")],
            [KeyboardButton(text="🔙 В главное меню")]
        ],
        resize_keyboard=True
    )


def get_inspections_keyboard(inspections_data):
    """Создает клавиатуру с кнопками для каждой проверки"""
    keyboard = []

    for place_id, inspection_data in inspections_data.items():
        # Создаем кнопку для каждой проверки
        button_text = f"📞 Связаться #{place_id}"
        keyboard.append([KeyboardButton(text=button_text)])

    # Добавляем кнопку назад
    keyboard.append([KeyboardButton(text="🔙 Назад")])

    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def get_back_to_inspections_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔙 К списку проверок")]
        ],
        resize_keyboard=True
    )


def get_available_inspections_keyboard(available_inspections):
    """Клавиатура для доступных проверок"""
    keyboard = []

    for place_id, inspection_data in available_inspections.items():
        button_text = f"✅ Взять проверку #{place_id}"
        keyboard.append([KeyboardButton(text=button_text)])

    keyboard.append([KeyboardButton(text="🔙 Назад")])

    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def get_confirm_inspection_keyboard(place_id: str):
    """Создает клавиатуру для подтверждения/отклонения проверки"""
    # Убедимся, что place_id передается правильно
    print(f"DEBUG: Creating keyboard for place_id: {place_id}")

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Подтвердить",
                    callback_data=f"accept_inspection_{place_id}"
                ),
                InlineKeyboardButton(
                    text="❌ Отклонить",
                    callback_data=f"decline_inspection_{place_id}"
                )
            ]
        ]
    )


def get_help_keyboard():
    """Клавиатура для раздела помощи"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📋 Мои проверки"), KeyboardButton(text="📍 Доступные проверки")],
            [KeyboardButton(text="👤 Мой профиль")],
            [KeyboardButton(text="🔙 Назад")]
        ],
        resize_keyboard=True
    )