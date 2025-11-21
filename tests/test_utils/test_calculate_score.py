from app.utils import calculate_score
from app.utils.calculate_score import calculate_basic_score
import pytest

def test_calculate_document():
    print("\n\n calculate_document")

    score_input = {
        "basic_rubric": {
            "문서 구조·형식": 20,
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
    total_score = calculate_score("document", "release_note", score_input)
    assert total_score == 100

def test_calculate_email():
    print("\n\n calculate_email")

    score_input = {
        "basic_rubric": {
            "구조·형식": 20,
            "목적·핵심성": 20,
            "완결성": 20,
            "명료성·가독성": 15,
            "근거·신뢰성": 10,
            "실행가능성": 10,
            "어조·매너": 10,
            "보안·기밀성": 5
        },
        "special_rubric": {
            "진행률/달성도 정량 표현": 5,
            "이슈 및 리스크 보고": 5,
            "이전 보고 대비 변경사항": 5,
            "KPI/메트릭 추적": 5,
            "우선순위 표시": 5
        }
    }
    total_score = calculate_score("email", "보고형", score_input)
    assert total_score == 100

def test_calculate_basic_rubric():
    print("\n\n calculate_basic_rubric")

    score_input = {
        "구조·논리성": 20,
        "목적 적합성": 100,
        "내용 완성도": 100,
        "실행 가능성": 100,
        "전문성·톤앤매너": 100
    }
    score = calculate_basic_score("document_v2", "project_report", score_input)

    assert score == 100

def test_calculate_test():
    print("\n\n calculate_test")

    score_input = {
        "구조·논리성": 60,
        "목적 적합성": 60,
        "내용 완성도": 50,
        "실행 가능성": 30,
        "전문성·톤앤매너": 5
    }

    score = calculate_basic_score("document_v2", "project_report", score_input)

    print(score)