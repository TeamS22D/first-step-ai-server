from openai import OpenAI
from app.core.config import config
import base64

client = OpenAI(api_key=config.OPENAI_API_KEY)

def get_openai_file(model: str = "gpt-4.1-nano", file_name: str = None, file_path: str = None):

    with open(file_path, "rb") as f:
        file = f.read()

    base64_string = base64.b64encode(file).decode("utf-8")

    response = client.responses.create(
        model=model,
        input=[ # type: ignore
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": "파일의 내용이 무엇인지 나에게 설명해줘. 텍스트는 무엇이 있고 이미지는 무엇이 있는지 알려줘"},
                    {
                        "type": "input_file",
                        "filename": file_name,
                        "file_data": f"data:application/pdf;base64,{base64_string}",
                    }
                ]
            }
        ]
    )

    return response

def process_file(model: str = "gpt-4.1-nano", file_url: str = None):

    response = client.responses.create(
        model=model,
        input=[ # type: ignore
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": "이 pdf의 metadata를 추출해주고 text가 무엇이 있는지 json형식으로 반환해줘"},
                    {
                        "type": "input_file",
                        "file_url": file_url
                    }
                ]
            }
        ]
    )

    return response


def upload_file(file_url: str):

    client.files.create(
        file=open(file_url, "rb"),
        purpose="user_data",
        expires_after={
            "anchor": "created_at",
            "seconds": 2592000
        }
    )

def search_file(file_id: str):

    return client.files.retrieve(file_id=file_id)


def extract_docx(file_id: str, model: str = "gpt-4.1-nano"):

    response = client.responses.create(
        model=model,
        input=[ # type: ignore
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": """
                            pdf파일을 분석해줘. 단, 내가 말하는 양식에 맞도록 분석하고 JSON형식으로만 보내줘
                            1. 문서의 구조를 나타내도록 한다.
                            2. 문서의 text는 {"text": 값}, 만약 스타일이 있다면 {"text": 값, "style": styles}
                            3. 다른 어떠한 말도 하지 않고 보내주는 파일을 분석만 한다
                            4. text, table 등 docx파일에서 사용되는 양식을 **pdf 파일 구조** 와 **pdf 파일의 흐름에**맞게 분석한다.
                            5. 현재 너가 분석하는 파일은 원래 docx였음을 명시해줬으면 좋겠어
                            """
                    },
                    {
                        "type": "input_file",
                        "file_id": file_id,
                    }
                ]
            }
        ]
    )

    return response
