from typing import List, Optional
from pydantic import BaseModel, Field

class FeedBack(BaseModel):
    good_points: str = Field("", description="Good Points"),
    improvement_points: str = Field("", description="Improvement Points"),
    suggested_fix: str = Field("", description="Suggestion Points")

class EvaluationItem(BaseModel):
    item: str = Field(..., description="Category name")
    score: int = Field(..., ge=0, le=100, description="Category Total Score (0~100)")
    feedback: FeedBack = Field(..., description="Category FeedBack")

class DocumentEvaluation(BaseModel):
    """문서 품질 및 미션 충족도 통합 평가 모델"""
    evaluations: List[EvaluationItem] = Field(..., description="Category Evaluations")
    general_feedback: str = Field(..., description="general feedback about category")

class EvaluationResult(BaseModel):
    evaluations: List[EvaluationItem] = Field(..., description="Category Evaluations")
    general_feedback: str = Field(..., description="general feedback about category")
    total_score: int = Field(..., ge=0, le=100)
    grade: str = Field(..., description="Grade")