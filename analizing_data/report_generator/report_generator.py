from pathlib import Path
from .data_model import ChecklistData 
from .score_calculator import ScoreCalculator
from .excel_generator import ExcelGenerator

class ReportGenerator:
    def __init__(self, calculator: ScoreCalculator, generator: ExcelGenerator):
        self.calculator = calculator
        self.generator = generator

    def generate_report(self, data: ChecklistData, output_path: Path) -> Path:
        """
        Генерирует отчет из готовых данных ChecklistData
        Идеально для использования с бэкендом
        """
        data = self.calculator.calculate_all_scores(data)
        return self.generator.generate(data, output_path)