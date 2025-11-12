from typing import Dict, Any
from pathlib import Path
from openpyxl import load_workbook
from metadata_extractor import MetadataExtractor
from structure_parser import ExcelStructureParser

class ExcelChecklistParser:
    def __init__(self, metadata_extractor: MetadataExtractor, structure_parser: ExcelStructureParser):
        self.metadata_extractor = metadata_extractor
        self.structure_parser = structure_parser

    def parse_file(self, file_path: str) -> Dict[str, Any]:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Файл не найден: {file_path}")

        wb = load_workbook(path, data_only=True)
        sheet = wb.active
        metadata = self.metadata_extractor.extract_from_sheet(sheet)
        structure = self.structure_parser.parse(sheet)

        return {
            "file_name": path.name,
            **metadata,
            **structure
        }