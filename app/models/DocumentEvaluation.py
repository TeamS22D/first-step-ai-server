from typing import List
from pydantic import BaseModel, Field

class EvaluationItem(BaseModel):
    item: str = Field(..., description="평가 항목명 (예: 명확성, 완전성 등)")
    score: int = Field(..., ge=1, le=5, description="해당 항목의 점수 (1~5점)")
    comment: str = Field(..., description="해당 항목에 대한 간단한 평가 코멘트")

class WordFeedback(BaseModel):
    word: str = Field(..., description="문서 내 특정 단어나 구절")
    reason: str = Field(..., description="이 단어/표현에 대한 피드백 이유 (불명확, 중복, 누락 등)")
    suggestion: str = Field(..., description="개선 제안 또는 대체 표현")

class DocumentEvaluation(BaseModel):
    """문서 평가 공통 모델 (릴리즈노트, 기술설계서 등)"""
    evaluations: List[EvaluationItem] = Field(..., description="항목별 평가 결과 목록")
    total_score: int = Field(..., description="총점 (모든 항목 점수의 합계)")
    grade: str = Field(..., description="등급 (A, B, C, D, F 중 하나)")
    suggestions: List[str] = Field(..., description="문서 전체 수준의 개선 제안 3가지")
    word_feedbacks: List[WordFeedback] = Field(..., description="문서 내 단어 단위 피드백 목록")
