from .manager import RubricManager
from ._models import Rubric, EvaluationItem
from typing import Optional, List

# Initialize the manager for the app to use
rubric_manager = RubricManager()

__all__ = ["rubric_manager"]

