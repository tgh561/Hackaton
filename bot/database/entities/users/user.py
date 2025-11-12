# models/user.py
from database import db
from messages.message_db import message_db
from messages.message import Message, MessageStatus
from enum import Enum

class UserRole(Enum):
    WORKER = "worker"
    MANAGER = "manager"
    INSPECTOR = "inspector"
    ADMIN = "admin"

class User:
    def __init__(self, telegram_id: int):
        self.telegram_id = telegram_id
        self._load_from_db()
    
    def _load_from_db(self):
        user_data = db.get_user(self.telegram_id)
        if user_data:
            self.username = user_data.get('username', '')
            self.first_name = user_data.get('first_name', '')
            self.last_name = user_data.get('last_name', '')
            self.phone = user_data.get('phone', '')
            self.role = UserRole(user_data.get('role', UserRole.WORKER.value))
            self.department = user_data.get('department', '')
            self.position = user_data.get('position', '')
            self.is_active = user_data.get('is_active', True)
        else:
            raise ValueError(f"User with telegram_id {self.telegram_id} not found")
    
    def get_full_name(self) -> str:
        names = [self.first_name or '', self.last_name or '']
        return ' '.join(filter(None, names)).strip() or self.username
    
    def get_info(self) -> str:
        """Возвращает информацию о пользователе для отображения в боте"""
        return (f"👤 {self.get_full_name()}\n"
                f"🏢 {self.position or 'Должность не указана'}\n"
                f"📞 {self.phone or 'Телефон не указан'}\n"
                f"🎯 Роль: {self.role.value}")
    
    def send_message(self, content: list, recipient_telegram_id: int, importance: int = 1) -> Message:
        message = Message(
            content=content,
            sender_telegram_id=self.telegram_id,
            recipient_telegram_id=recipient_telegram_id,
            importance=importance
        )
        message_db.save_message(message)
        return message
    
    def get_received_messages(self, status: MessageStatus = None) -> list:
        messages = message_db.get_user_messages(self.telegram_id, "inbox")
        if status:
            messages = [msg for msg in messages if msg.status == status]
        return messages
    
    def get_sent_messages(self) -> list:
        return message_db.get_user_messages(self.telegram_id, "sent")
    
    def get_unread_messages(self) -> list:
        return message_db.get_messages_by_status(self.telegram_id, MessageStatus.UNREAD)
    
    def mark_message_as_read(self, message_id: str):
        message_db.update_message_status(message_id, MessageStatus.READ)