from app.models.DocumentEvaluation import DocumentEvaluation
from app.utils.rubric_manager import rubric_manager
from app.core.openai_client import ask_gpt

#TODO: response Model
#TODO: 예시 만들기, 예시 바탕으로 good, suggested 예시 만들기
#TODO: 템플릿 생성
def evaluate_doc_v3(
    model: str="gpt-4o",
    user_document: str=None,
    mission_id: str=None,
    rubric_name: str=None,
)-> DocumentEvaluation:
    rubric = rubric_manager.get_rubric(rubric_name)
    rubric_prompt = None

    prompt = ""
    with open("app/services/report_document_prompt_v2.txt", "r", encoding="utf-8") as f:
        prompt = f.read()

    return ask_gpt(
        user_prompt=user_document,
        model=model,
        developer_prompt=prompt,
        response_model=DocumentEvaluation,
    )

