import re
from typing import Dict, Any
from openpyxl.worksheet.worksheet import Worksheet

class ExcelStructureParser:
    IGNORE_PATTERNS = [
        re.compile(r"Проверку проводил", re.I),
        re.compile(r"должность.*подпись.*расшифровка", re.I),
        re.compile(r"[_]{5,}", re.I)  # Много подчёркиваний
    ]

    def parse(self, sheet: Worksheet) -> Dict[str, Any]:
        structure: Dict[str, Any] = {"sections": {}, "overall_score": None}
        current_section = None
        current_subsection = None
        last_criterion = None

        for row in sheet.iter_rows():
            cells = [cell for cell in row if cell.value is not None]
            if not cells:
                continue

            first_cell_value = str(cells[0].value).strip() if cells[0].value else ""
            rest_text = " ".join(str(c.value).strip() for c in cells[1:] if c.value)

            # Игнор мусора и подписи
            if any(kw in rest_text.lower() for kw in ["???", "старонка", "страница"]) or any(p.search(rest_text) for p in self.IGNORE_PATTERNS):
                continue

            section_match = re.fullmatch(r"[A-ZА-Я]", first_cell_value.upper())
            if section_match:
                current_section = first_cell_value.upper()
                current_subsection = None
                structure["sections"][current_section] = self._create_section(rest_text)
                continue

            subsection_match = re.fullmatch(r"[A-ZА-Я]\d", first_cell_value.upper())
            if subsection_match:
                if current_section:
                    current_subsection = first_cell_value.upper()
                    structure["sections"][current_section]["subdivisions"][current_subsection] = self._create_subsection(rest_text)
                continue

            try:
                crit_num = int(first_cell_value)
                if 1 <= crit_num <= 100 and current_section:
                    criterion = self._create_criterion(crit_num, rest_text)
                    if current_subsection:
                        structure["sections"][current_section]["subdivisions"][current_subsection]["criteria"].append(criterion)
                    else:
                        structure["sections"][current_section]["criteria"].append(criterion)
                    last_criterion = criterion
                    continue
            except ValueError:
                pass

            if re.search(r"Общий балл|Общая оценка|Итоговая оценка", rest_text, re.I):
                if current_subsection and current_section:
                    structure["sections"][current_section]["subdivisions"][current_subsection]["total_score"] = None
                elif current_section:
                    structure["sections"][current_section]["total_score"] = None
                continue

            if last_criterion and rest_text:
                last_criterion["description"] += " " + rest_text

        return structure

    @staticmethod
    def _create_section(desc: str) -> Dict[str, Any]:
        return {
            "description": desc,
            "criteria": [],
            "subdivisions": {},
            "total_score": None
        }

    @staticmethod
    def _create_subsection(desc: str) -> Dict[str, Any]:
        return {
            "description": desc,
            "criteria": [],
            "total_score": None
        }

    @staticmethod
    def _create_criterion(number: int, desc: str) -> Dict[str, Any]:
        return {
            "number": number,
            "description": desc.strip(),
            "complies": None,
            "does_not_comply": None,
            "comment": ""
        }