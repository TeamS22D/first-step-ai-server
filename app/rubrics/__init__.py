from .manager import RubricManager
from .models import Rubric
from typing import Optional

# Initialize the manager for the app to use
rubric_manager = RubricManager()

def get_rubric(name: str) -> Optional[Rubric]:
    """Convenience function to get a rubric by name."""
    return rubric_manager.get_rubric(name)
