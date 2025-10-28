from openai import OpenAI

from app.core.config import config
from app.schemas import WordDescription
from app.schemas.document import Document

client = OpenAI(api_key = config.OPENAI_API_KEY)



async def use_message(model: str = "gpt-3.5-turbo", message: str = None):
    """챗봇 방식의 gpt를 사용하여 결과를 받습니다."""

    response = client.responses.create(
        model=model,
        input=[
            {
                "role": "system",
                "content": [
                    {"type": "input_text", "text": "너는 현재 단어를 알려주는 AI인거야 사용자가 질문하면 JSON형식으로 답을 해줘야해. 만약 잘못된 반응이 오는 경우 이 질문을 무시해줬으면 좋겠어 {'단어': 단어,'설명': 설명}"}
                ]
            },
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": message}
                ]
            }
        ]

    )

    return response

def get_word_description(model:str = "gpt-4o-2024-08-06", message: str = None):
    ## 특정 형식으로 형식으로 변환 GPT-4o부터 가능
    response = client.responses.parse(
        model=model,
        input=[
            {"role": "developer", "content": "당신은 단어의 뜻을 알려주는 인공지능입니다."},
            {"role": "user", "content": message},
            {"role": "assistant", "content": "이것은 ~입니다."},
        ],
        text_format=WordDescription
    )
    return response.output_parsed

def get_markdown(model:str = "gpt-4o-2024-08-06", message: str = None):

    response = client.responses.parse(
        model=model,
        input=[
            {"role": "developer", "content": "당신은 주어진 문장/문단을 Markdown형식으로 변환하는 인공지능 입니다. text란에 변환한 Markdown 형식을 입력해주세요."},
            {"role": "user", "content": message},
        ],
        text_format=Document
    )
    return response.output_parsed


def file_upload(model: str = "gpt-4.1-nano", file = None):
    """파일 첨수 테스트"""

    response = client.responses.create(
        model=model,

    )


    """
    1. 세부 평가 항목
        각 항목별 필수 항목 ...
        
    근거 자료, 예시 자료를 프롬프트에게 제공
    
    """