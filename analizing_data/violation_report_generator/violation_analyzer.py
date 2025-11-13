from typing import List, Optional
from report_generator.data_model import ChecklistData, Section, Subdivision, Criterion
from .violation_data_model import Violation, ViolationReportData

class ViolationAnalyzer:
    """
    Анализирует ChecklistData и извлекает информацию о нарушениях.
    Отвечает за принцип Single Responsibility.
    """
    
    @staticmethod
    def analyze_violations(checklist_data: ChecklistData) -> ViolationReportData:
        """Анализирует данные чек-листа и возвращает отчет о нарушениях"""
        violations: List[Violation] = []
        
        for section_key, section in checklist_data.sections.items():
            violations.extend(
                ViolationAnalyzer._analyze_section(section_key, section)
            )
        
        return ViolationReportData(
            original_report_name=checklist_data.file_name,
            inspection_date=checklist_data.inspection_date,
            section_name=checklist_data.section_name,
            inspector=checklist_data.inspector,
            violations=violations,
            total_violations=len(violations)
        )
    
    @staticmethod
    def _analyze_section(section_key: str, section: Section) -> List[Violation]:
        """Анализирует раздел на наличие нарушений"""
        violations = []
        
        # Проверяем подразделы
        if section.subdivisions:
            for sub_key, subdivision in section.subdivisions.items():
                violations.extend(
                    ViolationAnalyzer._analyze_subdivision(
                        section_key, section.description, 
                        sub_key, subdivision
                    )
                )
        else:
            # Проверяем критерии напрямую в разделе
            violations.extend(
                ViolationAnalyzer._analyze_criteria(
                    section_key, section.description, 
                    None, None, section.criteria
                )
            )
        
        return violations
    
    @staticmethod
    def _analyze_subdivision(
        section_key: str, 
        section_description: str,
        sub_key: str, 
        subdivision: Subdivision
    ) -> List[Violation]:
        """Анализирует подраздел на наличие нарушений"""
        return ViolationAnalyzer._analyze_criteria(
            section_key, section_description,
            sub_key, subdivision.description,
            subdivision.criteria
        )
    
    @staticmethod
    def _analyze_criteria(
        section_key: str,
        section_description: str,
        sub_key: Optional[str],
        sub_description: Optional[str],
        criteria: List[Criterion]
    ) -> List[Violation]:
        """Анализирует критерии на наличие нарушений"""
        violations = []
        
        for criterion in criteria:
            # Нарушение - когда критерий не соответствует (does_not_comply = 0)
            if criterion.does_not_comply == 0 and criterion.comment.strip():
                violation = Violation(
                    section_name=f"{section_key}. {section_description}",
                    subsection_name=(
                        f"{sub_key}. {sub_description}" 
                        if sub_key and sub_description 
                        else None
                    ),
                    criterion_number=criterion.number,
                    criterion_description=criterion.description,
                    comment=criterion.comment
                )
                violations.append(violation)
        
        return violations