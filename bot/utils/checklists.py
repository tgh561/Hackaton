import json
import os
from typing import Dict, List
import glob


class ChecklistManager:
    def __init__(self, templates_folder: str = "checklist_templates"):
        self.templates_folder = templates_folder
        self.checklist_templates = {}
        self.load_all_templates()

    def load_all_templates(self):
        """Загружает все шаблоны чек-листов из папки"""
        if not os.path.exists(self.templates_folder):
            os.makedirs(self.templates_folder)
            return

        template_files = glob.glob(os.path.join(self.templates_folder, "*.json"))

        for file_path in template_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    template_data = json.load(f)

                file_name = os.path.basename(file_path)
                form_key = file_name.replace('.json', '').lower()
                self.checklist_templates[form_key] = template_data

            except Exception as e:
                print(f"❌ Ошибка загрузки {file_path}: {e}")

    def get_checklist_template(self, place_id: str) -> Dict:
        """Возвращает шаблон чек-листа для места"""
        place_number = place_id.replace('place_', '')
        form_key = f"form{place_number}"
        return self.checklist_templates.get(form_key,
                                            self.checklist_templates.get("form2", self.get_default_template()))

    def get_default_template(self) -> Dict:
        """Возвращает шаблон по умолчанию"""
        return {
            "file_name": "стандартная_форма.xlsx",
            "revision_date": "",
            "inspection_date": "",
            "section_name": "Общий участок",
            "inspector": "",
            "sections": {
                "А": {
                    "description": "Общие критерии оценки",
                    "criteria": [
                        {
                            "number": 1,
                            "description": "Общее состояние рабочего пространства",
                            "complies": None,
                            "does_not_comply": None,
                            "comment": ""
                        }
                    ],
                    "total_score": None
                }
            },
            "overall_score": None
        }

    def format_checklist_message(self, place_id: str, checklist_data: Dict = None) -> str:
        """Форматирует чек-лист для отправки в сообщении"""
        if not checklist_data:
            template = self.get_checklist_template(place_id)
        else:
            template = checklist_data["checklist_data"]

        message = f"📋 {template['section_name']}\n"
        message += f"📁 Файл: {template['file_name']}\n\n"

        for section_key, section_data in template['sections'].items():
            message += f"🔹 РАЗДЕЛ {section_key}:\n"
            message += f"{section_data['description']}\n\n"

            for criterion in section_data['criteria']:
                status = "⚪ Не проверен"
                if criterion.get('complies') is True:
                    status = "✅ Соответствует"
                elif criterion.get('does_not_comply') is True:
                    status = "❌ Не соответствует"

                message += f"{criterion['number']}. {criterion['description']}\n"
                message += f"   Статус: {status}\n"
                if criterion.get('comment'):
                    message += f"   💬 {criterion['comment']}\n"
                message += "\n"

            message += "────────────────────\n\n"

        message += "Для заполнения нажмите '✅ Заполнить чек-лист'"

        return message


checklist_manager = ChecklistManager()