from pydantic import BaseModel, Field
from typing import List

class FeedbackDetail(BaseModel):
    """
    개별 평가 항목에 대한 구체적인 피드백을 담는 모델
    """
    good_points: str = Field(description="이 항목에서 잘한 점에 대한 구체적인 칭찬")
    improvement_points: str = Field(description="이 항목에서 개선이 필요한 부분에 대한 구체적인 지적")
    suggested_fix: str = Field(description="개선점을 보완할 수 있는 구체적인 예시 또는 제안")

class EvaluationItem(BaseModel):
    """
    5대 평가 항목 각각에 대한 평가 결과
    """
    item: str = Field(description="평가 항목 이름 (예: 구조·논리성)")
    score: int = Field(description="해당 항목의 점수 (0점에서 100점 사이)")
    feedback: FeedbackDetail

class EmailEvaluationResult(BaseModel):
    """
    이메일 평가 결과 전체를 담는 최종 모델
    """
    evaluations: List[EvaluationItem] = Field(description="5대 평가 항목 각각에 대한 상세 평가 결과 리스트")
    total_score: int = Field(description="5개 항목의 점수를 평균내어 계산한 최종 총점 (0점에서 100점 사이)")
    grade: str = Field(description="총점에 따라 부여된 등급 (예: Excellent, Good, Needs Improvement)")
    general_feedback: str = Field(description="평가 전반에 대한 종합적인 피드백 및 총평")

