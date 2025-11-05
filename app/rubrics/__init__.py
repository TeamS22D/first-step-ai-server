from .manager import RubricManager
from .models import Rubric, EvaluationItem
from typing import Optional, List

# Initialize the manager for the app to use
rubric_manager = RubricManager()

def get_rubric(name: str) -> Optional[Rubric]:
    """Convenience function to get a raw rubric by name."""
    return rubric_manager.get_rubric(name)

def get_evaluation_sheet(rubric_name: str, doc_type: str) -> Optional[List[EvaluationItem]]:
    """
    Gets a fully calculated evaluation sheet for a given rubric and document type.

    Args:
        rubric_name: The name of the rubric (e.g., 'report').
        doc_type: The type of the document to get the sheet for (e.g., '릴리즈', '주간보고').

    Returns:
        A list of EvaluationItem objects with calculated scores, or None if the rubric is not found.
    """
    rubric = get_rubric(rubric_name)
    if rubric:
        return rubric.get_evaluation_sheet(doc_type)
    return None