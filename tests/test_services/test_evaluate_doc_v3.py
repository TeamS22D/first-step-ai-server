import pytest
from app.services.evaluate_doc_v3 import *
from pprint import pprint
from app.utils import rubric_manager

def test_evaluate_doc_v3():
    user_answer = ""
    question_prompt = ""
    rubric = rubric_manager.get_rubric("document_v2").__dict__
    with open("app/missions/templates/mission_01/example_01.md" , "r", encoding="utf-8") as f:
        user_answer = f.read()
    with open("app/missions/templates/mission_01/mission_01.md", "r", encoding="utf-8") as f:
        question_prompt = f.read()

    print(rubric, user_answer, question_prompt)

    # evaluation_result = evaluate_document(user_answer, question_prompt, rubric, "")
    # print(evaluation_result)