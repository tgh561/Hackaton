# models/worker.py
from .user import User
from messages.message import MessageStatus

class Worker(User):
    def __init__(self, telegram_id: int):
        super().__init__(telegram_id)
    
    def report_problem(self, problem_type: str, description: list, supervisor_telegram_id: int):
        """Сообщает о проблеме"""
        content = [
            f"🚨 ПРОБЛЕМА: {problem_type}",
            *description,
            f"Работник: {self.get_full_name()}",
            f"Отдел: {self.department}"
        ]
        return self.send_message(content, supervisor_telegram_id, importance=3)
    
    def request_materials(self, materials: list, supervisor_telegram_id: int):
        """Запрашивает материалы"""
        content = [
            "📦 ЗАПРОС МАТЕРИАЛОВ",
            "Необходимые материалы:",
            *[f"- {material}" for material in materials],
            f"Запросил: {self.get_full_name()}"
        ]
        return self.send_message(content, supervisor_telegram_id, importance=2)