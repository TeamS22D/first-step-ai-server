from fastapi import APIRouter, HTTPException
from app.schemas.test_model import TestRequest, AnswerRequest
from app.services.eval_document_v1 import eval_document_v1
from app.services.evaluate_doc_v2 import evaluate_doc_v2
from app.services._tmp_save_evaluate_log import save_evaluate_log


router = APIRouter()

@router.get("/")
def test():
    return {"response": "Hello, World!!"}

@router.post("/evaluate")
async def test2(item: TestRequest):
    try:
        result = eval_document_v1(user_prompt=item.content, document_type=item.id)
        save_evaluate_log(item.id, "", item.content, result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return result

@router.post("/evaluate2")
async def test3(item: AnswerRequest):
    try:
        result = evaluate_doc_v2(user_prompt=item.content, document_type=item.rubric_id, mission_id=item.mission_id)
        save_evaluate_log(item.rubric_id, item.mission_id, item.content, result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return result