from fastapi import APIRouter, HTTPException
from app.schemas.test_model import TestRequest, AnswerRequest
from app.services.eval_document_v1 import eval_document_v1
from app.services.evaluate_doc_v2 import evaluate_doc_v2
from app.services._tmp_save_evaluate_log import save_evaluate_log


router = APIRouter()

@router.get("/")
def test():
    return {"response": "Hello, World!!"}
