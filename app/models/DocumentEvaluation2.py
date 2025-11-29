from typing import List, Dict

from pydantic import BaseModel, Field


class RubricScore(BaseModel):
    """개별 루브릭 항목 점수"""
    item: str = Field(..., description="평가 항목명")
    score: int = Field(..., description="획득 점수")
    max_score: int = Field(..., description="만점")
    comment: str = Field(..., description="평가 코멘트")


class WordFeedback(BaseModel):
    """표현 개선 피드백"""
    word: str = Field(description="개선이 필요한 표현")
    reason: str = Field(description="문제가 되는 이유")
    suggestion: str = Field(description="구체적 개선 제안")


class ProjectReportEvaluation(BaseModel):
    """프로젝트 보고서 평가 결과"""

    # 기본 루브릭 점수 (80점)
    basic_rubric: Dict[str, int] = Field(
        default_factory=dict,
        description="기본 문서 품질 루브릭 점수"
    )

    # 프로젝트 특화 루브릭 점수 (20점)
    special_rubric: Dict[str, int] = Field(
        default_factory=dict,
        description="프로젝트 보고서 특화 항목 점수"
    )

    # 총점 및 등급
    total_score: int = Field(default=0, description="총점 (100점 만점)", ge=0, le=100)
    grade: str = Field(default="F", description="등급 (A+, A, B+, B, C, D, F)")

    # 종합 평가
    summary: str = Field(default="", description="전체 평가 요약 (2-4문장)")

    # 개선 제안
    suggestions: List[str] = Field(default_factory=list, description="구체적 개선 제안 리스트")

    # 표현 개선 피드백
    word_feedbacks: List[WordFeedback] = Field(
        default_factory=list,
        description="모호하거나 개선이 필요한 표현 피드백"
    )

    # 초년생을 위한 추가 조언
    strengths: List[str] = Field(default_factory=list, description="잘한 점 3가지")
    priority_improvement: str = Field(default="", description="가장 시급한 개선사항 1가지")
    next_tip: str = Field(default="", description="다음 보고서 작성 팁 1가지")

