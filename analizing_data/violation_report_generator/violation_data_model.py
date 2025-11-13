from pydantic import BaseModel
from typing import List, Optional
from dataclasses import dataclass
from pathlib import Path

@dataclass
class Violation:
    section_name: str
    subsection_name: Optional[str]
    criterion_number: int
    criterion_description: str
    comment: str
    photo_path: Optional[Path] = None

class ViolationReportData(BaseModel):
    """Данные для отчета о нарушениях"""
    original_report_name: str
    inspection_date: str
    section_name: str
    inspector: str
    violations: List[Violation]
    total_violations: int
    
    @property
    def has_violations(self) -> bool:
        return len(self.violations) > 0