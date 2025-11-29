import pytest
from app.utils import rubric_manager


def test_rubric_manager():
    print("\n\n test_rubric_manager")

    print(rubric_manager.get_special_rubric("document", "mission_01"))
    print(rubric_manager.get_basic_rubric("document"))