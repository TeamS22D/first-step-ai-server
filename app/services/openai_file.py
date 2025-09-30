from openai import OpenAI
from app.core.config import config
import base64

client = OpenAI(api_key=config.OPENAI_API_KEY)

def get_openai_file(model: str = "gpt-4.1-nano", file_name: str = None, file_path: str = None):

    with open(file_path, "rb") as f:
        file = f.read()

    base64_string = base64.b64encode(file).decode("utf-8")

    response = client.responses.create(
        model = model,
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": "what is in this file?"},
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