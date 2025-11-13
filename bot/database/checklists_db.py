import json
import os
import shutil
from typing import Dict, Optional
from datetime import datetime


class ChecklistsDB:
    def __init__(self, db_path: str = "data/checklists.json", photos_folder: str = "data/checklist_photos"):
        self.db_path = db_path
        self.photos_folder = photos_folder
        self.checklists = self._load_checklists()

        # Создаем папку для фото если нет
        os.makedirs(photos_folder, exist_ok=True)

    def _load_checklists(self) -> Dict:
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Миграция старых данных
                    for place_id, checklist in data.items():
                        if "completed_criteria" not in checklist:
                            checklist["completed_criteria"] = self._count_completed_criteria(checklist)
                        if "total_criteria" not in checklist:
                            checklist["total_criteria"] = self._count_total_criteria(checklist["checklist_data"])
                    return data
            except:
                return {}
        return {}

    def _save_checklists(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with open(self.db_path, 'w', encoding='utf-8') as f:
            json.dump(self.checklists, f, ensure_ascii=False, indent=2)

    def _count_completed_criteria(self, checklist: Dict) -> int:
        """Подсчитывает количество заполненных критериев"""
        completed = 0
        checklist_data = checklist["checklist_data"]
        for section_data in checklist_data["sections"].values():
            for criterion in section_data["criteria"]:
                if criterion.get('complies') is not None:
                    completed += 1
        return completed

    def _count_total_criteria(self, checklist_data: Dict) -> int:
        """Подсчитывает общее количество критериев"""
        total = 0
        for section_data in checklist_data["sections"].values():
            total += len(section_data["criteria"])
        return total

    def create_checklist(self, place_id: str, inspector_name: str, checklist_data: Dict) -> bool:
        total_criteria = self._count_total_criteria(checklist_data)
        completed_criteria = self._count_completed_criteria({"checklist_data": checklist_data})

        self.checklists[place_id] = {
            "checklist_data": checklist_data,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "status": "draft",
            "inspector_name": inspector_name,
            "completed_criteria": completed_criteria,
            "total_criteria": total_criteria
        }
        self._save_checklists()
        return True

    def get_checklist(self, place_id: str) -> Optional[Dict]:
        checklist = self.checklists.get(place_id)
        if checklist and "completed_criteria" not in checklist:
            # Миграция для старых записей
            checklist["completed_criteria"] = self._count_completed_criteria(checklist)
            checklist["total_criteria"] = self._count_total_criteria(checklist["checklist_data"])
            self._save_checklists()
        return checklist

    def update_criterion(self, place_id: str, section: str, criterion_number: int,
                         complies: bool, comment: str = "", photo_path: str = None) -> bool:
        if place_id not in self.checklists:
            return False

        checklist_data = self.checklists[place_id]["checklist_data"]
        section_data = checklist_data["sections"].get(section)

        if not section_data:
            return False

        # Находим критерий и обновляем
        for criterion in section_data["criteria"]:
            if criterion["number"] == criterion_number:
                old_complies = criterion.get('complies')

                criterion["complies"] = complies
                criterion["does_not_comply"] = not complies
                criterion["comment"] = comment
                if photo_path:
                    criterion["photo_path"] = photo_path

                # Обновляем счетчик completed_criteria
                if old_complies is None and complies is not None:
                    self.checklists[place_id]["completed_criteria"] += 1
                break

        self.checklists[place_id]["updated_at"] = datetime.now().isoformat()

        # Проверяем, завершен ли чек-лист
        if self._is_checklist_completed(place_id):
            self.checklists[place_id]["status"] = "completed"
            self.checklists[place_id]["completed_at"] = datetime.now().isoformat()

        self._save_checklists()
        return True

    def _is_checklist_completed(self, place_id: str) -> bool:
        """Проверяет, заполнен ли весь чек-лист"""
        checklist = self.checklists[place_id]
        return checklist["completed_criteria"] >= checklist["total_criteria"]

    def save_photo(self, place_id: str, section: str, criterion_number: int, photo_file_id: str) -> str:
        """Сохраняет фото для критерия и возвращает путь"""
        photo_folder = os.path.join(self.photos_folder, place_id, section)
        os.makedirs(photo_folder, exist_ok=True)

        photo_path = os.path.join(photo_folder, f"criterion_{criterion_number}.jpg")
        # Здесь должна быть логика сохранения файла из file_id
        # Пока просто возвращаем путь
        return photo_path

    def get_checklist_progress(self, place_id: str) -> Dict:
        """Возвращает прогресс заполнения чек-листа"""
        checklist = self.get_checklist(place_id)
        if not checklist:
            return {"completed": 0, "total": 0, "percentage": 0}

        completed = checklist.get("completed_criteria", 0)
        total = checklist.get("total_criteria", 0)
        percentage = (completed / total * 100) if total > 0 else 0

        return {
            "completed": completed,
            "total": total,
            "percentage": round(percentage, 1)
        }


# Глобальный экземпляр
checklists_db = ChecklistsDB()