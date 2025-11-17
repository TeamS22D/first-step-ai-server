from openai import OpenAI

from app.core.config import config

client = OpenAI(api_key = config.OPENAI_API_KEY)



def use_message(model: str = "gpt-3.5-turbo", message: str = None, developer: str = None):
    """챗봇 방식의 gpt를 사용하여 결과를 받습니다."""

    response = client.responses.create(
        model=model,
        input=[
            {
                "role": "developer",
                "content": [
                    {"type": "input_text", "text": developer}
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