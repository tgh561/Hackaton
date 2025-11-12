# models/inspector.py
from .user import User
from messages.message import MessageStatus, Message

class Inspector(User):
    def __init__(self, telegram_id: int):
        super().__init__(telegram_id)
    
    def create_inspection_report(self, inspection_type: str, findings: list, 
                                recommendations: list, supervisor_telegram_id: int) -> Message:
        """Создает отчет о проверке"""
        content = [
            f"🔍 ОТЧЕТ О ПРОВЕРКЕ: {inspection_type}",
            f"Инспектор: {self.get_full_name()}",
            f"Отдел: {self.department}",
            "",
            "📋 НАЙДЕННЫЕ ЗАМЕЧАНИЯ:",
            *[f"• {finding}" for finding in findings],
            "",
            "💡 РЕКОМЕНДАЦИИ:",
            *[f"• {rec}" for rec in recommendations]
        ]
        
        importance = 4 if "критическ" in inspection_type.lower() else 3
        return self.send_message(content, supervisor_telegram_id, importance)
    
    def get_inspection_stats(self) -> dict:
        """Статистика по проведенным проверкам"""
        sent_messages = self.get_sent_messages()
        inspection_reports = [msg for msg in sent_messages 
                            if "ОТЧЕТ О ПРОВЕРКЕ" in msg.content[0]]
        
        return {
            'total_inspections': len(inspection_reports),
            'reports_pending': len([msg for msg in inspection_reports 
                                  if msg.status in [MessageStatus.UNREAD, MessageStatus.READ]]),
            'reports_in_progress': len([msg for msg in inspection_reports 
                                      if msg.status == MessageStatus.IN_PROGRESS]),
            'reports_resolved': len([msg for msg in inspection_reports 
                                   if msg.status == MessageStatus.FIXED])
        }