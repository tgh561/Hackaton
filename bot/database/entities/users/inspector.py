# models/inspector.py
from .user import User
from messages.message import MessageStatus, Message
from ....я_ебу_че_с_этими_файлами_делать.inspectors_status_db import inspector_status_db

class Inspector(User):
    def __init__(self, telegram_id: int):
        super().__init__(telegram_id)
        self._status_info = inspector_status_db.get_inspector_status(telegram_id)
    
    @property
    def is_active(self) -> bool:
        """Проверяет, активен ли инспектор"""
        return inspector_status_db.is_inspector_active(self.telegram_id)
    
    @property
    def status(self) -> dict:
        """Возвращает полную информацию о статусе"""
        return self._status_info
    
    def get_status_display(self) -> str:
        """Возвращает текстовое представление статуса"""
        if self.is_active:
            status_text = "🟢 Активен"
        else:
            status_text = "🔴 Неактивен"
        
        if self._status_info.get('reason'):
            status_text += f"\nПричина: {self._status_info['reason']}"
        
        return status_text
    
    def can_send_reports(self) -> bool:
        """Может ли инспектор отправлять отчеты"""
        return self.is_active
    
    def create_inspection_report(self, inspection_type: str, findings: list, 
                                recommendations: list, supervisor_telegram_id: int) -> Message:
        """Создает отчет о проверке с проверкой статуса"""
        if not self.can_send_reports():
            raise PermissionError(
                f"Инспектор не может отправлять отчеты. Текущий статус: {'активен' if self.is_active else 'неактивен'}"
            )
        
        content = [
            f"🔍 ОТЧЕТ О ПРОВЕРКЕ: {inspection_type}",
            f"Инспектор: {self.get_full_name()}",
            f"Отдел: {self.department}",
            f"Статус: {'🟢 Активен' if self.is_active else '🔴 Неактивен'}",
            "",
            "📋 НАЙДЕННЫЕ ЗАМЕЧАНИЯ:",
            *[f"• {finding}" for finding in findings],
            "",
            "💡 РЕКОМЕНДАЦИИ:",
            *[f"• {rec}" for rec in recommendations]
        ]
        
        importance = 4 if "критическ" in inspection_type.lower() else 3
        return self.send_message(content, supervisor_telegram_id, importance)
    
    def send_urgent_report(self, emergency_type: str, description: list, 
                          location: str, supervisor_telegram_id: int) -> Message:
        """Отправляет срочный отчет (доступен даже неактивным инспекторам)"""
        content = [
            f"🚨 СРОЧНЫЙ ОТЧЕТ: {emergency_type}",
            f"Инспектор: {self.get_full_name()}",
            f"Местоположение: {location}",
            f"Статус: {'🟢 Активен' if self.is_active else '🔴 Неактивен'}",
            "",
            "🚨 СИГНАЛИЗАЦИЯ:",
            *description
        ]
        
        return self.send_message(content, supervisor_telegram_id, importance=5)
    
    def update_status_info(self):
        """Обновляет информацию о статусе из базы данных"""
        self._status_info = inspector_status_db.get_inspector_status(self.telegram_id)
    
    def get_inspection_stats(self) -> dict:
        """Статистика по проведенным проверкам (только для активных инспекторов)"""
        if not self.is_active:
            return {
                'error': 'Инспектор неактивен',
                'status': self._status_info
            }
        
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
                                   if msg.status == MessageStatus.FIXED]),
            'inspector_status': self._status_info
        }