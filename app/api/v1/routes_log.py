from fastapi import APIRouter, HTTPException
from app.schemas.test_model import TestRequest, AnswerRequest
from app.services._tmp_save_evaluate_log import get_all_evaluate_log


router = APIRouter()


@router.get("/log")
async def get_log():
    return get_all_evaluate_log()