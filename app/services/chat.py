from openai import OpenAI
from pydantic import BaseModel

from app.core.config import config

class KwArgs(BaseModel):
    a: str
    b: str
    c: str
    d: str
    rr: str

class Action(BaseModel):
    method: str
    kwargs: KwArgs



client = OpenAI(api_key = config.OPENAI_API_KEY)

def check_action(model:str = "gpt-4o-2024-08-06", message: str = None) -> Action:
    ## 특정 형식으로 형식으로 변환 GPT-4o부터 가능
    response = client.responses.parse(
        model=model,
        input=[
            {"role": "developer", "content": "특정한 상황에서 어떠한 행동을 취할지 정하는 AI 입니다. 행동은 'attack', 'defence' 둘중 하나를 선택하고, 이에 들어가는 인자는 각각 attack에[a, b, c] 그리고 defense에[b, d, rr]이 있습니다."},
            {"role": "user", "content": message}
        ],
        text_format=Action
    )
    return response.output_parsed



def chatting(model:str = "gpt-4o-2024-08-06", message: str = None):
    ## 특정 형식으로 형식으로 변환 GPT-4o부터 가능
    response = client.responses.create(
        model=model,
        input=[
            {"role": "developer", "content": "당신은 대상과 이야기하는 인공지능 입니다."},

          {"role": "user", "content": "안녕, 오늘은 좀 가볍게 얘기하고 싶어."},
          {"role": "assistant", "content": "좋아요 😊 무거운 주제는 잠시 내려두고 편하게 이야기해요. 요즘 뭐 하면서 지내세요?"},

          {"role": "user", "content": "최근에 Java 프로젝트를 정리하고 있는데, 문서화가 좀 막막해."},
          {"role": "assistant", "content": "문서화라면 기능 명세서나 API 문서 같은 거죠? 전에 Spring Boot랑 ActivityPub 구현하신다고 했었는데, 그거 관련이에요?"},

          {"role": "user", "content": "응 맞아. 기능 명세서가 너무 추상적이라 디자인팀이 헷갈려 하더라고."},
          {"role": "assistant", "content": "그럴 땐 구체적인 시나리오나 사용자 흐름을 예로 들어주면 좋아요. 예를 들어 ‘사용자가 글을 작성하면 Outbox에 Activity가 생성된다’ 같은 형태로요."},

          {"role": "user", "content": "요즘은 라이브러리 형태로 코드도 정리하고 싶어서 구조 고민 중이야."},
          {"role": "assistant", "content": "그때 Python으로 `__init__.py` 구조랑 모듈화 배우신 것도 도움이 되겠네요. 내부 의존성 분리나 client 모듈 설계하셨던 거 기억나요 😊"},

          {"role": "user", "content": "맞아, 그때 설명 진짜 도움이 많이 됐어. 덕분에 Flask 버전도 돌려봤지."},
          {"role": "assistant", "content": "오, Flask 서버에서 GUI 띄우는 실시간 버스 알림 앱이었죠? macOS 트레이랑 TAGO API까지 연동하는 구조였던 걸로 기억해요!"},

          {"role": "user", "content": "그래서 이번엔 그 프로젝트에 릴리즈 노트도 써보려 해."},
          {"role": "assistant", "content": "좋아요 👏 릴리즈 노트는 버전 관리의 핵심이에요. 전에 예시로 드린 `Added / Fixed / Improved` 형식 기억나시죠? 그걸 그대로 쓰면 팀에도 공유하기 좋아요."},

          {"role": "user", "content": "나중에는 이런 프로젝트들을 모아서 포트폴리오로 만들고 싶어."},
          {"role": "assistant", "content": "완전 좋은 생각이에요. 특히 Unofficial-TAGO-API 같은 라이브러리성 프로젝트는 오픈소스 포트폴리오로도 인상 깊을 거예요 😎"},

          {"role": "user", "content": "그래서 문서랑 코드 스타일을 좀 더 일관되게 관리하려고."},
          {"role": "assistant", "content": "좋아요. 예를 들어 README.md에 릴리즈 노트, 설치 방법, 예제 코드, API 설명을 함께 포함하면 깔끔한 구조가 돼요. Markdown 포맷으로 정리하면 협업에도 유리하죠."},

          {"role": "user", "content": message}
],



    )
    return response.output_text