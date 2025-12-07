from fastapi import APIRouter, HTTPException

from app.models.DocumentEvaluation import EvaluationResult
from app.schemas.test_model import EvaluationRequest
from app.services.evaluate_doc_v3 import evaluate_document

router = APIRouter()

@router.post("/evaluate")
async def test2(request: EvaluationRequest) -> EvaluationResult:
    try:
        result = evaluate_document(**request.model_dump())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return result
