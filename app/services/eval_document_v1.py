from app.core.openai_client import ask_gpt
from typing import TYPE_CHECKING
from app.models.DocumentEvaluation import DocumentEvaluation
from app.rubrics import get_rubric
from app.utils.rubric_manager.prompt_converter import convert_criteria_to_prompt_string

if TYPE_CHECKING:
    from pydantic import BaseModel

def eval_document_v1(
        model: str="gpt-4o",
        user_prompt: str = None,
        document_type: str=None,

) -> "BaseModel":

    rubric = get_rubric(document_type)
    rubric_prompt = convert_criteria_to_prompt_string(rubric.base_criteria)

    developer_prompt = build_evaluation_prompt(rubric_prompt)

    return ask_gpt(response_model=DocumentEvaluation,
            model=model,
            user_prompt=user_prompt,
            developer_prompt=developer_prompt,
            )

def build_evaluation_prompt(rubric_markdown: str) -> str:
    """루브릭 표를 주입할 수 있는 프롬프트 템플릿"""
    return f"""
    당신은 문서 품질을 평가하는 전문가입니다.
    입력으로 주어지는 문서를 아래 루브릭 기준표에 따라 평가하세요.

    ---

    ## 📘 평가 기준표 (루브릭)
    {rubric_markdown}

    ---

    ## 🧩 평가 방식

    1. 각 **소항목**을 조건 충족 여부에 따라 0~해당 항목 배점으로 채점하세요.  
    2. 같은 **대항목**에 속한 소항목 점수를 합산하여 **대항목별 총점**을 계산합니다.  
    3. 모든 대항목 점수를 합산하여 **총점(100점 만점)**으로 환산합니다.  
       - 예: (대항목별 점수 합 ÷ 해당 항목 총배점) × 항목 가중치  
    4. 총점을 기준으로 **A~F 등급**을 결정합니다.

    | 등급 | 점수 | 의미 | 품질 수준 |
    |------|------|------|-----------|
    | A+ | 95~100 | 탁월함 | 즉시 배포 가능 |
    | A  | 90~94  | 우수함 | 전문가 수준 완성도 |
    | B+ | 85~89  | 양호함 | 기본 이상 품질 |
    | B  | 80~84  | 적정함 | 업무 기준 충족 |
    | C  | 70~79  | 보통 | 기본 요건 충족 |
    | D  | 60~69  | 미흡함 | 기초 수준 |
    | F  | <60 | 불합격 | 품질 기준 미달 |

    ---

    ## 🧾 출력 요구사항 (BaseModel 준수)

    출력은 아래 JSON 스키마 형식으로 작성합니다.

    ```json
    {{
      "evaluations": [ 
        {{"item": "문서 구조·형식", "score": 18, "comment": "표·그림 캡션 일관성 부족"}},
        {{"item": "명료성·가독성", "score": 9, "comment": "전문용어 일부 설명 보완 필요"}}
      ],
      "total_score": 89,
      "grade": "B+",
      "suggestions": [
        "Executive Summary 섹션에 150~250자 핵심 요약문 추가",
        "본문 내 도표·시각자료를 실제 삽입하여 캡션과 참조 일치 확보",
        "추진 계획에 담당자와 구체 일정을 명시해 실행력 강화"
      ],
      "word_feedbacks": [
        {{"word": "평가 편향", "reason": "모호한 개념", "suggestion": "학습 데이터 내 편향 유형 명시"}},
        {{"word": "API 공개", "reason": "구체적 범위 불분명", "suggestion": "REST API(결과 자동 배포) 등 구체 명시"}}
      ]
    }}

  "evaluations": [ 
    {{"item": "명확성", "score": 4, "comment": ""}}, 
    {{"item": "완전성", "score": 5, "comment": "모든 기능 포함"}}
  ],
  "total_score": 33,
  "grade": "F",
  "suggestions": [
    "영향도 섹션에 시스템 영향 설명 보강",
    "관련 PR과 이슈 링크를 추가",
    "불필요하게 긴 문장은 단축"
  ],
  "word_feedbacks": [
    {{"word": "보안 강화", "reason": "추상적 표현", "suggestion": "비밀번호 암호화 알고리즘 변경으로 명시"}}
  ]
}}
"""