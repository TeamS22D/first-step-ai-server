from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class EvaluationItem:
    """Represents a single, calculated item in the final evaluation sheet."""
    major_item: str
    minor_item: str
    score: int
    evaluation_criteria: str
    measurement_point: str
    evaluation_method: str

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

    def get_evaluation_sheet(self, doc_type: str) -> List[EvaluationItem]:
        """
        Generates a final evaluation sheet for a specific document type by applying weights
        and adding specialized criteria.
        """
        print(f"--- Generating sheet for doc_type: '{doc_type}' ---")
        evaluation_sheet: List[EvaluationItem] = []
        
        query_doc_type = '기본(100)' if doc_type == '기본' else doc_type

        # 1. Create a lookup for weights for the given doc_type
        doc_type_weights: Dict[str, int] = {}
        for wc in self.weighted_criteria:
            weight = wc.weights.get(query_doc_type, wc.weights.get('기본(100)'))
            if weight is not None:
                 doc_type_weights[wc.item] = weight
        print(f"Created weight lookup for '{query_doc_type}': {doc_type_weights}")

        # 2. Apply weights to base criteria
        for bc in self.base_criteria:
            major_item_base_score = bc.score
            major_item_weighted_score = doc_type_weights.get(bc.major_item, major_item_base_score)
            
            final_score = bc.minor_score
            if major_item_weighted_score != major_item_base_score and major_item_base_score > 0:
                ratio = major_item_weighted_score / major_item_base_score
                final_score = round(bc.minor_score * ratio)

            evaluation_sheet.append(EvaluationItem(
                major_item=bc.major_item,
                minor_item=bc.minor_item,
                score=final_score,
                evaluation_criteria=bc.evaluation_criteria,
                measurement_point=bc.measurement_point,
                evaluation_method=bc.evaluation_method,
            ))

        # 3. Add specialized criteria for the doc_type
        num_specialized = 0
        for sc in self.specialized_criteria:
            if sc.doc_type.startswith(doc_type):
                num_specialized += 1
                evaluation_sheet.append(EvaluationItem(
                    major_item='특화 평가항목',
                    minor_item=sc.item,
                    score=sc.score,
                    evaluation_criteria=sc.criteria,
                    measurement_point='',
                    evaluation_method=sc.measurement_method,
                ))
        print(f"Added {num_specialized} specialized criteria.")
        print(f"Final evaluation sheet has {len(evaluation_sheet)} items.")
        return evaluation_sheet