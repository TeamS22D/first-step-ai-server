from app.core.openai_client import ask_gpt
from typing import TYPE_CHECKING
from app.models.DocumentEvaluation import DocumentEvaluation
from app.rubrics import get_rubric
from app.utils.prompt_converter import convert_criteria_to_prompt_string

if TYPE_CHECKING:
    from pydantic import BaseModel

mission_list = {"id_1": {
    "문서 기본 정보": {
        "제목": {
            "작성 내용 / 예시": "FirstStep Platform - 인증 API 릴리즈 노트 v2.0.0",
            "작성 팁": "시스템명 + 모듈명 + 버전명 형식 유지"
        },
        "작성일": {
            "작성 내용 / 예시": "2025-11-11",
            "작성 팁": "문서 작성일 기준(YYYY-MM-DD)"
        },
        "작성자": {
            "작성 내용 / 예시": "홍길동 / Backend Team",
            "작성 팁": "개인 이름과 부서 함께 기재"
        },
        "버전": {
            "작성 내용 / 예시": "v2.0.0",
            "작성 팁": "Semantic Versioning 규칙 적용"
        },
        "릴리즈 타입": {
            "작성 내용 / 예시": "Major / Minor / Patch",
            "작성 팁": "변경 범위에 따라 선택"
        }
    },
    "1. 개요": {
        "요약": {
            "작성 내용 / 예시": "토큰 포맷 변경 및 v2 전환",
            "작성 팁": "50자 이내 핵심 변경 요약"
        }
    },
    "2. 버전 정보": {
        "이전 버전": {
            "작성 내용 / 예시": "v1.2.0",
            "작성 팁": "바로 전 버전 명시"
        },
        "현재 버전": {
            "작성 내용 / 예시": "v2.0.0",
            "작성 팁": "현재 릴리즈 버전"
        },
        "버전 규칙": {
            "작성 내용 / 예시": "Semantic Versioning (MAJOR.MINOR.PATCH)",
            "작성 팁": "고정 문구"
        },
        "배포 대상": {
            "작성 내용 / 예시": "Backend API 서버",
            "작성 팁": "영향받는 시스템 또는 모듈"
        }
    },
    "3. 주요 변경 사항": {
        "구분": {
            "작성 내용 / 예시": "보안, 수정, 기타 등",
            "작성 팁": "표준 카테고리 선택"
        },
        "항목": {
            "작성 내용 / 예시": "토큰 포맷(PASETO), Base URL 변경 등",
            "작성 팁": "변경된 기능명"
        },
        "변경 내용": {
            "작성 내용 / 예시": "JWT → PASETO 서명 방식 변경",
            "작성 팁": "한 줄 요약"
        },
        "영향도": {
            "작성 내용 / 예시": "낮음 / 중간 / 높음",
            "작성 팁": "영향 수준 판단"
        }
    },
    "4. Breaking Changes": {
        "설명": {
            "작성 내용 / 예시": "v1 대비 필드명 변경(user.id → user.user_id)",
            "작성 팁": "하위 호환성 문제를 구체적으로"
        },
        "JSON Before": {
            "작성 내용 / 예시": '{ "token": "eyJ...", "user": {"id": 1, "email": "a@b.com"} }',
            "작성 팁": "이전 버전 예시"
        },
        "JSON After": {
            "작성 내용 / 예시": '{ "token": "v2.local...", "token_type": "PASETO", "user": {"user_id": 1, "email": "a@b.com"} }',
            "작성 팁": "새 버전 예시"
        },
        "클라이언트 영향": {
            "작성 내용 / 예시": "응답 파서 수정 필요, 토큰 검증 로직 교체",
            "작성 팁": "개발 영향 명시"
        },
        "수정 필요 항목": {
            "작성 내용 / 예시": "user.id 필드 참조, 토큰 검증 라이브러리",
            "작성 팁": "수정해야 하는 구체 항목"
        }
    },
    "5. 마이그레이션 가이드": {
        "단계별 지침": {
            "작성 내용 / 예시": "1) /v2 엔드포인트로 교체, 2) token_type 검사 추가",
            "작성 팁": "실행 순서 중심으로 작성"
        },
        "예상 소요 시간": {
            "작성 내용 / 예시": "3~5일",
            "작성 팁": "팀 기준 예상 작업 기간"
        },
        "추가 고려사항": {
            "작성 내용 / 예시": "호환 모드 유지, QA 병행",
            "작성 팁": "리스크나 주의점"
        }
    },
    "6. Known Issues": {
        "ID": {
            "작성 내용 / 예시": "#FS-07",
            "작성 팁": "내부 트래킹용"
        },
        "구분": {
            "작성 내용 / 예시": "호환성, 라이브러리, 환경 등",
            "작성 팁": "문제 유형"
        },
        "설명": {
            "작성 내용 / 예시": "일부 PASETO 라이브러리의 서명 포맷 불일치",
            "작성 팁": "원인 요약"
        },
        "우회 방안": {
            "작성 내용 / 예시": "서버측 임시 호환 모드 사용",
            "작성 팁": "임시 해결책"
        }
    },
    "7. 향후 계획": {
        "버전": {
            "작성 내용 / 예시": "v1 폐기, SDK v2.1 등",
            "작성 팁": "후속 릴리즈 버전"
        },
        "예정 기능": {
            "작성 내용 / 예시": "v1 엔드포인트 폐기, SDK 업데이트",
            "작성 팁": "향후 변경 내용"
        },
        "예상 일정": {
            "작성 내용 / 예시": "6개월 후 (2026-05 예정)",
            "작성 팁": "일정 명확히"
        }
    },
    "8. 참고 정보": {
        "검토자": {
            "작성 내용 / 예시": "이수연 / QA Team",
            "작성 팁": "문서 리뷰 담당자"
        },
        "참고 문서": {
            "작성 내용 / 예시": "PASETO 공식 문서, v2 API 명세 링크",
            "작성 팁": "관련 문서 URL 또는 명칭"
        }
    }
}}

def evaluate_doc_v2(
        model: str="gpt-4o",
        user_prompt: str = None,
        document_type: str=None,
        mission_id: str=None,
) -> "BaseModel":
    """
    v2에서는 사용자의 문서를 단순히 평가만 할 뿐만 아니라 문제에서 주어진 조건을 만족하는지 까지 평가합니다.

    """
    mission = mission_list.get(mission_id)

    rubric = get_rubric(document_type)
    rubric_prompt = convert_criteria_to_prompt_string(rubric.base_criteria)

    developer_prompt = build_evaluation_prompt(rubric_prompt)

    return ask_gpt(response_model=DocumentEvaluation,
            model=model,
            user_prompt=user_prompt,
            developer_prompt=developer_prompt,
            )


def dict_to_markdown(d: dict, level: int = 2) -> str:
    """중첩 dict를 Markdown 리스트/테이블 형식으로 변환"""
    md = ""
    indent = "  " * (level - 2)
    for k, v in d.items():
        if isinstance(v, dict):
            md += f"{indent}- **{k}**\n"
            md += dict_to_markdown(v, level + 1)
        else:
            md += f"{indent}- **{k}**: {v['작성 내용 / 예시']} ({v.get('작성 팁', '')})\n"
    return md


def build_evaluation_prompt(rubric_markdown: str, doc_fields: dict = None) -> str:
    """
    루브릭 표와 문서 필드(dict)를 주입할 수 있는 평가 프롬프트 생성
    - rubric_markdown: 루브릭 표(사용자 작성)
    - doc_fields: 문서 필드 dict (위에서 만든 release_note_fields)
    """
    doc_md = ""
    if doc_fields:
        doc_md = dict_to_markdown(doc_fields)

    return f"""
당신은 문서 품질을 평가하는 전문가입니다.
입력으로 주어지는 문서를 아래 루브릭 기준표와 문서 구조 정보에 따라 평가하세요.

---

## 📘 평가 기준표 (루브릭)
{rubric_markdown}

---

## 📄 문서 구조/필드 정보
{doc_md if doc_md else "없음"}

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
"""

def get_mission(mission_id: str) -> dict:
    return mission_list.get(mission_id)