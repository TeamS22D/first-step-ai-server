from app.core.openai_client import ask_gpt
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pydantic import BaseModel

def eval_document_v1(
        model: str="gpt-4o",
        rubric: str="",
        structed_model: "BaseModel" = None,
        user_prompt: str = None,
        developer_prompt: str = None
) -> "BaseModel":
    """ 사용자 맞춤형 문서 평가 결과를 반환합니다.

    """

    developer_prompt = ''

    ask_gpt(response_model=BaseModel,
            model=model,
            user_prompt=user_prompt,
            developer_prompt= developer_prompt,
            additional_messages=
            )