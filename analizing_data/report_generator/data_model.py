from pydantic import BaseModel, Field
from typing import Dict, List, Optional

class Criterion(BaseModel):
    number: int
    description: str
    complies: Optional[int] = Field(None, description="1 if complies")
    does_not_comply: Optional[int] = Field(None, description="0 if not")
    comment: str = ""

class Subdivision(BaseModel):
    description: str
    criteria: List[Criterion]
    total_score: Optional[float] = None

class Section(BaseModel):
    description: str
    criteria: List[Criterion]
    subdivisions: Dict[str, Subdivision] = {}
    total_score: Optional[float] = None

class ChecklistData(BaseModel):
    file_name: str
    revision_date: str = ""
    inspection_date: str = ""
    section_name: str = ""
    inspector: str = ""
    sections: Dict[str, Section] = {}
    overall_score: Optional[float] = None