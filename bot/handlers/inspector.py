from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, StateFilter

from database.simple_db import db, UserRole
from database.places_db import places_db
from utils.states import InspectorStates
from utils.inspection_service import inspection_service
from keyboards.inspector_keyboards import (
    get_inspector_main_keyboard,
    get_inspections_keyboard,
    get_back_to_inspections_keyboard,
    get_available_inspections_keyboard,
    get_approved_inspections_keyboard,
    get_checklist_keyboard
)
# Добавляем импорт чек-листов
from utils.checklists import checklist_manager
from database.checklists_db import checklists_db
from utils.states import ChecklistStates
router = Router()


# Проверка прав проверяющего
async def check_inspector(user_id: int) -> bool:
    user = db.get_user(user_id)
    if not user:
        return False
    return user['role'] == UserRole.INSPECTOR.value


@router.message(F.text == "📋 Мои проверки")
async def my_inspections(message: Message):
    if not await check_inspector(message.from_user.id):
        await message.answer("❌ У вас нет прав доступа к этой функции.")
        return

    inspections = places_db.get_inspections_by_inspector(message.from_user.id)

    if not inspections:
        await message.answer(
            "📭 У вас нет назначенных проверок.",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text="🔙 Назад")]],
                resize_keyboard=True
            )
        )
        return

    inspections_list = "📋 Ваши проверки:\n\n"

    for place_id, inspection_data in inspections.items():
        info = inspection_service.get_inspection_info(place_id)

        inspections_list += (
            f"🔹 Место: {place_id}\n"
            f"📍 Адрес: {info['address']}\n"
            f"👷 Бригадир: {info['supervisor_name']}\n"
            f"📞 Телефон: {info['supervisor_phone']}\n"
            f"🆔 ID бригадира: {info['supervisor_id']}\n"
            f"📅 Время проверки: {info['date']}\n"
        )

        if info['date'] == "Не назначена":
            inspections_list += "⚠️ Время не назначено - свяжитесь с бригадиром\n"

        inspections_list += f"────────────────────\n"

    # Отправляем список и клавиатуру с кнопками для каждой проверки
    if len(inspections_list) > 4000:
        parts = [inspections_list[i:i + 4000] for i in range(0, len(inspections_list), 4000)]
        for part in parts:
            await message.answer(part)
        await message.answer("Выберите проверку для связи с бригадиром:",
                             reply_markup=get_inspections_keyboard(inspections))
    else:
        await message.answer(
            inspections_list + "\nВыберите проверку для связи с бригадиром:",
            reply_markup=get_inspections_keyboard(inspections)
        )

# Добавляем новые обработчики:

@router.message(F.text == "✅ Согласованные проверки")
async def approved_inspections(message: Message):
    """Показывает согласованные проверки (с назначенным временем)"""
    if not await check_inspector(message.from_user.id):
        await message.answer("❌ У вас нет прав доступа к этой функции.")
        return

    # Получаем только проверки с назначенным временем
    inspections = places_db.get_approved_inspections_by_inspector(message.from_user.id)

    if not inspections:
        await message.answer(
            "📭 У вас нет согласованных проверок.\n"
            "Согласованные проверки - это проверки с назначенным временем.",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text="🔙 Назад")]],
                resize_keyboard=True
            )
        )
        return

    inspections_list = "✅ Согласованные проверки:\n\n"

    for place_id, inspection_data in inspections.items():
        info = inspection_service.get_inspection_info(place_id)

        inspections_list += (
            f"🔹 Место: {place_id}\n"
            f"📍 Адрес: {info['address']}\n"
            f"👷 Бригадир: {info['supervisor_name']}\n"
            f"📞 Телефон: {info['supervisor_phone']}\n"
            f"⏰ Время проверки: {info['date']}\n"
            f"────────────────────\n"
        )

    # Отправляем список и клавиатуру с кнопками чек-листов
    if len(inspections_list) > 4000:
        parts = [inspections_list[i:i + 4000] for i in range(0, len(inspections_list), 4000)]
        for part in parts:
            await message.answer(part)
        await message.answer("Выберите проверку для работы с чек-листом:",
                             reply_markup=get_approved_inspections_keyboard(inspections))
    else:
        await message.answer(
            inspections_list + "\nВыберите проверку для работы с чек-листом:",
            reply_markup=get_approved_inspections_keyboard(inspections)
        )


@router.message(F.text.startswith("📝 Чек-лист #"))
async def show_checklist_options(message: Message):
    """Показывает опции для работы с чек-листом"""
    if not await check_inspector(message.from_user.id):
        return

    try:
        # Извлекаем ID места из текста кнопки
        place_id = message.text.split('#')[1]

        # Проверяем, что проверка согласована и принадлежит проверяющему
        inspection_data = places_db.search.get(place_id)
        if (not inspection_data or
                inspection_data.get('inspector') != str(message.from_user.id) or
                places_db.get_inspection_status(place_id) != 'approved'):
            await message.answer("❌ Проверка не найдена или не согласована.")
            return

        info = inspection_service.get_inspection_info(place_id)

        await message.answer(
            f"📋 Работа с чек-листом\n\n"
            f"🏢 Место: {place_id}\n"
            f"📍 Адрес: {info['address']}\n"
            f"⏰ Время проверки: {info['date']}\n\n"
            f"Выберите действие:",
            reply_markup=get_checklist_keyboard(place_id)
        )

    except (ValueError, IndexError):
        await message.answer("❌ Ошибка при обработке запроса.")


@router.message(F.text.startswith("📋 Открыть чек-лист #"))
async def open_checklist(message: Message):
    """Показывает чек-лист для проверки с актуальными статусами"""
    if not await check_inspector(message.from_user.id):
        return

    try:
        place_id = message.text.split('#')[1]

        # Проверяем доступ к проверке
        inspection_data = places_db.search.get(place_id)
        if (not inspection_data or
                inspection_data.get('inspector') != str(message.from_user.id)):
            await message.answer("❌ Проверка не найдена.")
            return

        # Получаем актуальные данные чек-листа
        checklist = checklists_db.get_checklist(place_id)
        if not checklist:
            # Создаем новый если нет
            inspector_name = f"{message.from_user.first_name}"
            template = checklist_manager.get_checklist_template(place_id)
            checklists_db.create_checklist(place_id, inspector_name, template)
            checklist = checklists_db.get_checklist(place_id)

        # Форматируем чек-лист с актуальными статусами
        checklist_message = checklist_manager.format_checklist_message(place_id, checklist)

        await message.answer(
            checklist_message,
            reply_markup=get_checklist_keyboard(place_id)
        )

    except (ValueError, IndexError):
        await message.answer("❌ Ошибка при обработке запроса.")


@router.message(F.text.startswith("✅ Заполнить чек-лист #"))
async def start_fill_checklist(message: Message, state: FSMContext):
    """Начинает процесс заполнения чек-листа"""
    if not await check_inspector(message.from_user.id):
        return

    try:
        place_id = message.text.split('#')[1]

        # Проверяем доступ к проверке
        inspection_data = places_db.search.get(place_id)
        if (not inspection_data or
                inspection_data.get('inspector') != str(message.from_user.id)):
            await message.answer("❌ Проверка не найдена.")
            return

        # Создаем чек-лист если его нет
        checklist = checklists_db.get_checklist(place_id)
        if not checklist:
            inspector_name = f"{message.from_user.first_name}"
            template = checklist_manager.get_checklist_template(place_id)
            checklists_db.create_checklist(place_id, inspector_name, template)
            checklist = checklists_db.get_checklist(place_id)

        # Показываем меню заполнения
        template = checklist['checklist_data']

        # Показываем прогресс
        progress = checklists_db.get_checklist_progress(place_id)

        keyboard = []
        for section_key in template['sections'].keys():
            keyboard.append([KeyboardButton(text=f"📝 Заполнить раздел {section_key} #{place_id}")])

        keyboard.append([KeyboardButton(text="📊 Статус заполнения")])
        keyboard.append([KeyboardButton(text="🔙 Назад")])

        sections_info = f"📋 Прогресс заполнения: {progress['percentage']}% ({progress['completed']}/{progress['total']})\n\n"
        sections_info += "Выберите раздел для заполнения:\n\n"

        for section_key, section_data in template['sections'].items():
            sections_info += f"🔹 Раздел {section_key}: {section_data['description']}\n"
            criteria_count = len(section_data['criteria'])
            # Считаем заполненные критерии в разделе
            filled = sum(1 for c in section_data['criteria'] if c.get('complies') is not None)
            sections_info += f"   📊 Заполнено: {filled}/{criteria_count}\n\n"

        await message.answer(
            sections_info,
            reply_markup=ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
        )

    except (ValueError, IndexError):
        await message.answer("❌ Ошибка при обработке запроса.")


@router.message(F.text.startswith("📝 Заполнить раздел "))
async def fill_section(message: Message, state: FSMContext):
    """Заполнение конкретного раздела чек-листа"""
    if not await check_inspector(message.from_user.id):
        return

    try:
        # "📝 Заполнить раздел A #place_1"
        text_parts = message.text.split(' ')
        section = text_parts[3]  # A, B, C
        place_id = text_parts[4].split('#')[1]

        # Проверяем доступ
        inspection_data = places_db.search.get(place_id)
        if not inspection_data or inspection_data.get('inspector') != str(message.from_user.id):
            await message.answer("❌ Нет доступа к проверке.")
            return

        checklist = checklists_db.get_checklist(place_id)
        if not checklist:
            await message.answer("❌ Чек-лист не найдена.")
            return

        template = checklist['checklist_data']
        section_data = template['sections'].get(section)

        if not section_data:
            await message.answer(f"❌ Раздел {section} не найден.")
            return

        # Показываем первый критерий раздела
        criteria = section_data['criteria']
        if not criteria:
            await message.answer(f"❌ В разделе {section} нет критериев.")
            return

        await state.set_state(ChecklistStates.filling_section)
        await state.update_data(
            current_section=section,
            current_place_id=place_id,
            current_criteria=criteria,
            current_index=0
        )

        await show_current_criterion(message, state)

    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")
        await state.clear()


async def show_current_criterion(message: Message, state: FSMContext):
    """Показывает текущий критерий для заполнения"""
    user_data = await state.get_data()

    section = user_data['current_section']
    place_id = user_data['current_place_id']
    criteria = user_data['current_criteria']
    current_index = user_data['current_index']

    criterion = criteria[current_index]

    # Проверяем текущий статус - БЛЯТЬ ТЕПЕРЬ ПРАВИЛЬНО!
    current_status = ""
    if criterion.get('complies') is True:
        current_status = "\n📊 Текущий статус: ✅ Соответствует"
    elif criterion.get('does_not_comply') is True:
        current_status = f"\n📊 Текущий статус: ❌ Не соответствует\n💬 Комментарий: {criterion.get('comment', 'нет')}"

    await message.answer(
        f"📝 Раздел {section}\n"
        f"🔸 Критерий {current_index + 1} из {len(criteria)}:\n\n"
        f"{criterion['description']}"
        f"{current_status}\n\n"
        f"Выберите статус:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="✅ Соответствует"), KeyboardButton(text="❌ Не соответствует")],
                [KeyboardButton(text="⏩ Пропустить"), KeyboardButton(text="🔙 Назад")]
            ],
            resize_keyboard=True
        )
    )


@router.message(ChecklistStates.filling_section, F.text.in_(["✅ Соответствует", "❌ Не соответствует", "⏩ Пропустить"]))
async def process_criterion_choice(message: Message, state: FSMContext):
    """Обрабатывает выбор статуса критерия"""
    user_data = await state.get_data()

    section = user_data['current_section']
    place_id = user_data['current_place_id']
    criteria = user_data['current_criteria']
    current_index = user_data['current_index']

    current_criterion = criteria[current_index]

    if message.text == "⏩ Пропустить":
        # Просто переходим к следующему
        await go_to_next_criterion(message, state)
        return

    # Сохраняем базовый статус
    complies = message.text == "✅ Соответствует"

    if not complies:  # Если не соответствует - запрашиваем комментарий
        await state.update_data(
            pending_criterion=current_criterion,
            pending_complies=complies
        )
        await state.set_state(ChecklistStates.waiting_for_comment)

        await message.answer(
            f"❌ Критерий не соответствует требованиям.\n\n"
            f"Пожалуйста, укажите комментарий о выявленном несоответствии:",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text="⏩ Без комментария")]],
                resize_keyboard=True
            )
        )
    else:
        # Если соответствует - просто сохраняем
        checklists_db.update_criterion(
            place_id=place_id,
            section=section,
            criterion_number=current_criterion['number'],
            complies=complies,
            comment=""
        )
        await message.answer("✅ Статус сохранен")
        await go_to_next_criterion(message, state)


@router.message(ChecklistStates.waiting_for_comment, F.text)
async def process_comment(message: Message, state: FSMContext):
    """Обрабатывает комментарий для несоответствия"""
    user_data = await state.get_data()

    section = user_data['current_section']
    place_id = user_data['current_place_id']
    current_criterion = user_data['pending_criterion']
    complies = user_data['pending_complies']

    comment = message.text if message.text != "⏩ Без комментария" else ""

    # Запрашиваем фото
    await state.update_data(pending_comment=comment)
    await state.set_state(ChecklistStates.waiting_for_photo)

    await message.answer(
        f"📸 Теперь пришлите фото несоответствия:\n\n"
        f"<i>Или нажмите '⏩ Без фото' чтобы продолжить</i>",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="⏩ Без фото")]],
            resize_keyboard=True
        )
    )


@router.message(ChecklistStates.waiting_for_photo, F.text == "⏩ Без фото")
@router.message(ChecklistStates.waiting_for_photo, F.photo)
async def process_photo(message: Message, state: FSMContext):
    """Обрабатывает фото или пропуск фото"""
    user_data = await state.get_data()

    section = user_data['current_section']
    place_id = user_data['current_place_id']
    current_criterion = user_data['pending_criterion']
    complies = user_data['pending_complies']
    comment = user_data['pending_comment']

    photo_path = None
    if message.photo:
        # Сохраняем информацию о фото
        photo_file_id = message.photo[-1].file_id
        photo_path = checklists_db.save_photo(place_id, section, current_criterion['number'], photo_file_id)
        photo_text = "✅ Фото сохранено"
    else:
        photo_text = "📷 Фото не прикреплено"

    # Сохраняем критерий со всей информацией
    checklists_db.update_criterion(
        place_id=place_id,
        section=section,
        criterion_number=current_criterion['number'],
        complies=complies,
        comment=comment,
        photo_path=photo_path
    )

    await message.answer(
        f"❌ Несоответствие сохранено!\n"
        f"💬 Комментарий: {comment if comment else 'нет'}\n"
        f"{photo_text}",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="✅ Соответствует"), KeyboardButton(text="❌ Не соответствует")],
                [KeyboardButton(text="⏩ Пропустить"), KeyboardButton(text="🔙 Назад")]
            ],
            resize_keyboard=True
        )
    )

    # Возвращаемся к заполнению и переходим к следующему критерию
    await state.set_state(ChecklistStates.filling_section)
    await go_to_next_criterion(message, state)


async def go_to_next_criterion(message: Message, state: FSMContext):
    """Переходит к следующему критерию или завершает раздел"""
    user_data = await state.get_data()

    criteria = user_data['current_criteria']
    current_index = user_data['current_index'] + 1

    if current_index < len(criteria):
        await state.update_data(current_index=current_index)
        await show_current_criterion(message, state)
    else:
        # Раздел завершен - БЛЯТЬ ВОЗВРАЩАЕМ ПРАВИЛЬНУЮ КЛАВИАТУРУ!
        section = user_data['current_section']
        place_id = user_data['current_place_id']

        # Получаем актуальные данные для прогресса
        checklist = checklists_db.get_checklist(place_id)
        progress = checklists_db.get_checklist_progress(place_id)

        completion_text = ""
        if checklist["status"] == "completed":
            completion_text = f"\n\n🎉 ЧЕК-ЛИСТ ПОЛНОСТЬЮ ЗАПОЛНЕН! 🎉\n"
            completion_text += f"✅ Все критерии проверены\n"
            completion_text += f"📊 Итоговый прогресс: 100%"

        await message.answer(
            f"🎉 Раздел {section} заполнен!\n"
            f"✅ Обработано критериев: {len(criteria)}"
            f"{completion_text}",
            reply_markup=get_checklist_keyboard(place_id)  # ← БЛЯТЬ ВОТ ОНА ПРАВИЛЬНАЯ КЛАВИАТУРА!
        )
        await state.clear()


# Добавляем обработчик для кнопки "🔙 Назад" во время заполнения
@router.message(ChecklistStates.filling_section, F.text == "🔙 Назад")
async def back_from_filling(message: Message, state: FSMContext):
    """Возврат из заполнения раздела"""
    user_data = await state.get_data()
    place_id = user_data.get('current_place_id')

    await state.clear()

    if place_id:
        # Возвращаем к управлению чек-листом
        await message.answer(
            "Возврат к управлению чек-листом:",
            reply_markup=get_checklist_keyboard(place_id)
        )
    else:
        await message.answer(
            "Возврат в меню:",
            reply_markup=get_inspector_main_keyboard()
        )
@router.message(F.text == "📊 Чек-листы")
async def checklists_info(message: Message):
    """Информация о чек-листах"""
    if not await check_inspector(message.from_user.id):
        await message.answer("❌ У вас нет прав доступа к этой функции.")
        return

    await message.answer(
        "📊 Работа с чек-листами\n\n"
        "Чек-листы доступны для согласованных проверок - тех, у которых назначено время.\n\n"
        "Для работы с чек-листами:\n"
        "1. Перейдите в '✅ Согласованные проверки'\n"
        "2. Выберите проверку\n"
        "3. Откройте или заполните чек-лист\n\n"
        "Каждый тип объекта имеет свой специализированный чек-лист.",
        reply_markup=get_inspector_main_keyboard()
    )


# Добавляем обработчик возврата к согласованным проверкам
@router.message(F.text == "🔙 К согласованным проверкам")
async def back_to_approved_inspections(message: Message):
    """Возврат к списку согласованных проверок"""
    if not await check_inspector(message.from_user.id):
        return

    await approved_inspections(message)

@router.message(F.text.startswith("📞 Связаться #"))
async def contact_manager_from_list(message: Message, state: FSMContext):
    """Обработчик кнопки связи с бригадиром из списка"""
    if not await check_inspector(message.from_user.id):
        return

    try:
        # Извлекаем ID места из текста кнопки
        place_id = message.text.split('#')[1].split(' -')[0]

        inspection_data = places_db.search.get(place_id)
        if not inspection_data or inspection_data.get('inspector') != str(message.from_user.id):
            await message.answer("❌ Проверка не найдена или не принадлежит вам.")
            return

        info = inspection_service.get_inspection_info(place_id)

        await message.answer(
            f"📞 Связь с бригадиром\n\n"
            f"🏢 Место: {place_id}\n"
            f"📍 Адрес: {info['address']}\n"
            f"👷 Бригадир: {info['supervisor_name']}\n"
            f"📞 Телефон: {info['supervisor_phone']}\n"
            f"🆔 ID бригадира: {info['supervisor_id']}\n"
            f"📅 Текущее время: {info['date']}\n\n"
            f"Введите предложенное время для проверки:\n"
            f"<i>Пример: 25.12.2023 14:30</i>",
            parse_mode="HTML",
            reply_markup=get_back_to_inspections_keyboard()
        )

        await state.update_data(place_id=place_id, supervisor_id=info['supervisor_id'])
        await state.set_state(InspectorStates.waiting_for_proposed_time)

    except (ValueError, IndexError):
        await message.answer("❌ Ошибка при обработке запроса.")


@router.message(F.text == "📊 Статус заполнения")
async def show_checklist_status(message: Message):
    """Показывает статус заполнения текущего чек-листа"""
    # Здесь можно добавить логику для показа детального статуса
    await message.answer(
        "📊 Для просмотра статуса заполнения выберите раздел чек-листа",
        reply_markup=get_inspector_main_keyboard()
    )
@router.message(InspectorStates.waiting_for_proposed_time, F.text)
async def process_proposed_time(message: Message, state: FSMContext, bot: Bot):
    """Обработчик ввода предложенного времени"""
    if message.text == "🔙 К списку проверок":
        await message.answer("Возвращаемся к списку проверок...")
        await state.clear()
        return

    proposed_time = message.text.strip()
    user_data = await state.get_data()
    place_id = user_data['place_id']
    supervisor_id = user_data['supervisor_id']

    # Обновляем дату проверки
    success = places_db.update_inspection_date(place_id, proposed_time)

    if success:
        # Отправляем уведомление бригадиру через сервис
        await inspection_service.send_proposal_to_supervisor(
            bot, place_id, supervisor_id, message.from_user.first_name, proposed_time
        )

        await message.answer(
            f"✅ Предложение отправлено бригадиру!\n\n"
            f"⏰ Ваше предложение: {proposed_time}\n"
            f"Ожидайте подтверждения.",
            reply_markup=get_inspector_main_keyboard()
        )
    else:
        await message.answer(
            "❌ Ошибка при отправке предложения.",
            reply_markup=get_inspector_main_keyboard()
        )

    await state.clear()


# Обработчики навигации
@router.message(F.text == "🔙 Назад")
async def back_to_inspector_panel(message: Message):
    if not await check_inspector(message.from_user.id):
        return

    await message.answer(
        "👁️ Панель проверяющего\n\n"
        "Выберите действие:",
        reply_markup=get_inspector_main_keyboard()
    )


@router.message(F.text == "🔙 К списку проверок")
async def back_to_inspections_list(message: Message):
    if not await check_inspector(message.from_user.id):
        return

    await my_inspections(message)


# Отладочные команды
@router.message(Command("debug_places"))
async def debug_places(message: Message):
    """Отладочная информация о местах и проверках"""
    if not await check_inspector(message.from_user.id):
        return

    all_places = places_db.get_all_places()
    all_inspections = places_db.get_all_inspections()

    debug_info = "🧪 ДЕБАГ ИНФОРМАЦИЯ:\n\n"
    debug_info += f"📍 Всего мест: {len(all_places)}\n"
    debug_info += f"📋 Всего проверок: {len(all_inspections)}\n\n"

    for place_id, supervisor_id in all_places.items():
        inspection = all_inspections.get(place_id, {})
        debug_info += (
            f"🏢 {place_id}\n"
            f"👷 Бригадир: {supervisor_id}\n"
            f"👁️ Проверяющий: {inspection.get('inspector', 'Нет')}\n"
            f"📅 Время: {inspection.get('date', 'Нет')}\n"
            f"────────────────────\n"
        )

    await message.answer(debug_info)