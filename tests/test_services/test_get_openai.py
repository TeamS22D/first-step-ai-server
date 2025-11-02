import pytest
import json
from app.services.get_openapi import *
from app.services.chat import *


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

def test_get_word_description():
    print("\n\n#### test get word description ####\n\n")

    message = "니코틴아마이드 아데닌 다이뉴클레오타이드"

    response = get_word_description(message=message)

    print(response, type(response))

def test_chat():
    print("\n\n#### test chat ####\n\n")

    message = "어떤 프로젝트가 있었지? 기억이 잘 나지 않네"

    response = chatting(message=message)

    print(response)

def test_check_action():
    class API:
        def __init__(self):
            pass

        def attack(self, a, b, c, d, rr):
            return f"상대를 공격합니다. {a}, {b}, {c}, {d}, {rr}"

        def defence(self, a, b, c, d, rr):
            return f"공격을 막습니다. {b}, {d}, {rr}, {a}, {c}"

    api = API()

    message="내앞에 도둑이 있다."

    response = check_action(model="gpt-4o-mini", message=message)

    method = response.method
    kwargs = response.kwargs.model_dump()
    print(response)

    fn = getattr(api, method)
    print(fn(**kwargs))

def test_get_document():

    message = """GitHub를 이용하는 방법
필자가 자주 애용하는 방식이다.
예를 들면 theorydb.github.io\assets\img\의 위치에 포스트 계층과 동일하게 폴더를 만들어 포스트 제목-일련번호의 형태로 파일을 저장한 후, https://theorydb.github.io/assets/img/think/2019-06-25-think-future-ai-1.png와 같은 방식으로 링크를 걸어 활용한다.
물론, 이미지 파일 관리에 있어 노가다가 첨가되고 GitHub에 이미지를 먼저 올리지 않으면 Markdown을 작성하며 실시간으로 확인할 수 없다는 불편한 점이 있다.
하지만 필자가 처음 블로그를 개발했을 때 가장 중요했던 목적 하나는 블로그 서비스가 종료되더라도 포스트와 이미지를 개인 DB화 하여 영구 보존하는 것이었기에 큰 불만이 없는 방식이다. 더불어 숙달되어 큰 불편을 느끼지 않는다.
기타
구글드라이브, 플리커, 드랍박스에 이미지를 체계적으로 관리하고 URL을 생성하여 연결하는 것도 한가지 방법이다.
큰 불편함을 느끼지 않아 더 찾아보지는 않았는데 이 부분을 쉽게 처리해 줄 Plug-in이 존재할 것으로 믿는다.ㅎㅎ"""

    response = get_markdown(message=message)

    print(response)