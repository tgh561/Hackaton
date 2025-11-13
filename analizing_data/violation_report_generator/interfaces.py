from abc import ABC, abstractmethod
from pathlib import Path
from report_generator.data_model import ChecklistData
from .violation_data_model import ViolationReportData

class GeneratorInterface(ABC):
    """Интерфейс для генераторов отчетов"""
    @abstractmethod
    def generate(self, data, output_path: Path) -> Path:
        pass

class ChecklistGeneratorInterface(GeneratorInterface):
    """Интерфейс для генераторов чек-листов"""
    @abstractmethod
    def generate(self, data: ChecklistData, output_path: Path) -> Path:
        pass

class ViolationReportGeneratorInterface(GeneratorInterface):
    """Интерфейс для генераторов отчетов о нарушениях"""
    @abstractmethod
    def generate(self, data: ViolationReportData, output_path: Path) -> Path:
        pass