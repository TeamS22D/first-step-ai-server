from app.rubrics import rubric_manager, get_rubric, get_evaluation_sheet
from app.utils.prompt_converter import convert_criteria_to_prompt_string
import pytest
from pprint import pprint

def test_get_rubric():
    print("\n\n test get_rubric \n\n")

    report_rubric = get_rubric("report_evaluation_criteria")
    pprint(report_rubric.base_criteria)
    print(convert_criteria_to_prompt_string(report_rubric.base_criteria))
    assert report_rubric.name == "report_evaluation_criteria"

