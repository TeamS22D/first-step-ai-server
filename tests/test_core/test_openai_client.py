import pytest
from pydantic import BaseModel, Field
from typing import List
from app.core.openai_client import ask_gpt, ask_gpt2
from app.core.openai_client import client
from app.models.DocumentEvaluation import DocumentEvaluation
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

def test_ask_gpt2():

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

    pprint(ask_gpt2(response_model=ReleaseNoteEvaluation, model="gpt-5",
                  user_prompt=user_prompt,
                  developer_prompt=developer_prompt).__dict__)

def test_rubric():
    developer_prompt = """
# GPT-4o Developer Prompt — Document Evaluation

You are an expert document quality evaluator.  
Your task is to assess the given document according to the rubric provided below  
and return results **strictly following the JSON schema (DocumentEvaluation)**.

---

## 🧾 Evaluation Rules (Rubric Summary)

Each major category and sub-criterion should be evaluated with a **score from 1 to 5**  
and a **brief comment**.  
After individual evaluations, calculate:
- `total_score`: the sum of all sub-scores (max 200 points)
- `grade`: overall document grade (A, B, C, D, E, or F)
- `suggestions`: three concise improvement proposals
- `word_feedbacks`: 5–10 word-level feedback entries for unclear or weak expressions

**Grading Scale**  
A ≥ 180, B ≥ 160, C ≥ 130, D ≥ 100, E ≥ 70, F < 70

---

## 🧠 Evaluation Categories (Summary Only)

### 1. Document Structure & Format (20 pts)
- File naming rule compliance  
- Section hierarchy & logical order  
- Visual consistency (tables, bullets, emphasis)  
- Paragraph length & alignment  
- Captions and figure labels  
- Page layout & margins consistency

### 2. Purpose & Core Content (15 pts)
- Clear reporting purpose  
- Executive summary completeness  
- Emphasis on key results (KPIs)  
- Alignment between title and main topic

### 3. Completeness & Logic (20 pts)
- Required elements included  
- No missing data or fields  
- Logical progression (Background → Problem → Solution → Result)  
- Cause-effect relationships clearly stated  
- Conclusion or next-step section present

### 4. Specificity & Accuracy (15 pts)
- Use of quantitative metrics (%, version, duration)  
- Supporting evidence (tables, logs, references)  
- Objective tone and measurable claims  
- Absence of vague or ambiguous expressions

### 5. Clarity & Readability (10 pts)
- Appropriate sentence length (≤ 20 words average)  
- Consistent terminology  
- Concise sentence structure  
- Explanation of abbreviations or technical terms

### 6. Feasibility (10 pts)
- Actionable plans with schedule and owner  
- Risk/limitation statements  
- Realistic improvement roadmap

### 7. Tone & Style (10 pts)
- Neutral, professional tone  
- No first-person expressions  
- Proper closing or acknowledgment  
- Correct spelling and grammar  
- Consistent tense and writing style  
- Author and department signature present

### 8. Data Quality (10 pts)
- Version history tracking  
- Reference links to related docs  
- Visual material quality  
- Data visualization presence  
- Well-organized appendices

---

## 🧩 Evaluation Output Requirements

Return the result **strictly** in this JSON format:

```json
{
  "evaluations": [
    {"item": "Clarity", "score": 4, "comment": "Terminology is clear but some sentences are long"},
    {"item": "Completeness", "score": 5, "comment": "All required sections are included"}
  ],
  "total_score": 165,
  "grade": "B",
  "suggestions": [
    "Add more detail to the Executive Summary.",
    "Include specific evidence or data references.",
    "Shorten sentences exceeding 25 words."
  ],
  "word_feedbacks": [
    {
      "word": "improvement rate",
      "reason": "ambiguous phrasing",
      "suggestion": "specify quantitative increase, e.g., +12%"
    }
  ]
}
```

**Rules**
- Output must be **valid JSON** (no markdown, comments, or explanations).  
- All keys must exactly match the schema.  
- Keep comments concise (max 15 words).  
- Be objective and analytical; do not add personal opinions.

---

## 📘 Output Format Schema

```python
class DocumentEvaluation(BaseModel):
    evaluations: List[Dict[str, Union[str, int]]]
    total_score: int
    grade: str
    suggestions: List[str]
    word_feedbacks: List[Dict[str, str]]
```

---
### 🌐 Language Rule
All evaluation comments, suggestions, and feedbacks **must be written in Korean**.  
The output structure and JSON keys must remain in English.

"""
    user_prompt = """
    # REPORT_AI_문서품질평가모델_2025-11-04_v1.0  
    **문서 제목:** 문서 품질 자동평가 모델 개발 결과 보고서  
    **작성자:** AI문서평가팀 (Data Lab 1팀)  
    **작성일:** 2025-11-04  
    **버전:** v1.0  

    ---

    ## Executive Summary (요약)


    ---

    ## 1. 개요
    - **목적:** 사내 보고 문서의 품질 편차를 최소화하기 위한 자동 평가 모델 개발  
    - **배경:** 부서별 문서 형식 불일치로 평가 일관성 저하  
    - **목표:** 문서 품질을 **정량화(100점 만점)** 하여 자동 평가 가능하도록 시스템화  

    ---

    ## 2. 주요 성과

    | 구분 | 평가 항목 | 지표 | 개선율 |
    |------|------------|------|--------|
    | 모델 정확도 | 평가 점수 동일함 | 0.92 → 0.96 | ▲4.3% |
    | 처리 효율 | 문서당 평가 속도 | 7.2초 → 3.8초 | ▲-47% |
    | 사용자 만족도 | 파일명·서식 자동 교정 | 72% → 89% | ▲17% |

    **표 1. 문서 품질 평가 모델 성능 요약 (출처: 내부 테스트 로그)**  

    ---

    ## 3. 문제 정의
    기존 문서 품질 점검은 **사람의 주관적 판단**에 의존했습니다.  
    이에 따라 동일 문서라도 부서 간 점수 편차가 평균 ±12점 발생했고,  
    ‘목적·핵심성’ 항목 누락률이 **18%**에 달했습니다.  
    이로 인해 보고서 신뢰성이 떨어지고 피드백 소요 시간이 길어졌습니다.

    ---

    ## 4. 추진 내용

    ### 4.1 시스템 구조
    - **입력 계층:** PDF, DOCX, MD 등 다양한 문서 포맷 수집  
    - **분석 계층:**  
      - Regex 기반 형식 분석 (`파일명`, `목차`, `캡션`)  
      - NLP 기반 문장 분석 (`명료성`, `객관성`, `논리 흐름`)  
    - **평가 계층:** 항목별 가중치 계산 및 점수 산출  
    - **출력 계층:** JSON·HTML 형태의 리포트 생성  

    **그림 1. 문서 품질 평가 시스템 아키텍처 (출처: 내부 개발 문서)**  

    ---

    ### 4.2 기술 구성
    | 모듈 | 기술 | 기능 |
    |-------|-------|------|
    | Text Analyzer | Python + spaCy | 문장 길이, 주어·서술 분석 |
    | Format Checker | Regex Engine | 제목/파일명 규칙 검증 |
    | Logic Verifier | BERT fine-tune | 논리적 전개 및 인과관계 검출 |
    | Visual Parser | BeautifulSoup | 표·캡션·레이아웃 분석 |

    ---

    ## 5. 문제 해결 및 결과

    - **논리성 향상:** "배경→문제→해결→결과" 구조 감지 정확도 **93%**  
    - **가독성 향상:** 평균 문장 길이 **18.4어절** → 목표 범위(≤20어절) 만족  
    - **형식 일관성:** 제목·파일명 규칙 일치율 **98%**  
    - **객관적 표현 비율:** 감정 표현 감축률 **83%**

    ---

    ## 6. 리스크 및 한계

    | 구분 | 내용 | 대응방안 |
    |------|------|-----------|
    | 데이터 다양성 | 특정 형식(PDF)에 편중 | 텍스트 추출 모듈 범위 확장 |
    | 맞춤법 검사 | 비표준어 처리 한계 | 사용자 사전 기능 추가 |
    | 평가 편향 | 가중치 학습 데이터 불균형 | 샘플 균등화 및 검증 데이터 보강 |

    ---

    ## 7. 향후 계획
    1. **모델 확장:** 한글·영문를 합친 문서 자동 평가 기능 추가  
    2. **API 공개:** 내부 시스템과 연동 가능한 기능 제공  
    3. **자동 교정:** 오탈자 및 문장 구조 실시간 수정 기능 개발  
    4. **시각화 강화:** 리포트 내 차트/그래프 시각화 자동 생성  

    ---

    ## 8. 결론
    본 프로젝트를 통해 문서 품질 관리의 **객관화 및 자동화 기반**이 마련되었습니다.  
    시스템 적용 후 평균 평가 시간이 -47% 단축되었으며, 부서 간 점수 편차도 ±12점 → ±3점으로 감소했습니다.  
    추후 모델 성장을 통해 문서 평가 신뢰도를 98% 이상으로 향상시킬 예정입니다.  

    ---

    ## 부록
    - **[A] 테스트 로그 샘플 (첨부파일)**  
    - **[B] 주요 규칙 목록 (파일명, 목차, 용어사전)**  
    - **[C] 시각자료 원본 (캡션 포함 이미지)**  

    ---

    ## 감사의 말씀
    본 프로젝트는 AI문서평가팀과 품질혁신실의 협업으로 수행되었습니다.  
    검토 및 피드백에 협조해주신 관계자분들께 깊이 감사드립니다.

    ---

    ## 메타데이터
    - **Version:** v1.0  
    - **Last Modified:** 2025-11-04  
    - **Reference:** [사내 표준문서규정 v2.1](http://intranet/docs/standard21)  
    """

    pprint(ask_gpt(
        user_prompt=user_prompt,
        developer_prompt=developer_prompt,
        model="gpt-4o",
        response_model=DocumentEvaluation,).__dict__
           )

def test_ask_gpt_using_file():

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

    file_id = "file-6pYQkmJ7cJRLfH4UDsP74L"

    file_list = [ {"file_id": file_id } ]

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
업로드된 루브릭 파일을 참고해주세요.

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
                    developer_prompt=developer_prompt,
                   ).__dict__)

