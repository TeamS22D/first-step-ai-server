from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.schemas.test_model import TestRequest, AnswerRequest
from app.services.eval_document_v1 import eval_document_v1
from app.services.evaluate_doc_v2 import evaluate_doc_v2
from app.services._tmp_save_evaluate_log import save_evaluate_log
from app.api.mail import evaluate_mission_email # mail.py에서 함수 import


router = APIRouter()

class EmailMissionRequest(BaseModel):
    mission_id: str
    user_email: str

@router.get("/")
def test():
    return {"response": "Hello, World!!"}

@router.post("/evaluate-email-mission")
async def evaluate_email_mission_endpoint(request: EmailMissionRequest):
    try:
        evaluation_result = evaluate_mission_email(request.mission_id, request.user_email)
        save_evaluate_log(request.mission_id, request.user_email, evaluation_result) # 로그 저장 (임시)
        return evaluation_result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {e}")
