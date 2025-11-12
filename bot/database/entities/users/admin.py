# models/admin.py (дополняем)
from ....я_ебу_че_с_этими_файлами_делать.inspectors_status_db import inspector_status_db
from ..users.user import User
from ..users.inspector import Inspector

class Admin(User):
    # ... существующий код ...
    
    def manage_inspectors_status(self) -> dict:
        """Управление статусами инспекторов"""
        if not self.has_permission('user_management'):
            return {'error': 'Недостаточно прав'}
        
        all_users = self.get_all_users()
        inspectors = {uid: data for uid, data in all_users.items() 
                     if data.get('role') == 'inspector'}
        
        status_info = {}
        for telegram_id, inspector_data in inspectors.items():
            status = inspector_status_db.get_inspector_status(int(telegram_id))
            status_info[telegram_id] = {
                'user_data': inspector_data,
                'status_info': status
            }
        
        return status_info
    
    def set_inspector_active(self, target_telegram_id: int, is_active: bool, reason: str = None) -> bool:
        """Устанавливает статус активности инспектора"""
        if not self.has_permission('user_management'):
            return False
        
        # Проверяем, что целевой пользователь - инспектор
        target_user = self.get_user_by_telegram_id(target_telegram_id)
        if not target_user or target_user.get('role') != 'inspector':
            return False
        
        inspector_status_db.set_inspector_active(target_telegram_id, is_active, reason)
        return True
    
    def get_active_inspectors(self) -> list:
        """Получает активных инспекторов"""
        if not self.has_permission('user_management'):
            return []
        
        active_ids = inspector_status_db.get_active_inspectors()
        result = []
        
        for telegram_id_str in active_ids:
            user_data = self.get_user_by_telegram_id(int(telegram_id_str))
            status_info = inspector_status_db.get_inspector_status(int(telegram_id_str))
            if user_data:
                result.append({
                    'user_data': user_data,
                    'status_info': status_info
                })
        
        return result
    
    def get_inactive_inspectors(self) -> list:
        """Получает неактивных инспекторов"""
        if not self.has_permission('user_management'):
            return []
        
        inactive_ids = inspector_status_db.get_inactive_inspectors()
        result = []
        
        for telegram_id_str in inactive_ids:
            user_data = self.get_user_by_telegram_id(int(telegram_id_str))
            status_info = inspector_status_db.get_inspector_status(int(telegram_id_str))
            if user_data:
                result.append({
                    'user_data': user_data,
                    'status_info': status_info
                })
        
        return result
    
    def get_inspector_detailed_info(self, telegram_id: int) -> dict:
        """Получает детальную информацию об инспекторе"""
        if not self.has_permission('user_management'):
            return {'error': 'Недостаточно прав'}
        
        user_data = self.get_user_by_telegram_id(telegram_id)
        if not user_data or user_data.get('role') != 'inspector':
            return {'error': 'Пользователь не является инспектором'}
        
        status_info = inspector_status_db.get_inspector_status(telegram_id)
        
        # Получаем статистику по сообщениям
        try:
            inspector = Inspector(telegram_id)
            stats = inspector.get_inspection_stats()
        except:
            stats = {'error': 'Не удалось получить статистику'}
        
        return {
            'user_data': user_data,
            'status_info': status_info,
            'inspection_stats': stats
        }