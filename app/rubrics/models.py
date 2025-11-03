from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class BaseCriterion:
    major_item: str
    score: int
    minor_item: str
    minor_score: int
    evaluation_criteria: str
    measurement_point: str
    evaluation_method: str

@dataclass
class WeightedCriterion:
    item: str
    weights: Dict[str, int] # e.g., {'기본': 20, '주간보고': 15, ...}

@dataclass
class SpecializedCriterion:
    doc_type: str
    item: str
    criteria: str
    score: int
    measurement_method: str

@dataclass
class Rubric:
    name: str
    base_criteria: List[BaseCriterion] = field(default_factory=list)
    weighted_criteria: List[WeightedCriterion] = field(default_factory=list)
    specialized_criteria: List[SpecializedCriterion] = field(default_factory=list)
    # other sheets can be added here if needed, e.g., checklists, grading guides