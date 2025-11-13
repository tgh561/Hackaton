import json
import os
from datetime import datetime
from enum import Enum


class UserRole(Enum):
    WORKER = "worker"
    MANAGER = "manager"
    INSPECTOR = "inspector"
    ADMIN = "admin"


class InspectionStatus(Enum):
    PENDING = "pending"  # Ожидает подтверждения
    SCHEDULED = "scheduled"  # Подтверждена
    REJECTED = "rejected"  # Отклонена
    COMPLETED = "completed"  # Завершена


class SimpleDB:
    def __init__(self, db_file: str = "users.json"):
        self.db_file = db_file
        self.users = self._load_data()
        self._create_default_users()
        self._create_default_inspections()

    def _load_data(self):
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def _save_data(self):
        with open(self.db_file, 'w', encoding='utf-8') as f:
            json.dump(self.users, f, ensure_ascii=False, indent=2)

    def _create_default_users(self):
        # Предзаполненные пользователи
        default_users = {
            "123456789": {
                'telegram_id': 123456789,
                'username': 'admin_user',
                'first_name': 'Иван',
                'last_name': 'Петров',
                'phone': '+79991234567',
                'role': UserRole.ADMIN.value,
                'registered_at': datetime.now().isoformat(),
                'is_active': True
            },
            "987654321": {
                'telegram_id': 987654321,
                'username': 'manager_user',
                'first_name': 'Мария',
                'last_name': 'Сидорова',
                'phone': '+79997654321',
                'role': UserRole.MANAGER.value,
                'registered_at': datetime.now().isoformat(),
                'is_active': True
            },
            "555555555": {
                'telegram_id': 555555555,
                'username': 'inspector_user',
                'first_name': 'Алексей',
                'last_name': 'Козлов',
                'phone': '+79995555555',
                'role': UserRole.INSPECTOR.value,
                'registered_at': datetime.now().isoformat(),
                'is_active': True
            },
            "111111111": {
                'telegram_id': 111111111,
                'username': 'worker1',
                'first_name': 'Сергей',
                'last_name': 'Иванов',
                'phone': '+79991111111',
                'role': UserRole.WORKER.value,
                'registered_at': datetime.now().isoformat(),
                'is_active': True
            },
            "222222222": {
                'telegram_id': 222222222,
                'username': 'worker2',
                'first_name': 'Ольга',
                'last_name': 'Смирнова',
                'phone': '+79992222222',
                'role': UserRole.WORKER.value,
                'registered_at': datetime.now().isoformat(),
                'is_active': True
            }
        }

        # Добавляем только тех пользователей, которых еще нет в базе
        for user_id, user_data in default_users.items():
            if user_id not in self.users:
                self.users[user_id] = user_data

        self._save_data()

    def _create_default_inspections(self):
        """Создает тестовые проверки"""
        if 'inspections' not in self.users:
            self.users['inspections'] = {}

        default_inspections = {
            "1": {
                'id': 1,
                'location': 'Строительная площадка №1',
                'manager_id': 987654321,  # ID бригадира
                'inspector_id': 555555555,  # ID проверяющего
                'scheduled_time': None,
                'status': InspectionStatus.PENDING.value,
                'created_at': datetime.now().isoformat(),
                'proposed_time': None,
                'rejection_reason': None,
                'alternative_time': None
            },
            "2": {
                'id': 2,
                'location': 'Офисное здание №2',
                'manager_id': 987654321,
                'inspector_id': None,  # Свободная проверка
                'scheduled_time': None,
                'status': InspectionStatus.PENDING.value,
                'created_at': datetime.now().isoformat(),
                'proposed_time': None,
                'rejection_reason': None,
                'alternative_time': None
            }
        }

        for inspection_id, inspection_data in default_inspections.items():
            if inspection_id not in self.users['inspections']:
                self.users['inspections'][inspection_id] = inspection_data

        self._save_data()

    def get_user(self, telegram_id: int):
        return self.users.get(str(telegram_id))

    def get_all_users(self):
        """Возвращает всех пользователей"""
        return {k: v for k, v in self.users.items() if k.isdigit()}

    def get_managers(self):
        """Возвращает всех руководителей"""
        return {k: v for k, v in self.users.items() if k.isdigit() and v.get('role') == UserRole.MANAGER.value}


    def create_user(self, telegram_id: int, username: str, first_name: str,
                    last_name: str, role: UserRole, phone: str = None):
        user_data = {
            'telegram_id': telegram_id,
            'username': username,
            'first_name': first_name,
            'last_name': last_name,
            'phone': phone,
            'role': role.value,
            'registered_at': datetime.now().isoformat(),
            'is_active': True
        }
        self.users[str(telegram_id)] = user_data
        self._save_data()
        return user_data

    def update_user_role(self, telegram_id: int, new_role: UserRole):
        user = self.get_user(telegram_id)
        if user:
            user['role'] = new_role.value
            self._save_data()
            return True
        return False


# Глобальный экземпляр БД
db = SimpleDB()