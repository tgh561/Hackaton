# models/admin.py
from .user import User
from database import db, UserRole
from messages.message_db import message_db
from messages.message import MessageStatus
import json

class Admin(User):
    def __init__(self, telegram_id: int):
        super().__init__(telegram_id)
        self.permissions = self._load_permissions()
    
    def _load_permissions(self):
        """Загружает права админа из базы"""
        user_data = db.get_user(self.telegram_id)
        return user_data.get('permissions', [])
    
    def has_permission(self, permission: str) -> bool:
        """Проверяет наличие права у админа"""
        return permission in self.permissions
    
    # Методы управления пользователями
    def get_all_users(self) -> dict:
        """Получает всех пользователей системы"""
        return db.get_all_users()
    
    def get_user_by_telegram_id(self, telegram_id: int) -> dict:
        """Получает пользователя по Telegram ID"""
        return db.get_user(telegram_id)
    
    def create_user(self, telegram_id: int, username: str, first_name: str,
                   last_name: str, role: UserRole, phone: str = None,
                   department: str = None, position: str = None) -> bool:
        """Создает нового пользователя"""
        if not self.has_permission('user_management'):
            return False
        
        try:
            db.create_user(
                telegram_id=telegram_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
                role=role,
                phone=phone,
                department=department,
                position=position
            )
            return True
        except Exception as e:
            print(f"Error creating user: {e}")
            return False
    
    def update_user_role(self, target_telegram_id: int, new_role: UserRole) -> bool:
        """Изменяет роль пользователя"""
        if not self.has_permission('role_management'):
            return False
        
        return db.update_user_role(target_telegram_id, new_role)
    
    def update_user_info(self, target_telegram_id: int, **kwargs) -> bool:
        """Обновляет информацию о пользователе"""
        if not self.has_permission('user_management'):
            return False
        
        return db.update_user(target_telegram_id, **kwargs)
    
    def deactivate_user(self, target_telegram_id: int) -> bool:
        """Деактивирует пользователя"""
        if not self.has_permission('user_management'):
            return False
        
        return db.update_user(target_telegram_id, is_active=False)
    
    def activate_user(self, target_telegram_id: int) -> bool:
        """Активирует пользователя"""
        if not self.has_permission('user_management'):
            return False
        
        return db.update_user(target_telegram_id, is_active=True)
    
    # Методы для работы с сообщениями
    def get_all_messages(self, limit: int = 100) -> list:
        """Получает все сообщения системы (с ограничением)"""
        if not self.has_permission('view_all_reports'):
            return []
        
        all_messages = list(message_db.messages.values())
        return sorted(all_messages, key=lambda x: x.timestamp, reverse=True)[:limit]
    
    def get_messages_by_status(self, status: MessageStatus) -> list:
        """Получает сообщения по статусу"""
        if not self.has_permission('view_all_reports'):
            return []
        
        return [msg for msg in message_db.messages.values() if msg.status == status]
    
    def broadcast_message(self, content: list, importance: int = 1) -> list:
        """Отправляет сообщение всем пользователям"""
        if not self.has_permission('broadcast_messages'):
            return []
        
        all_users = db.get_all_users()
        sent_messages = []
        
        for user_id_str, user_data in all_users.items():
            if user_data.get('is_active', True):
                message = self.send_message(
                    content=content,
                    recipient_telegram_id=user_data['telegram_id'],
                    importance=importance
                )
                sent_messages.append(message)
        
        return sent_messages
    
    def get_system_stats(self) -> dict:
        """Получает статистику системы"""
        all_users = db.get_all_users()
        all_messages = list(message_db.messages.values())
        
        # Статистика по ролям
        roles_count = {}
        for user_data in all_users.values():
            role = user_data.get('role', 'unknown')
            roles_count[role] = roles_count.get(role, 0) + 1
        
        # Статистика по сообщениям
        messages_by_status = {}
        for status in MessageStatus:
            messages_by_status[status.value] = len([
                msg for msg in all_messages if msg.status == status
            ])
        
        # Активность
        active_users = len([u for u in all_users.values() if u.get('is_active', True)])
        
        return {
            'total_users': len(all_users),
            'active_users': active_users,
            'users_by_role': roles_count,
            'total_messages': len(all_messages),
            'messages_by_status': messages_by_status,
            'system_health': 'optimal' if active_users > 0 else 'warning'
        }
    
    def export_users_data(self, file_path: str = "users_export.json") -> bool:
        """Экспортирует данные пользователей в файл"""
        if not self.has_permission('user_management'):
            return False
        
        try:
            users_data = db.get_all_users()
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(users_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Error exporting users data: {e}")
            return False
    
    def find_users_by_criteria(self, **criteria) -> list:
        """Находит пользователей по критериям"""
        all_users = db.get_all_users()
        matching_users = []
        
        for user_id, user_data in all_users.items():
            match = True
            for key, value in criteria.items():
                if user_data.get(key) != value:
                    match = False
                    break
            if match:
                matching_users.append(user_data)
        
        return matching_users