from typing import Dict

from app.models.DocumentEvaluation import DocumentEvaluation
from app.utils.rubric_manager import rubric_manager

def calculate_basic_score(rubric_name: str, special_type: str = None, user_score: Dict[str, int] = None) -> int:
    basic_rubric = rubric_manager.get_basic_rubric(rubric_name)
    rubric_weights = rubric_manager.get_special_weights(rubric_name, special_type)
    score = 0

    for name, weights in rubric_weights.items():
        score += user_score.get(name, 0)/100 * weights

    return int(score)

def parse_scores(evaluation: DocumentEvaluation) -> Dict[str, int]:
    return {item.item: item.score for item in evaluation.evaluations}

def get_grade(score: int) -> str:
    if score < 60:
        return 'F'
    elif score < 70:
        return 'D'
    elif score < 80:
        return 'C'
    elif score < 85:
        return 'B'
    elif score < 90:
        return 'B+'
    elif score < 95:
        return 'A'
    else:
        return 'A+'

def calculate_score(rubric_name: str, special_type: str = None, score: dict = None) -> int:
    """루브릭을 기반으로 특화 항목에 관한 점수 계산을 합니다."""
    return 0

    basic_rubric = rubric_manager.get_basic_rubric(rubric_name)
    rubric_weights = rubric_manager.get_special_weights(rubric_name, special_type)


    user_basic_scores = score.get("basic_rubric", {})
    user_basic_score = 0
    for weights in rubric_weights:
        user_score = user_basic_scores.get(weights, 0)
        total_score = basic_rubric.get(weights, {}).total_score
        weights = rubric_weights[weights]
        user_basic_score += user_score/total_score * weights

    user_special_scores = score.get("special_rubric", {})
    user_special_score = sum([v for v in user_special_scores.values()])

    #TODO: 가중치 따로 두기
    score = int(user_basic_score / total_basic_score * 70 + user_special_score / total_special_score * 30)

    return score
