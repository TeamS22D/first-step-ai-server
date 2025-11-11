from fastapi import APIRouter, HTTPException
from app.schemas.test_model import TestRequest
from app.services.eval_document_v1 import eval_document_v1


router = APIRouter()

@router.get("/")
def test():
    return {"response": "Hello, World!!"}

@router.post("/evaluate")
async def test2(item: TestRequest):
    try:
        result = eval_document_v1(user_prompt=item.content, document_type=item.id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return result