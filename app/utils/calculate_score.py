from app.utils.rubric_manager.manager import RubricManager
from app.utils.rubric_manager import rubric_manager



def calculate_score(rubric_name: str, special_type: str = None, score: dict = None) -> int:
    """루브릭을 기반으로 특화 항목에 관한 점수 계산을 합니다."""

    basic_rubric = rubric_manager.get_basic_rubric(rubric_name)
    rubric_weights = rubric_manager.get_special_weights(rubric_name, special_type)
    special_rubric = rubric_manager.get_special_rubric(rubric_name, special_type)

    user_basic_scores = score.get("basic_rubric", {})
    user_basic_score = 0
    for weights in rubric_weights:
        user_score = user_basic_scores.get(weights, 0)
        total_score = basic_rubric.get(weights, {}).total_score
        weights = rubric_weights[weights]
        user_basic_score += user_score/total_score * weights

    user_special_scores = score.get("special_rubric", {})
    user_special_score = sum([v for v in user_special_scores.values()])

    score = int(user_basic_score * 0.7 + user_special_score)

    return score

if __name__ == "__main__":
    rubric_manager = RubricManager("../rubrics/")
    
    score_input = {
        "basic_rubric": {
            "문서 구조·형식": 16,
            "목적·핵심성": 15,
            "완결성·논리성": 20,
            "구체성·정확성": 15,
            "명료성·가독성": 10,
            "실행가능성": 10,
            "어조·매너": 10
        },
        "special_rubric": {
            "이번 주 대비 진척도": 5,
            "이슈/블로커 명시": 5,
            "다음 주 계획 명확성": 5,
            "KPI/메트릭 추적": 10,
            "우선순위 표시": 5
        }
    }
    #TODO: manager에 total_score 명시
    total_score = calculate_score("document", "release_note", score_input)
    print(total_score)