from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

def get_schedules_keyboard():
    """
    Клавиатура для раздела графиков менеджера
    """
    builder = ReplyKeyboardBuilder()
    
    builder.add(
        KeyboardButton(text="👀 Просмотреть график"),
        KeyboardButton(text="📤 Загрузить график"),
        KeyboardButton(text="🔙 Назад")
    )
    
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)

def get_reports_keyboard():
    """
    Клавиатура для раздела отчетов менеджера
    """
    builder = ReplyKeyboardBuilder()
    
    builder.add(
        KeyboardButton(text="📅 Месячный отчет"),
        KeyboardButton(text="📊 Ежедневный отчет"),
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

def get_cancel_keyboard():
    """
    Клавиатура для отмены действий
    """
    builder = ReplyKeyboardBuilder()
    
    builder.add(KeyboardButton(text="❌ Отмена"))
    
    return builder.as_markup(resize_keyboard=True)

def get_confirm_keyboard():
    """
    Клавиатура для подтверждения действий
    """
    builder = ReplyKeyboardBuilder()
    
    builder.add(
        KeyboardButton(text="✅ Подтвердить"),
        KeyboardButton(text="❌ Отменить")
    )
    
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)

def get_file_actions_keyboard():
    """
    Клавиатура для действий с файлами
    """
    builder = ReplyKeyboardBuilder()
    
    builder.add(
        KeyboardButton(text="📎 Отправить файл"),
        KeyboardButton(text="⏭️ Пропустить"),
        KeyboardButton(text="🔙 Назад")
    )
    
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)

def get_date_selection_keyboard():
    """
    Клавиатура для быстрого выбора дат (опционально)
    """
    builder = ReplyKeyboardBuilder()
    
    builder.add(
        KeyboardButton(text="📅 Сегодня"),
        KeyboardButton(text="📅 Вчера"),
        KeyboardButton(text="📅 Текущая неделя"),
        KeyboardButton(text="🔙 Назад")
    )
    
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)

def get_report_period_keyboard():
    """
    Клавиатура для выбора периода отчетов
    """
    builder = ReplyKeyboardBuilder()
    
    builder.add(
        KeyboardButton(text="📊 За сегодня"),
        KeyboardButton(text="📈 За неделю"),
        KeyboardButton(text="📋 За месяц"),
        KeyboardButton(text="🔙 Назад")
    )
    
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)

def get_help_keyboard():
    """
    Клавиатура для раздела помощи менеджера
    """
    builder = ReplyKeyboardBuilder()
    
    builder.add(
        KeyboardButton(text="📊 Графики"),
        KeyboardButton(text="📈 Отчеты"),
        KeyboardButton(text="👤 Мой профиль"),
        KeyboardButton(text="🔙 Назад")
    )
    
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)