from pathlib import Path
from report_generator.data_model import ChecklistData
from .violation_analyzer import ViolationAnalyzer
from .violation_report_generator import ViolationReportGenerator
from .violation_data_model import ViolationReportData

class ViolationReportFacade:
    """
    Фасад для упрощенной работы с генерацией отчетов о нарушениях.
    Реализует принцип Facade из GRASP.
    """
    
    def __init__(self):
        self.analyzer = ViolationAnalyzer()
        self.generator = ViolationReportGenerator()
    
    def generate_violation_report(
        self, 
        checklist_data: ChecklistData, 
        output_path: Path
    ) -> Path:
        """
        Генерирует полный отчет о нарушениях на основе данных чек-листа
        """
        # Анализируем нарушения
        violation_data = self.analyzer.analyze_violations(checklist_data)
        
        # Генерируем отчет только если есть нарушения
        if not violation_data.has_violations:
            raise ValueError("Нет нарушений для генерации отчета")
        
        # Генерируем Excel отчет
        return self.generator.generate(violation_data, output_path)
    
    def analyze_violations_only(self, checklist_data: ChecklistData) -> ViolationReportData:
        """Только анализирует нарушения без генерации отчета"""
        return self.analyzer.analyze_violations(checklist_data)