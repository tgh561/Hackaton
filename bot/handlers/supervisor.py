from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from database.simple_db import db, UserRole
from database.places_db import places_db
from utils.inspection_service import inspection_service
from utils.states import SupervisorStates


router = Router()


# Проверка прав бригадира
async def check_supervisor(user_id: int) -> bool:
    user = db.get_user(user_id)
    if not user:
        return False
    return user['role'] == UserRole.MANAGER.value


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