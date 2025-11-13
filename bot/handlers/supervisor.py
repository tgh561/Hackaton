from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext

from database.simple_db import db, UserRole
from database.places_db import places_db
from database.checklists_db import checklists_db
from utils.inspection_service import inspection_service
from utils.states import SupervisorStates
from utils.checklists import checklist_manager

router = Router()


# Проверка прав бригадира
async def check_supervisor(user_id: int) -> bool:
    user = db.get_user(user_id)
    if not user:
        return False
    return user['role'] == UserRole.MANAGER.value


# Клавиатура для бригадира
def get_supervisor_main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📋 Мои объекты"), KeyboardButton(text="👁️ Просмотр чек-листов")],
            [KeyboardButton(text="📊 Статистика"), KeyboardButton(text="ℹ️ Помощь")],
            [KeyboardButton(text="🔙 В главное меню")]
        ],
        resize_keyboard=True
    )


def get_checklists_keyboard(places_data):
    """Клавиатура с чек-листами объектов бригадира"""
    keyboard = []

    for place_id in places_data:
        button_text = f"📋 Чек-лист #{place_id}"
        keyboard.append([KeyboardButton(text=button_text)])

    keyboard.append([KeyboardButton(text="🔙 Назад")])

    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def get_checklist_view_keyboard(place_id):
    """Клавиатура для просмотра конкретного чек-листа"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔄 Обновить"), KeyboardButton(text="📊 Детальная статистика")],
            [KeyboardButton(text="🔙 К списку объектов")]
        ],
        resize_keyboard=True
    )


@router.message(F.text == "👁️ Просмотр чек-листов")
async def view_checklists(message: Message):
    """Показывает чек-листы объектов бригадира"""
    if not await check_supervisor(message.from_user.id):
        await message.answer("❌ У вас нет прав доступа к этой функции.")
        return

    # Получаем объекты бригадира из places.json
    supervisor_places = []
    user_id_str = str(message.from_user.id)

    for place_id, supervisor_id in places_db.places.items():
        if supervisor_id == user_id_str:
            supervisor_places.append(place_id)

    if not supervisor_places:
        await message.answer(
            "📭 У вас нет закрепленных объектов.",
            reply_markup=get_supervisor_main_keyboard()
        )
        return

    # Формируем список объектов с информацией о чек-листах
    places_list = "👁️ Ваши объекты для просмотра чек-листов:\n\n"

    for place_id in supervisor_places:
        checklist = checklists_db.get_checklist(place_id)

        places_list += f"🔹 Объект: {place_id}\n"

        # Получаем информацию о проверке если есть
        inspection_data = places_db.search.get(place_id, {})
        if inspection_data:
            places_list += f"📍 Адрес: {inspection_data.get('address', 'Не указан')}\n"
            places_list += f"👤 Проверяющий: {inspection_data.get('inspector', 'Не назначен')}\n"

        if checklist:
            progress = checklists_db.get_checklist_progress(place_id)
            status = "✅ Завершен" if checklist.get('status') == 'completed' else "🟡 В процессе"
            places_list += f"📊 Чек-лист: {status}\n"
            places_list += f"   Прогресс: {progress['percentage']}% ({progress['completed']}/{progress['total']})\n"
        else:
            places_list += f"📊 Чек-лист: ⚪ Не начат\n"

        places_list += f"────────────────────\n"

    await message.answer(
        places_list + "\nВыберите объект для просмотра чек-листа:",
        reply_markup=get_checklists_keyboard(supervisor_places)
    )


@router.message(F.text.startswith("📋 Чек-лист #"))
async def show_checklist_for_supervisor(message: Message):
    """Показывает чек-лист конкретного места для бригадира"""
    if not await check_supervisor(message.from_user.id):
        return

    try:
        place_id = message.text.split('#')[1]

        # Проверяем, что объект принадлежит бригадиру
        supervisor_id = places_db.places.get(place_id)
        if not supervisor_id or supervisor_id != str(message.from_user.id):
            await message.answer("❌ У вас нет доступа к этому объекту.")
            return

        # Получаем чек-лист
        checklist = checklists_db.get_checklist(place_id)

        if not checklist:
            await message.answer(
                f"📭 Чек-лист для объекта {place_id} еще не создан.\n"
                f"Проверяющий еще не начал заполнение.",
                reply_markup=get_checklists_keyboard([place_id])
            )
            return

        # Форматируем чек-лист для просмотра (как у инспектора)
        checklist_message = _format_checklist_for_supervisor(place_id, checklist)

        # Отправляем чек-лист
        if len(checklist_message) > 4000:
            parts = [checklist_message[i:i + 4000] for i in range(0, len(checklist_message), 4000)]
            for part in parts:
                await message.answer(part)
        else:
            await message.answer(checklist_message)

        # Показываем кнопки действий
        await message.answer(
            "Выберите действие:",
            reply_markup=get_checklist_view_keyboard(place_id)
        )

    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")


def _format_checklist_for_supervisor(place_id: str, checklist: dict) -> str:
    """Форматирует чек-лист для просмотра бригадиром"""
    checklist_data = checklist['checklist_data']

    message_text = f"📋 Чек-лист объекта {place_id}\n"

    # Добавляем информацию о проверке если есть
    inspection_data = places_db.search.get(place_id, {})
    if inspection_data:
        message_text += f"📍 Адрес: {inspection_data.get('address', 'Не указан')}\n"
        message_text += f"👤 Проверяющий: {checklist['inspector_name']}\n"
        message_text += f"📅 Дата проверки: {inspection_data.get('date', 'Не назначена')}\n"

    message_text += f"📅 Создан: {checklist['created_at'][:10]}\n"
    message_text += f"📊 Статус: {'✅ Завершен' if checklist.get('status') == 'completed' else '🟡 В процессе'}\n\n"

    # Добавляем разделы и критерии
    for section_key, section_data in checklist_data['sections'].items():
        message_text += f"🔹 РАЗДЕЛ {section_key}:\n"
        message_text += f"{section_data['description']}\n\n"

        for criterion in section_data['criteria']:
            status = "⚪ Не проверен"
            if criterion.get('complies') is True:
                status = "✅ Соответствует"
            elif criterion.get('does_not_comply') is True:
                status = "❌ Не соответствует"

            message_text += f"{criterion['number']}. {criterion['description']}\n"
            message_text += f"   Статус: {status}\n"

            if criterion.get('comment'):
                message_text += f"   💬 Комментарий: {criterion['comment']}\n"

            if criterion.get('does_not_comply') is True:
                message_text += f"   🚨 Требует внимания!\n"

            message_text += "\n"

        message_text += "────────────────────\n\n"

    # Добавляем статистику
    progress = checklists_db.get_checklist_progress(place_id)
    non_compliant = _count_non_compliant_criteria(checklist_data)

    message_text += f"📈 СТАТИСТИКА:\n"
    message_text += f"✅ Соответствует: {progress['completed'] - non_compliant}\n"
    message_text += f"❌ Не соответствует: {non_compliant}\n"
    message_text += f"⚪ Не проверено: {progress['total'] - progress['completed']}\n"
    message_text += f"📊 Общий прогресс: {progress['percentage']}%"

    return message_text


def _count_non_compliant_criteria(checklist_data: dict) -> int:
    """Подсчитывает количество несоответствующих критериев"""
    non_compliant = 0
    for section_data in checklist_data['sections'].values():
        for criterion in section_data['criteria']:
            if criterion.get('does_not_comply') is True:
                non_compliant += 1
    return non_compliant


@router.message(F.text == "🔄 Обновить")
async def refresh_checklist(message: Message):
    """Обновляет просмотр чек-листа"""
    # Находим последний просматриваемый объект из контекста
    # В реальном приложении можно хранить историю в состоянии
    # Пока просто возвращаем к списку чек-листов
    await view_checklists(message)


@router.message(F.text == "📊 Детальная статистика")
async def detailed_statistics(message: Message):
    """Показывает детальную статистику по чек-листам"""
    if not await check_supervisor(message.from_user.id):
        return

    # Получаем объекты бригадира из places.json
    supervisor_places = []
    user_id_str = str(message.from_user.id)

    for place_id, supervisor_id in places_db.places.items():
        if supervisor_id == user_id_str:
            supervisor_places.append(place_id)

    if not supervisor_places:
        await message.answer("❌ У вас нет закрепленных объектов.")
        return

    stats_text = "📊 ДЕТАЛЬНАЯ СТАТИСТИКА ЧЕК-ЛИСТОВ\n\n"

    total_objects = len(supervisor_places)
    completed_checklists = 0
    in_progress_checklists = 0
    total_non_compliant = 0
    total_criteria = 0

    for place_id in supervisor_places:
        checklist = checklists_db.get_checklist(place_id)

        stats_text += f"🔹 {place_id}:\n"

        if checklist:
            progress = checklists_db.get_checklist_progress(place_id)
            non_compliant = _count_non_compliant_criteria(checklist['checklist_data'])

            if checklist.get('status') == 'completed':
                completed_checklists += 1
                status_emoji = "✅"
            else:
                in_progress_checklists += 1
                status_emoji = "🟡"

            stats_text += f"   {status_emoji} Прогресс: {progress['percentage']}%\n"
            stats_text += f"   ❌ Несоответствий: {non_compliant}\n"

            total_non_compliant += non_compliant
            total_criteria += progress['total']
        else:
            stats_text += f"   ⚪ Чек-лист не начат\n"

        stats_text += "\n"

    # Общая статистика
    stats_text += f"📈 ОБЩАЯ СТАТИСТИКА:\n"
    stats_text += f"🏢 Всего объектов: {total_objects}\n"
    stats_text += f"✅ Завершено чек-листов: {completed_checklists}\n"
    stats_text += f"🟡 В процессе: {in_progress_checklists}\n"
    stats_text += f"❌ Всего несоответствий: {total_non_compliant}\n"

    if total_criteria > 0:
        compliance_rate = ((total_criteria - total_non_compliant) / total_criteria * 100)
        stats_text += f"📊 Общий процент соответствия: {compliance_rate:.1f}%"

    await message.answer(stats_text)


@router.message(F.text == "🔙 К списку объектов")
async def back_to_checklists_list(message: Message):
    """Возврат к списку чек-листов"""
    await view_checklists(message)


@router.message(F.text == "🔙 Назад")
async def back_to_supervisor_panel(message: Message):
    """Возврат в панель бригадира"""
    if not await check_supervisor(message.from_user.id):
        return

    await message.answer(
        "👷 Панель бригадира\n\n"
        "Выберите действие:",
        reply_markup=get_supervisor_main_keyboard()
    )


# Обработчики для работы с инспекциями (оставляем без изменений)
@router.callback_query(F.data.startswith("accept_inspection_"))
async def accept_inspection(callback: CallbackQuery, bot: Bot):
    """Бригадир подтверждает время проверки"""
    raw_place_id = callback.data.split("_")[-1]

    # Ищем проверку в базе
    possible_place_ids = [
        raw_place_id,
        f"place_{raw_place_id}",
        f"#{raw_place_id}",
        raw_place_id.replace('place_', '')
    ]

    inspection_data = None
    actual_place_id = None

    for place_id in possible_place_ids:
        if place_id in places_db.search:
            inspection_data = places_db.search[place_id]
            actual_place_id = place_id
            break

    if not inspection_data:
        await callback.answer("❌ Проверка не найдена.")
        return

    inspector_id = inspection_data.get('inspector')
    proposed_time = inspection_data.get('date', 'Не указано')

    if not inspector_id or inspector_id == 'Не назначен':
        await callback.answer("❌ Проверяющий не назначен.")
        return

    # Просто отправляем подтверждение проверяющему
    success = await inspection_service.send_confirmation_to_inspector(
        bot, actual_place_id, inspector_id, proposed_time
    )

    if success:
        await callback.message.edit_text(
            f"✅ Вы подтвердили проверку!\n\n"
            f"🏢 Место: {actual_place_id}\n"
            f"⏰ Время: {proposed_time}\n\n"
            f"Проверяющий уведомлен."
        )
    else:
        await callback.answer("❌ Ошибка при отправке подтверждения.")


@router.callback_query(F.data.startswith("decline_inspection_"))
async def decline_inspection(callback: CallbackQuery, state: FSMContext):
    """Бригадир отклоняет время проверки"""
    raw_place_id = callback.data.split("_")[-1]

    # Ищем проверку в базе
    possible_place_ids = [
        raw_place_id,
        f"place_{raw_place_id}",
        f"#{raw_place_id}",
        raw_place_id.replace('place_', '')
    ]

    actual_place_id = None
    for place_id in possible_place_ids:
        if place_id in places_db.search:
            actual_place_id = place_id
            break

    if not actual_place_id:
        await callback.answer("❌ Проверка не найдена.")
        return

    inspection_data = places_db.search[actual_place_id]
    inspector_id = inspection_data.get('inspector')

    if not inspector_id or inspector_id == 'Не назначен':
        await callback.answer("❌ Проверяющий не назначен.")
        return

    await state.update_data(
        place_id=actual_place_id,
        inspector_id=inspector_id
    )

    await callback.message.answer(
        f"❌ Отклонение проверки {actual_place_id}\n\n"
        f"Укажите причину отказа:\n"
        f"<i>Пример: В это время проводятся работы, предлагаю другое время</i>",
        parse_mode="HTML"
    )

    await state.set_state(SupervisorStates.waiting_for_rejection_reason)
    await callback.answer()


@router.message(SupervisorStates.waiting_for_rejection_reason, F.text)
async def process_rejection_reason(message: Message, state: FSMContext, bot: Bot):
    """Обработчик ввода причины отказа"""
    user_data = await state.get_data()
    place_id = user_data['place_id']
    inspector_id = user_data['inspector_id']
    rejection_reason = message.text

    # Отправляем уведомление об отказе проверяющему
    success = await inspection_service.send_rejection_to_inspector(
        bot, place_id, inspector_id, rejection_reason
    )

    if success:
        await message.answer("✅ Отказ отправлен проверяющему.")
    else:
        await message.answer("❌ Ошибка при отправке отказа.")

    await state.clear()