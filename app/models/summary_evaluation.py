from typing import List

from pydantic import BaseModel, Field

class EvaluationItem(BaseModel):
    item: str = Field(..., description="평가 항목명 (예: 명확성, 완전성 등)")
    score: int = Field(..., ge=0, le=100, description="해당 항목의 점수 (0~100점)")

class SummaryEvaluation(BaseModel):
    evaluations: List[EvaluationItem]
    summary: str