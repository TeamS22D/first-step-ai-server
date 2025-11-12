from typing import List, Optional
from pydantic import BaseModel, Field


class EvaluationItem(BaseModel):
    item: str = Field(..., description="평가 항목명 (예: 명확성, 완전성 등)")
    score: int = Field(..., ge=0, le=100, description="해당 항목의 점수 (0~100점)")
    comment: str = Field(..., description="해당 항목에 대한 간단한 평가 코멘트")


class WordFeedback(BaseModel):
    word: str = Field(..., description="문서 내 특정 단어나 구절")
    reason: str = Field(..., description="이 단어/표현에 대한 피드백 이유 (불명확, 중복, 누락 등)")
    suggestion: str = Field(..., description="개선 제안 또는 대체 표현")


class MissionEvaluation(BaseModel):
    section: str = Field(..., description="미션 대항목명 (예: 문서 기본 정보, 주요 변경 사항 등)")
    missing_fields: List[str] = Field(..., description="누락된 필드 목록 (예: ['작성자', '버전'])")
    comment: Optional[str] = Field(None, description="누락 또는 오류 관련 요약 코멘트")


class DocumentEvaluation(BaseModel):
    """문서 품질 및 미션 충족도 통합 평가 모델"""
    evaluations: List[EvaluationItem] = Field(..., description="루브릭 항목별 평가 결과 목록")
    mission_evaluation: Optional[List[MissionEvaluation]] = Field(
        None, description="미션 기준 항목 누락 또는 오류 평가 결과"
    )
    total_score: int = Field(..., description="총점 (모든 항목 및 미션 평가 합산 점수)")
    grade: str = Field(..., description="등급 (A+, A, B+, B, C, D, F 등)")
    suggestions: List[str] = Field(..., description="문서 전반에 대한 개선 제안 목록 (3~5개)")
    word_feedbacks: List[WordFeedback] = Field(..., description="단어 단위 피드백 목록")
