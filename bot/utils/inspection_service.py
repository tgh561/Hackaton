from aiogram import Bot
from database.simple_db import db
from database.places_db import places_db
from keyboards.inspector_keyboards import get_confirm_inspection_keyboard


class InspectionService:
    @staticmethod
    def get_place_address(place_id: str) -> str:
        """Возвращает читаемое название места"""
        addresses = {
            "place_1": "Строительная площадка 'Северный'",
            "place_2": "ЖК 'Солнечный берег', корпус 3",
            "place_3": "Торговый центр 'Метрополис'",
            "place_4": "Офисное здание 'Бизнес-парк'",
            "place_5": "Стадион 'Олимпийский'"
        }
        return addresses.get(place_id, place_id)

    @staticmethod
    async def send_proposal_to_supervisor(
            bot: Bot,
            place_id: str,
            supervisor_id: str,
            inspector_name: str,
            proposed_time: str
    ) -> bool:
        """Отправляет предложение о времени проверки бригадиру"""
        try:
            supervisor_user = db.get_user(int(supervisor_id))
            if not supervisor_user:
                return False

            message_text = (
                f"🕐 Новое предложение по проверке\n\n"
                f"🏢 Место: {place_id}\n"
                f"📍 Адрес: {InspectionService.get_place_address(place_id)}\n"
                f"👁️ Проверяющий: {inspector_name}\n"
                f"⏰ Предложенное время: {proposed_time}\n\n"
                f"Подтвердите время или отклоните с указанием причины:"
            )

            await bot.send_message(
                supervisor_user['telegram_id'],
                message_text,
                reply_markup=get_confirm_inspection_keyboard(place_id)
            )
            return True
        except Exception as e:
            print(f"Ошибка отправки сообщения бригадиру: {e}")
            return False

    @staticmethod
    async def send_confirmation_to_inspector(
            bot: Bot,
            place_id: str,
            inspector_id: str,
            scheduled_time: str
    ) -> bool:
        """Отправляет подтверждение проверки проверяющему"""
        try:
            inspector_user = db.get_user(int(inspector_id))
            if not inspector_user:
                return False

            await bot.send_message(
                inspector_user['telegram_id'],
                f"✅ Бригадир подтвердил проверку!\n\n"
                f"🏢 Место: {place_id}\n"
                f"📍 Адрес: {InspectionService.get_place_address(place_id)}\n"
                f"⏰ Подтвержденное время: {scheduled_time}\n\n"
                f"Проверка запланирована!"
            )
            return True
        except Exception as e:
            print(f"Ошибка отправки подтверждения проверяющему: {e}")
            return False

    @staticmethod
    async def send_rejection_to_inspector(
            bot: Bot,
            place_id: str,
            inspector_id: str,
            rejection_reason: str,
            alternative_time: str = None
    ) -> bool:
        """Отправляет уведомление об отказе проверяющему"""
        try:
            inspector_user = db.get_user(int(inspector_id))
            if not inspector_user:
                return False

            message = (
                f"❌ Бригадир отклонил предложенное время\n\n"
                f"🏢 Место: {place_id}\n"
                f"📍 Адрес: {InspectionService.get_place_address(place_id)}\n"
                f"📝 Причина: {rejection_reason}\n"
            )

            if alternative_time:
                message += f"🕐 Альтернативное время: {alternative_time}\n\n"
            else:
                message += "\n"

            message += "Предложите другое время через кнопку 'Связаться с бригадиром'"

            await bot.send_message(inspector_user['telegram_id'], message)
            return True
        except Exception as e:
            print(f"Ошибка отправки отказа проверяющему: {e}")
            return False


    @staticmethod
    def get_inspection_info(place_id: str) -> dict:
        """Возвращает полную информацию о проверке"""
        inspection_data = places_db.search.get(place_id, {})
        supervisor_id = places_db.get_supervisor_by_place(place_id)
        supervisor = db.get_user(int(supervisor_id)) if supervisor_id and supervisor_id.isdigit() else None

        return {
            'place_id': place_id,
            'address': InspectionService.get_place_address(place_id),
            'date': inspection_data.get('date', 'Не назначена'),
            'inspector_id': inspection_data.get('inspector'),
            'supervisor_id': supervisor_id,
            'supervisor_name': f"{supervisor['first_name']} {supervisor.get('last_name', '')}" if supervisor else "Неизвестно",
            'supervisor_phone': supervisor.get('phone', 'Не указан') if supervisor else 'Не указан'
        }


# Создаем экземпляр сервиса
inspection_service = InspectionService()