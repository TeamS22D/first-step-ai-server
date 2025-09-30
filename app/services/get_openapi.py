from openai import OpenAI

from app.core.config import config


client = OpenAI(api_key = config.OPENAI_API_KEY)


def use_message(model: str = "gpt-3.5-turbo", message: str = None):
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

def file_upload(model: str = "gpt-4.1-nano", file = None):
    pass