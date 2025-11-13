# models/supervisor.py
from .user import User
from messages.message import MessageStatus
from database import db
from ...entities.messages.message_db import message_db
class Supervisor(User):
    def __init__(self, telegram_id: int):
        super().__init__(telegram_id)
    
    def get_managed_workers(self) -> list:
        """Получает список работников в подчинении"""
        all_users = db.get_all_users()
        workers = []
        for user_data in all_users.values():
            if (user_data.get('role') == 'worker' and 
                user_data.get('department') == self.department):
                workers.append(user_data['telegram_id'])
        return workers
    
    def broadcast_to_department(self, content: list, importance: int = 1) -> list:
        """Отправляет сообщение всему отделу"""
        workers = self.get_managed_workers()
        sent_messages = []
        for worker_id in workers:
            message = self.send_message(content, worker_id, importance)
            sent_messages.append(message)
        return sent_messages
    
    def get_department_stats(self) -> dict:
        """Статистика по отделу"""
        workers = self.get_managed_workers()
        messages = message_db.get_user_messages(self.telegram_id, "inbox")
        
        status_counts = {}
        for status in MessageStatus:
            status_counts[status.value] = len([
                msg for msg in messages if msg.status == status
            ])
        
        return {
            'workers_count': len(workers),
            'active_workers': len([w for w in workers if db.get_user(w).get('is_active', True)]),
            'messages_by_status': status_counts,
            'unread_messages': len(self.get_unread_messages())
        }