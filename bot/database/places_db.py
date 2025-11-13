import json
import os
from datetime import datetime
from typing import Dict, Optional


class PlacesDB:
    def __init__(self, places_file: str = "places.json", search_file: str = "search.json"):
        self.places_file = places_file
        self.search_file = search_file
        self.places = self._load_places()
        self.search = self._load_search()

    def _load_places(self) -> Dict:
        """Загружает данные о местах и бригадирах"""
        if os.path.exists(self.places_file):
            try:
                with open(self.places_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def _load_search(self) -> Dict:
        """Загружает данные о проверках"""
        if os.path.exists(self.search_file):
            try:
                with open(self.search_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def _save_search(self):
        """Сохраняет данные о проверках"""
        with open(self.search_file, 'w', encoding='utf-8') as f:
            json.dump(self.search, f, ensure_ascii=False, indent=2)

    def get_inspections_by_inspector(self, inspector_id: str) -> Dict:
        """Возвращает проверки для конкретного проверяющего"""
        inspector_id_str = str(inspector_id)
        inspections = {}

        for place_id, inspection_data in self.search.items():
            if inspection_data.get('inspector') == inspector_id_str:
                inspections[place_id] = inspection_data
            print(place_id)
            print(inspection_data)
        return inspections

    def get_available_inspections(self) -> Dict:
        """Возвращает свободные проверки (без назначенного проверяющего)"""
        available = {}

        for place_id, inspection_data in self.search.items():
            if not inspection_data.get('inspector') or inspection_data.get('inspector') == 'date':
                available[place_id] = inspection_data

        return available

    def assign_inspector_to_inspection(self, place_id: str, inspector_id: str) -> bool:
        """Назначает проверяющего на проверку"""
        if place_id not in self.search:
            return False

        self.search[place_id]['inspector'] = str(inspector_id)
        self._save_search()
        return True

    def update_inspection_date(self, place_id: str, date: str) -> bool:
        """Обновляет дату проверки"""
        if place_id not in self.search:
            return False

        self.search[place_id]['date'] = date
        self._save_search()
        return True

    def get_supervisor_by_place(self, place_id: str) -> Optional[str]:
        """Возвращает логин бригадира для места"""
        return self.places.get(place_id)

    def get_all_places(self) -> Dict:
        """Возвращает все места"""
        return self.places

    def get_all_inspections(self) -> Dict:
        """Возвращает все проверки"""
        return self.search

    def create_inspection(self, place_id: str, inspector_id: str = None, date: str = None) -> bool:
        """Создает новую проверку"""
        if place_id not in self.places:
            return False

        self.search[place_id] = {
            'date': date or 'Не назначена',
            'inspector': inspector_id or 'Не назначен'
        }
        self._save_search()
        return True

    def get_approved_inspections_by_inspector(self, inspector_id: str) -> Dict:
        """Возвращает согласованные проверки для проверяющего (с назначенным временем)"""
        inspector_id_str = str(inspector_id)
        approved_inspections = {}

        for place_id, inspection_data in self.search.items():
            if (inspection_data.get('inspector') == inspector_id_str and
                    inspection_data.get('date') not in [None, 'Не назначена', 'date'] and
                    inspection_data.get('date') != 'Не назначена'):
                approved_inspections[place_id] = inspection_data

        return approved_inspections

    def get_inspection_status(self, place_id: str) -> str:
        """Возвращает статус проверки"""
        inspection_data = self.search.get(place_id, {})
        date = inspection_data.get('date', 'Не назначена')

        if date in [None, 'Не назначена', 'date']:
            return 'pending'
        else:
            return 'approved'


# Глобальный экземпляр БД
places_db = PlacesDB()