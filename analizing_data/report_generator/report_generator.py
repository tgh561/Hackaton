from pathlib import Path
from json_loader import JsonLoader
from score_calculator import ScoreCalculator
from excel_generator import ExcelGenerator

class ReportGenerator:
    def __init__(self, loader: JsonLoader, calculator: ScoreCalculator, generator: ExcelGenerator):
        self.loader = loader
        self.calculator = calculator
        self.generator = generator

    def generate_report(self, json_path: Path, output_path: Path) -> Path:
        data = self.loader.load(json_path)
        data = self.calculator.calculate_all_scores(data)
        return self.generator.generate(data, output_path)