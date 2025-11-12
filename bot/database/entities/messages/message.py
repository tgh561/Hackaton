# messages/message.py
import uuid
from datetime import datetime
from enum import Enum

class MessageStatus(Enum):
    UNREAD = "не прочитано"
    READ = "прочитано"
    IN_PROGRESS = "в работе"
    FIXED = "исправлено"
    REJECTED = "отклонено"

class Message:
    def __init__(self, content: list, sender_telegram_id: int, recipient_telegram_id: int, 
                 importance: int = 1, answer: str = "", status: MessageStatus = MessageStatus.UNREAD):
        self.id = str(uuid.uuid4())
        self.content = content
        self.sender_telegram_id = sender_telegram_id
        self.recipient_telegram_id = recipient_telegram_id
        self.importance = importance
        self.answer = answer
        self.status = status
        self.timestamp = datetime.now().isoformat()
        self.status_history = [{
            'status': status.value,
            'timestamp': datetime.now().isoformat()
        }]
    
    def to_dict(self):
        """Конвертирует сообщение в словарь для сохранения в JSON"""
        return {
            'id': self.id,
            'content': self.content,
            'sender_telegram_id': self.sender_telegram_id,
            'recipient_telegram_id': self.recipient_telegram_id,
            'importance': self.importance,
            'answer': self.answer,
            'status': self.status.value,
            'timestamp': self.timestamp,
            'status_history': self.status_history
        }
    
    @classmethod
    def from_dict(cls, data):
        """Создает объект Message из словаря"""
        message = cls(
            content=data['content'],
            sender_telegram_id=data['sender_telegram_id'],
            recipient_telegram_id=data['recipient_telegram_id'],
            importance=data.get('importance', 1),
            answer=data.get('answer', ''),
            status=MessageStatus(data['status'])
        )
        message.id = data['id']
        message.timestamp = data['timestamp']
        message.status_history = data.get('status_history', [])
        return message
    
    def change_status(self, new_status: MessageStatus):
        """Изменяет статус сообщения"""
        self.status = new_status
        self.status_history.append({
            'status': new_status.value,
            'timestamp': datetime.now().isoformat()
        })
    
    def get_preview(self, max_length: int = 50) -> str:
        """Превью сообщения"""
        full_content = "\n".join(str(item) for item in self.content)
        if len(full_content) > max_length:
            return full_content[:max_length] + "..."
        return full_content