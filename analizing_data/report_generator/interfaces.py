from abc import ABC, abstractmethod
from typing import Dict
from pathlib import Path

class GeneratorInterface(ABC):
    """Интерфейс для генераторов (Interface Segregation)."""
    @abstractmethod
    def generate(self, data: Dict, output_path: Path) -> Path:
        pass
