from typing import List

from app.utils import rubric_manager

from app.utils.rubric_manager.models import Category


def test_rubrics():
    print("\n\n test rubrics \n\n")

    assert isinstance(rubric_manager.get_basic_rubric("document"), List)
    assert isinstance(rubric_manager.get_basic_rubric("document")[0], Category)

    assert isinstance(rubric_manager.get_basic_rubric("email"), List)
