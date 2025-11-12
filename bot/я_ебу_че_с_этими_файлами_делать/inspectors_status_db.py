# inspectors_status_db.py
import json
import os
from datetime import datetime

class InspectorStatusDB:
    def __init__(self, db_file: str = "inspectors_status.json"):
        self.db_file = db_file
        self.status_data = self._load_data()
    
    def _load_data(self):
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading inspectors status: {e}")
                return {}
        return {}
    
    def _save_data(self):
        with open(self.db_file, 'w', encoding='utf-8') as f:
            json.dump(self.status_data, f, ensure_ascii=False, indent=2)
    
    def set_inspector_active(self, telegram_id: int, is_active: bool, reason: str = None):
        """Устанавливает статус инспектора"""
        status_record = {
            'is_active': is_active,
            'last_updated': datetime.now().isoformat(),
            'reason': reason
        }
        
        self.status_data[str(telegram_id)] = status_record
        self._save_data()
    
    def get_inspector_status(self, telegram_id: int) -> dict:
        """Получает статус инспектора"""
        return self.status_data.get(str(telegram_id), {
            'is_active': True,
            'last_updated': datetime.now().isoformat(),
            'reason': None
        })
    
    def is_inspector_active(self, telegram_id: int) -> bool:
        """Проверяет, активен ли инспектор"""
        status = self.get_inspector_status(telegram_id)
        return status['is_active']
    
    def get_all_inspectors_status(self) -> dict:
        """Получает статусы всех инспекторов"""
        return self.status_data
    
    def get_active_inspectors(self) -> list:
        """Получает активных инспекторов"""
        return [telegram_id for telegram_id, data in self.status_data.items() 
                if data.get('is_active', True)]
    
    def get_inactive_inspectors(self) -> list:
        """Получает неактивных инспекторов"""
        return [telegram_id for telegram_id, data in self.status_data.items() 
                if not data.get('is_active', True)]
    
    def delete_inspector_status(self, telegram_id: int):
        """Удаляет запись статуса инспектора"""
        if str(telegram_id) in self.status_data:
            del self.status_data[str(telegram_id)]
            self._save_data()
            return True
        return False

# Глобальный экземпляр
inspector_status_db = InspectorStatusDB()