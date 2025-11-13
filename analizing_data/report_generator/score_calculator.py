from .data_model import Section, Subdivision, ChecklistData
class ScoreCalculator:
    @staticmethod
    def calculate_section_score(section: Section) -> float:
        if section.subdivisions:
            sub_scores = [ScoreCalculator.calculate_subdivision_score(sub) for sub in section.subdivisions.values() if sub.criteria]
            return sum(sub_scores) / len(sub_scores) if sub_scores else 0.0
        else:
            complying = sum(1 for c in section.criteria if c.complies == 1)
            return complying / len(section.criteria) if section.criteria else 0.0

    @staticmethod
    def calculate_subdivision_score(sub: Subdivision) -> float:
        complying = sum(1 for c in sub.criteria if c.complies == 1)
        return complying / len(sub.criteria) if sub.criteria else 0.0

    def calculate_all_scores(self, data: ChecklistData) -> ChecklistData:
        total_scores = []
        for section in data.sections.values():
            section.total_score = self.calculate_section_score(section)
            total_scores.append(section.total_score)
            for sub in section.subdivisions.values():
                sub.total_score = self.calculate_subdivision_score(sub)
        data.overall_score = sum(total_scores) / len(total_scores) if total_scores else 0.0
        return data