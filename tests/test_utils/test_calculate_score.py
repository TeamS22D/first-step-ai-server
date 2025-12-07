from app.models.DocumentEvaluation import DocumentEvaluation, EvaluationItem, FeedBack
from app.utils import calculate_score
from app.utils.calculate_score import calculate_basic_score, parse_scores
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

def test_parse_scores():
    print("\n\n test_parse_scores")
    doc_eval = DocumentEvaluation(
        evaluations=[
            EvaluationItem(
                item="Structure & Logic",
                score=85,
                feedback=FeedBack(
                    good_points="문서의 기본 틀과 논리적 흐름이 잘 잡혀 있음",
                    improvement_points="중간 제목 일부가 조금 모호함",
                    suggestion_points="항목 간 연결 문장을 추가하면 더 자연스러움"
                )
            ),
            EvaluationItem(
                item="Clarity & Expression",
                score=90,
                feedback=FeedBack(
                    good_points="표현이 명확하고 이해하기 쉬움",
                    improvement_points="일부 전문 용어에 대한 간단한 설명 추가 필요",
                    suggestion_points="중요 개념 강조를 위해 굵은 글씨 또는 리스트 활용"
                )
            ),
            EvaluationItem(
                item="Completeness & Accuracy",
                score=80,
                feedback=FeedBack(
                    good_points="필수 항목 대부분 포함됨",
                    improvement_points="예시나 수치 근거가 부족한 부분 존재",
                    suggestion_points="참조 링크 또는 데이터 표 첨부"
                )
            )
        ],
        total_score=0,
        grade="B+",
        general_feedback="전반적으로 문서가 잘 작성되었으며, 일부 세부 내용과 근거를 보완하면 우수 수준 도달 가능"
    )

    print(parse_scores(doc_eval))