from app.core.openai_client import ask_gpt
from typing import TYPE_CHECKING
from app.models.DocumentEvaluation import DocumentEvaluation
from app.rubrics import get_rubric
from app.utils.prompt_converter import convert_criteria_to_prompt_string

if TYPE_CHECKING:
    from pydantic import BaseModel

def eval_document_v1(
        model: str="gpt-4o",
        user_prompt: str = None,
        document_type: str=None,

) -> DocumentEvaluation:
    """ 사용자 맞춤형 문서 평가 결과를 반환합니다.

    """
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
1. 각 항목별로 점수(1~5)와 코멘트를 작성한다.
2. 총점을 계산하고 A~F 등급을 결정한다.
3. 문서 전체 수준의 개선 제안 3가지를 작성한다.
4. 문서 내에서 개선이 필요한 단어나 구절을 찾아
   - `word`: 문제 단어/구절  
   - `reason`: 문제 원인 (모호함, 중복, 문법 오류 등)  
   - `suggestion`: 대체 표현  
   형식으로 5~10개 작성한다.

---

## 🧾 출력 형식 (BaseModel 구조 준수)
모델은 아래 `DocumentEvaluation` 스키마에 맞는 JSON 형태로 응답해야 한다.

```json
{{
  "evaluations": [
    {{"item": "명확성", "score": 4, "comment": "용어 명확하나 일부 문장 길음"}},
    {{"item": "완전성", "score": 5, "comment": "모든 기능 포함"}}
  ],
  "total_score": 33,
  "grade": "B",
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