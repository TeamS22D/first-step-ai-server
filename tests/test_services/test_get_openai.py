import pytest
import json

from app.services import get_openapi

def test_get_openapi():
    message = "아첨이 무엇인지 궁금해"
    #
    # response = get_openapi.use_message(message=message)
    #
    # print(response.output_text)


def test_convert_json():
    print("\n\n#### test convert json ####\n\n")

    string = '{"단어": "아첨", "설명": "남을 기쁘게 하기 위해 비아냥거리고 잘맞추는 말이나 행동을 하는 것을 가리키는 단어입니다."}'

    python_dict = json.loads(string)

    print(python_dict)