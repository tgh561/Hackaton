import openpyxl
from openpyxl.styles import Font, Alignment, Border, Side
from pathlib import Path
from typing import Dict
from data_model import ChecklistData

class ExcelGenerator:
    def generate(self, data: ChecklistData, output_path: Path) -> Path:
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Лист1"

        self._setup_header(ws, data)
        row_idx = self._setup_table_header(ws)

        for section_key, section in data.sections.items():
            row_idx = self._add_section(ws, section_key, section, row_idx)

        self._add_overall_score(ws, data.overall_score, row_idx)
        self._apply_styles(ws)

        wb.save(output_path)
        return output_path

    def _setup_header(self, ws, data: ChecklistData):
        if data.revision_date:
            ws['A1'] = f"Редакция от {data.revision_date}"
        ws['A2'] = data.section_name
        ws['C2'] = "Дата проведения проверки"

    def _setup_table_header(self, ws):
        ws['A5'] = "Чек-лист оценки состояния оборудования и рабочего пространства рабочего персонала"
        ws['A6'] = "№ п/п"
        ws['B6'] = "Критерий оценки"
        ws['C6'] = "Оценка"
        ws['D6'] = ""
        ws['E6'] = "Краткий комментарий с указанием номера единицы оборудования, где выявлено несоответствие, и фото несоответствия"
        ws['C7'] = "соответствует"
        ws['D7'] = "не соответствует"
        return 8

    def _add_section(self, ws, key: str, section, row_idx: int) -> int:
        ws.cell(row=row_idx, column=1).value = key
        ws.cell(row=row_idx, column=2).value = section.description
        row_idx += 1

        if section.subdivisions:
            for sub_key, sub in section.subdivisions.items():
                row_idx = self._add_subdivision(ws, sub_key, sub, row_idx)
        else:
            row_idx = self._add_criteria(ws, section.criteria, row_idx)

        if section.total_score is not None:
            ws.cell(row=row_idx, column=2).value = f"Общий балл за раздел {key}"
            ws.cell(row=row_idx, column=3).value = round(section.total_score, 2)
            row_idx += 2
        return row_idx

    def _add_subdivision(self, ws, key: str, sub, row_idx: int) -> int:
        ws.cell(row=row_idx, column=1).value = key
        ws.cell(row=row_idx, column=2).value = sub.description
        row_idx += 1
        row_idx = self._add_criteria(ws, sub.criteria, row_idx)
        if sub.total_score is not None:
            ws.cell(row=row_idx, column=2).value = f"Общий балл за раздел {key}"
            ws.cell(row=row_idx, column=3).value = round(sub.total_score, 2)
            row_idx += 2
        return row_idx

    def _add_criteria(self, ws, criteria, row_idx: int) -> int:
        for crit in criteria:
            ws.cell(row=row_idx, column=1).value = crit.number
            ws.cell(row=row_idx, column=2).value = crit.description
            ws.cell(row=row_idx, column=3).value = crit.complies
            ws.cell(row=row_idx, column=4).value = crit.does_not_comply
            ws.cell(row=row_idx, column=5).value = crit.comment
            row_idx += 1
        return row_idx

    def _add_overall_score(self, ws, score: float, row_idx: int):
        ws.cell(row=row_idx, column=2).value = "Итоговая оценка структурному подразделению"
        ws.cell(row=row_idx, column=3).value = round(score, 2) if score is not None else 0
        
    def _apply_styles(self, ws):
        bold_font = Font(bold=True)
        center_align = Alignment(horizontal='center', vertical='center', wrap_text=True)
        border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))
        for row in ws['A6:E7']:
            for cell in row:
                cell.font = bold_font
                cell.alignment = center_align
                cell.border = border