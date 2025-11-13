from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


def get_inspector_main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📋 Мои проверки"), KeyboardButton(text="✅ Согласованные проверки")],
            [KeyboardButton(text="📊 Чек-листы")],
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


def get_approved_inspections_keyboard(approved_inspections):
    """Клавиатура для согласованных проверок с чек-листами"""
    keyboard = []

    for place_id, inspection_data in approved_inspections.items():
        # Кнопка для открытия чек-листа
        button_text = f"📝 Чек-лист #{place_id}"
        keyboard.append([KeyboardButton(text=button_text)])

    keyboard.append([KeyboardButton(text="🔙 Назад")])

    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def get_checklist_management_keyboard(place_id: str, has_subdivisions: bool = False):
    """Клавиатура для управления чек-листом"""
    keyboard = [
        [KeyboardButton(text=f"👀 Просмотр чек-листа #{place_id}")],
        [KeyboardButton(text=f"📝 Заполнить раздел А #{place_id}")]
    ]

    # Динамически добавляем кнопки для разделов с подразделами
    if has_subdivisions:
        keyboard.extend([
            [KeyboardButton(text=f"📝 Заполнить раздел B1 #{place_id}")],
            [KeyboardButton(text=f"📝 Заполнить раздел B2 #{place_id}")]
        ])
    else:
        keyboard.append([KeyboardButton(text=f"📝 Заполнить раздел B #{place_id}")])

    keyboard.extend([
        [KeyboardButton(text=f"📝 Заполнить раздел C #{place_id}")],
        [KeyboardButton(text=f"📊 Результаты #{place_id}")],
        [KeyboardButton(text="🔙 К согласованным проверкам")]
    ])

    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def get_section_filling_keyboard(place_id: str, section: str, criteria_data: list):
    """Клавиатура для заполнения раздела чек-листа"""
    keyboard = []

    # Только основные действия, не все критерии сразу
    keyboard.extend([
        [KeyboardButton(text="✅ Соответствует"), KeyboardButton(text="❌ Не соответствует")],
        [KeyboardButton(text="💾 Сохранить и выйти")],
        [KeyboardButton(text="🔙 К управлению чек-листом")]
    ])

    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def get_checklist_keyboard(place_id: str):
    """Клавиатура для работы с чек-листом"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=f"📋 Открыть чек-лист #{place_id}")],
            [KeyboardButton(text=f"✅ Заполнить чек-лист #{place_id}")],
            [KeyboardButton(text="🔙 К согласованным проверкам")]
        ],
        resize_keyboard=True
    )


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

def get_checklist_management_keyboard(place_id: str, has_subdivisions: bool = False):
    """Клавиатура для управления чек-листом"""
    keyboard = [
        [KeyboardButton(text=f"👀 Просмотр чек-листа #{place_id}")],
        [KeyboardButton(text=f"📝 Заполнить раздел А #{place_id}")]
    ]

    # Динамически добавляем кнопки для разделов с подразделами
    if has_subdivisions:
        keyboard.extend([
            [KeyboardButton(text=f"📝 Заполнить раздел B1 #{place_id}")],
            [KeyboardButton(text=f"📝 Заполнить раздел B2 #{place_id}")]
        ])
    else:
        keyboard.append([KeyboardButton(text=f"📝 Заполнить раздел B #{place_id}")])

    keyboard.extend([
        [KeyboardButton(text=f"📝 Заполнить раздел C #{place_id}")],
        [KeyboardButton(text=f"📊 Результаты #{place_id}")],
        [KeyboardButton(text="🔙 К согласованным проверкам")]
    ])

    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def get_confirm_inspection_keyboard(place_id: str):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"accept_inspection_{place_id}"),
                InlineKeyboardButton(text="❌ Отклонить", callback_data=f"decline_inspection_{place_id}")
            ]
        ]
    )