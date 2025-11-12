import re
from typing import Dict
from openpyxl.worksheet.worksheet import Worksheet

class MetadataExtractor:
    PATTERNS = {
        "revision_date": re.compile(r"Редакция от\s+(\d{2}\.\d{2}\.\d{4})", re.I),
        "inspection_date": re.compile(r"Дата проведения проверки\s*([\d\.]+)", re.I),
        "section_name": re.compile(r"(УПП|ЭМО|Инструментальный участок|Дробильное отделение|Помещение централизованной подачи материалов)", re.I),
        "inspector": re.compile(r"Проверку проводил\s*(.+)", re.I)
    }

    def extract_from_sheet(self, sheet: Worksheet) -> Dict[str, str]:
        lines = []
        for row in sheet.iter_rows(values_only=True):
            row_text = " ".join(str(cell).strip() for cell in row if cell is not None)
            if row_text:
                lines.append(row_text)
        full_text = "\n".join(lines)
        meta = {}
        for key, pattern in self.PATTERNS.items():
            m = pattern.search(full_text)
            meta[key] = m.group(1).strip() if m and m.group(1) else ""
        return meta