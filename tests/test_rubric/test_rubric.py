from app.rubrics import rubric_manager, get_rubric
import pytest


def test_get_rubric():
    print("\n\n test get_rubric \n\n")

    report_rubric = get_rubric("report_evaluation_criteria")
    print(report_rubric.base_criteria)
    assert report_rubric.name == "report_evaluation_criteria"

