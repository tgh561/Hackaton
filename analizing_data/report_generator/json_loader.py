from pathlib import Path
import json
from data_model import ChecklistData

class JsonLoader:
    @staticmethod
    def load(path: Path) -> ChecklistData:
        with open(path, 'r', encoding='utf-8') as f:
            data_dict = json.load(f)
        return ChecklistData(**data_dict)