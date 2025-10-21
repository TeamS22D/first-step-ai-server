import pytest
from pydantic import BaseModel
from app.core.openai_client import ask_gpt



def test_ask_gpt():

    class Ask(BaseModel):
        text: str

    print(ask_gpt(response_model=Ask, model="gpt-4o", user_prompt="아무말이나 해줘! 빠르게"))