# messages/message_db.py
import json
import os
from .message import Message, MessageStatus

class MessageDB:
    def __init__(self, db_file: str = "messages.json"):
        self.db_file = db_file
        self.messages = self._load_data()
    
    def _load_data(self):
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return {msg_id: Message.from_dict(msg_data) for msg_id, msg_data in data.items()}
            except Exception as e:
                print(f"Error loading messages: {e}")
                return {}
        return {}
    
    def _save_data(self):
        """Сохраняет сообщения в JSON"""
        data = {msg_id: msg.to_dict() for msg_id, msg in self.messages.items()}
        with open(self.db_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def save_message(self, message: Message) -> str:
        """Сохраняет сообщение и возвращает его ID"""
        self.messages[message.id] = message
        self._save_data()
        return message.id
    
    def get_message(self, message_id: str) -> Message:
        """Получает сообщение по ID"""
        return self.messages.get(message_id)
    
    def get_user_messages(self, telegram_id: int, folder: str = "inbox") -> list:
        """Получает сообщения пользователя"""
        user_messages = []
        for message in self.messages.values():
            if folder == "inbox" and message.recipient_telegram_id == telegram_id:
                user_messages.append(message)
            elif folder == "sent" and message.sender_telegram_id == telegram_id:
                user_messages.append(message)
        return sorted(user_messages, key=lambda x: x.timestamp, reverse=True)
    
    def update_message_status(self, message_id: str, new_status: MessageStatus):
        """Обновляет статус сообщения"""
        message = self.messages.get(message_id)
        if message:
            message.change_status(new_status)
            self._save_data()
    
    def get_messages_by_status(self, telegram_id: int, status: MessageStatus) -> list:
        """Получает сообщения по статусу"""
        return [msg for msg in self.messages.values() 
                if msg.recipient_telegram_id == telegram_id and msg.status == status]

# Глобальный экземпляр базы сообщений
message_db = MessageDB()