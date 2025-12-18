from fastapi import APIRouter, HTTPException, Depends

from app.models.DocumentEvaluation import EvaluationResult
from app.schemas.test_model import EvaluationRequest
from app.services.evaluate_email_v3 import evaluate_email
from app.core.auth import verify_jwt

router = APIRouter()

@router.post("/evaluate")
async def evaluate_document_router(
        request: EvaluationRequest,
        # payload: dict = Depends(verify_jwt)
) -> EvaluationResult:
    # if payload["iss"] is not "nestJS":
    #     raise HTTPException(status_code=403, detail="Invalid issuer.")
    print(request)
    try:
        result = evaluate_email(**request.model_dump())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return result
