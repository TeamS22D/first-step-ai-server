import pytest
from app.services.evaluate_doc_v3 import *
from pprint import pprint


def test_evaluate_doc_v3():
    user_prompt = ""
    with open("app/missions/templates/mission_01/sample_01_01.md" , "r", encoding="utf-8") as f:
        user_prompt = f.read()

    print(evaluate_doc_v3(user_document=user_prompt).__dict__)