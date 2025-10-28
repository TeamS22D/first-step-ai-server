import pytest
from pydantic import BaseModel, Field
from typing import List
from app.core.openai_client import ask_gpt
from pprint import pprint



def test_ask_gpt():

    class EvaluationItem(BaseModel):
        item: str = Field(..., description="평가 항목명 (예: 명확성, 완전성 등)")
        score: int = Field(..., ge=1, le=5, description="해당 항목의 점수 (1~5점)")
        comment: str = Field(..., description="해당 항목에 대한 간단한 평가 코멘트")

    class WordFeedback(BaseModel):
        word: str = Field(..., description="문서 내 특정 단어나 구절")
        reason: str = Field(..., description="이 단어/표현에 대한 피드백 이유 (불명확, 중복, 누락 등)")
        suggestion: str = Field(..., description="개선 제안 또는 대체 표현")

    class ReleaseNoteEvaluation(BaseModel):
        evaluations: List[EvaluationItem] = Field(..., description="항목별 평가 결과 목록")
        total_score: int = Field(..., description="총점 (모든 항목 점수의 합계)")
        grade: str = Field(..., description="등급 (A, B, C, D, F 중 하나)")
        suggestions: List[str] = Field(..., description="문서 전체 수준의 개선 제안 3가지")
        word_feedbacks: List[WordFeedback] = Field(..., description="문서 내 단어 단위 피드백 목록")

    user_prompt = """
# Release Note - v2.3.0 (2025-10-20)

## 주요 변경사항
- 사용자 로그인 세션 유지 로직 개선
- 비밀번호 초기화 API 보안 강화

## 버그 수정
- Safari 브라우저에서 이미지 업로드 실패 이슈 해결
- 알림 설정 저장 시 null 예외 처리

## 주의사항
- 로그인 토큰 정책 변경으로 인해 기존 세션이 만료됩니다.

## 배포 정보
- 배포 일시: 2025-10-20 18:00
- 배포 환경: production
- 담당자: SEED

## 참고
- 관련 PR: [#132](https://github.com/seed/app/pull/132)
"""

    #TODO: 루브릭을 따로 분류
    #TODO: 문서 종류 결정, 프롬프트 확인
    #TODO: 루브릭 평가
    developer_prompt ="""
당신은 릴리즈 문서 품질을 평가하는 전문가입니다.
입력으로 주어지는 마크다운(Markdown) 형식의 릴리즈 노트를 다음 평가 기준에 따라 분석하고, 
각 항목별 점수(1~5점), 평가 코멘트, 총점, 등급, 개선 제안을 생성하세요.

---

## 📘 릴리즈 문서 평가 기준표

| 번호 | 항목명 | 평가 내용 | 점검 포인트 | 배점 |
|------|---------|-------------|---------------|------|
| 1 | 명확성 (Clarity) | 변경사항이 명확하고 이해하기 쉬운가 | 문장 명료성, 용어 일관성, 독자 고려 여부 | 1~5 |
| 2 | 완전성 (Completeness) | 모든 기능/수정사항이 누락 없이 포함되었는가 | 주요 기능, 버그, 개선사항, 비고 포함 | 1~5 |
| 3 | 구조 및 가독성 (Structure & Readability) | 문서 구조가 일관되고 읽기 쉬운가 | 제목/소제목 체계, 표·리스트 활용 | 1~5 |
| 4 | 정확성 (Accuracy) | 실제 배포 내용과 일치하는가 | 버전, 기능 동작, 영향 범위 검증 | 1~5 |
| 5 | 영향도 및 주의사항 (Impact & Notice) | 사용자나 시스템에 미치는 영향이 명시되었는가 | Breaking change, 마이그레이션 가이드 | 1~5 |
| 6 | 배포 정보 (Deployment Info) | 배포 일시, 버전, 환경이 명시되었는가 | 버전명, 배포일자, 환경(dev/stg/prod) | 1~5 |
| 7 | 형식 일관성 (Formatting Consistency) | 문서 형식과 규칙을 준수했는가 | 템플릿 일관성, 표기 규칙 준수 | 1~5 |
| 8 | 부가 정보 (Additional Info) | 관련 참고 정보가 충분한가 | JIRA/Git 링크, 관련 문서, PR | 1~5 |

---

## 📊 점수 및 등급 기준

| 총점 범위 | 등급 | 평가 설명 |
|------------|------|------------|
| 36~40점 | A (우수) | 문서 완성도 매우 높음. 실무 활용 가능 |
| 31~35점 | B (양호) | 품질 양호. 일부 개선 필요 |
| 26~30점 | C (보통) | 주요 내용 포함. 형식/명확성 개선 필요 |
| 16~25점 | D (미흡) | 정보 누락 또는 불명확 |
| 0~15점 | F (불량) | 기준 미달, 재작성 필요 |

---

## 🧩 평가 방식

1. 입력된 릴리즈 노트를 위 기준에 따라 평가한다.  
2. 각 항목별로 점수(1~5)와 코멘트를 작성한다.  
3. 총점을 계산하고 A~F 등급을 결정한다.  
4. 문서 전체 수준의 개선 제안 3가지를 작성한다.  
5. 문서 내에서 개선이 필요한 단어나 구절을 찾아  
   - `word`: 해당 단어 또는 구절  
   - `reason`: 문제 원인(예: 모호함, 중복, 문법 오류 등)  
   - `suggestion`: 더 나은 표현이나 수정 제안  
   형식으로 5~10개 정도 작성한다.

---

## 🧾 출력 형식 (반드시 아래 포맷을 유지)

## 🧾 출력 형식 (BaseModel 구조 준수)

모델은 아래 `ReleaseNoteEvaluation` 스키마에 맞는 JSON 형태로 응답해야 한다.

```json
{
  "evaluations": [
    {"item": "명확성", "score": 4, "comment": "용어 명확하나 일부 문장 길음"},
    {"item": "완전성", "score": 5, "comment": "모든 기능 포함"},
    ...
  ],
  "total_score": 33,
  "grade": "B",
  "suggestions": [
    "영향도 섹션에 시스템 영향 설명 보강",
    "관련 PR과 이슈 링크를 추가",
    "불필요하게 긴 문장은 단축"
  ],
  "word_feedbacks": [
    {"word": "세션 유지", "reason": "의미가 모호함", "suggestion": "세션 지속 시간으로 구체화"},
    {"word": "보안 강화", "reason": "추상적 표현", "suggestion": "비밀번호 암호화 알고리즘 변경으로 명시"},
    {"word": "null 예외 처리", "reason": "기술적 표현 불명확", "suggestion": "NullPointerException 처리로 구체화"}
  ]
}


---

## 🧱 입력 예시
# Release Note - v2.3.0 (2025-10-20)

## 주요 변경사항
- 사용자 로그인 세션 유지 로직 개선
- 비밀번호 초기화 API 보안 강화

## 버그 수정
- Safari 브라우저에서 이미지 업로드 실패 이슈 해결
- 알림 설정 저장 시 null 예외 처리

## 주의사항
- 로그인 토큰 정책 변경으로 인해 기존 세션이 만료됩니다.

## 배포 정보
- 배포 일시: 2025-10-20 18:00
- 배포 환경: production
- 담당자: SEED

## 참고
- 관련 PR: [#132](https://github.com/seed/app/pull/132)

---

## 🧮 요청
입력으로 주어진 릴리즈 노트를 평가하고,
위 ReleaseNoteEvaluation 모델 구조에 맞는 JSON 형태로 출력하라.
"""

    pprint(ask_gpt(response_model=ReleaseNoteEvaluation, model="gpt-5",
                  user_prompt=user_prompt,
                  developer_prompt=developer_prompt).__dict__)