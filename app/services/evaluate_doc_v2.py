from app.core.openai_client import ask_gpt
from typing import TYPE_CHECKING, Optional, List
from app.models.DocumentEvaluation import DocumentEvaluation
from app.rubrics import get_rubric
from app.utils.rubric_manager.prompt_converter import convert_criteria_to_prompt_string
from app.models.summary_evaluation import SummaryEvaluation

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
},
    "id_2": {
    "문서 기본 정보": {
        "제목": {
            "작성 내용 / 예시": "FirstStep Platform - 인증 API 릴리즈 노트 v1.1.1",
            "작성 팁": "시스템명 + 모듈명 + 버전명 형식 유지"
        },
        "작성일": {
            "작성 내용 / 예시": "2025-11-12",
            "작성 팁": "문서 작성일 기준(YYYY-MM-DD)"
        },
        "작성자": {
            "작성 내용 / 예시": "홍길동 / Backend Team",
            "작성 팁": "개인 이름과 부서 함께 기재"
        },
        "버전": {
            "작성 내용 / 예시": "v1.1.1",
            "작성 팁": "Semantic Versioning 규칙 적용"
        },
        "릴리즈 타입": {
            "작성 내용 / 예시": "Patch",
            "작성 팁": "변경 범위에 따라 선택"
        }
    },
    "1. 개요": {
        "요약": {
            "작성 내용 / 예시": "토큰 갱신 충돌 핫픽스 및 에러 코드 보정",
            "작성 팁": "50자 이내 핵심 변경 요약"
        }
    },
    "2. 버전 정보": {
        "이전 버전": {
            "작성 내용 / 예시": "v1.1",
            "작성 팁": "바로 전 버전 명시"
        },
        "현재 버전": {
            "작성 내용 / 예시": "v1.1.1",
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
            "작성 내용 / 예시": "수정, 기타",
            "작성 팁": "표준 카테고리 선택"
        },
        "항목": {
            "작성 내용 / 예시": "POST /api/v1/auth/token/refresh 충돌 처리, 에러 코드 409_REFRESH_CONFLICT, 응답 헤더 X-Request-Id",
            "작성 팁": "변경된 기능명 또는 엔드포인트 명시"
        },
        "변경 내용": {
            "작성 내용 / 예시": "동시 갱신 충돌에 낙관적 잠금과 지수 백오프 적용, 일부 500을 409로 보정, 요청 추적을 위한 X-Request-Id 추가",
            "작성 팁": "한 줄 요약"
        },
        "영향도": {
            "작성 내용 / 예시": "중간(충돌 시 재시도 필요), 낮음(헤더 추가)",
            "작성 팁": "영향 수준 판단"
        }
    },
    "4. Breaking Changes": {
        "설명": {
            "작성 내용 / 예시": "없음",
            "작성 팁": "Breaking Changes가 없으면 ‘없음’ 명시"
        },
        "JSON Before": {
            "작성 내용 / 예시": "없음",
            "작성 팁": "하위 호환 유지 시 예시 생략 가능"
        },
        "JSON After": {
            "작성 내용 / 예시": "없음",
            "작성 팁": "하위 호환 유지 시 예시 생략 가능"
        },
        "클라이언트 영향": {
            "작성 내용 / 예시": "409_REFRESH_CONFLICT 처리 및 재시도 로직 필요",
            "작성 팁": "개발 영향 명시"
        },
        "수정 필요 항목": {
            "작성 내용 / 예시": "토큰 갱신 실패 처리 분기(500→409 포함), 재시도 백오프 적용, X-Request-Id 로깅",
            "작성 팁": "수정해야 하는 구체 항목"
        }
    },
    "5. 마이그레이션 가이드": {
        "단계별 지침": {
            "작성 내용 / 예시": "1) 409_REFRESH_CONFLICT 수신 시 지수 백오프(200ms 시작, 최대 3회)로 재시도 추가, 2) 응답 헤더 X-Request-Id를 로그에 포함, 3) 장애 모니터링 대시보드에 409 비율 지표 추가",
            "작성 팁": "실행 순서 중심으로 작성"
        },
        "예상 소요 시간": {
            "작성 내용 / 예시": "0.5~1일",
            "작성 팁": "팀 기준 예상 작업 기간"
        },
        "추가 고려사항": {
            "작성 내용 / 예시": "재시도 시 동시성 폭증 방지(지수 백오프/지터), 서버 레이트 제한과 충돌하지 않도록 최대 3회 제한, 롤백 시 기존 로직 플래그 전환",
            "작성 팁": "리스크나 주의점"
        }
    },
    "6. Known Issues": {
        "ID": {
            "작성 내용 / 예시": "#FS-01",
            "작성 팁": "내부 트래킹용"
        },
        "구분": {
            "작성 내용 / 예시": "성능/지연",
            "작성 팁": "문제 유형"
        },
        "설명": {
            "작성 내용 / 예시": "토큰 저장소 지연 시 간헐적 409 지속 발생 가능",
            "작성 팁": "원인 요약"
        },
        "우회 방안": {
            "작성 내용 / 예시": "최대 3회 지수 백오프 후 재시도, 필요 시 사용자에게 재시도 안내",
            "작성 팁": "임시 해결책"
        }
    },
    "7. 향후 계획": {
        "버전": {
            "작성 내용 / 예시": "v1.2.0",
            "작성 팁": "후속 릴리즈 버전"
        },
        "예정 기능": {
            "작성 내용 / 예시": "OAuth 소셜 로그인 추가(google, apple)",
            "작성 팁": "향후 변경 내용"
        },
        "예상 일정": {
            "작성 내용 / 예시": "다음 분기(예: 2025-12 예정)",
            "작성 팁": "일정 명확히"
        }
    },
    "8. 참고 정보": {
        "검토자": {
            "작성 내용 / 예시": "이수연 / QA Team",
            "작성 팁": "문서 리뷰 담당자"
        },
        "참고 문서": {
            "작성 내용 / 예시": "관련 장애 리포트(#INC-2025-1101), 인증 로그 포맷 문서, 인증 API 스펙(v1)",
            "작성 팁": "관련 문서 URL 또는 명칭"
        }
    }} }



def evaluate_doc_v2(
        model: str="gpt-4o",
        user_prompt: str = None,
        document_type: str=None,
        mission_id: str=None,
) -> "BaseModel":
    """
    v2에서는 사용자의 문서를 단순히 평가만 할 뿐만 아니라 문제에서 주어진 조건을 만족하는지 까지 평가합니다.

    """
    mission = get_mission(mission_id)

    rubric = get_rubric(document_type)
    rubric_prompt = convert_criteria_to_prompt_string(rubric.base_criteria)

    developer_prompt = build_evaluation_prompt(rubric_prompt, mission)

    return ask_gpt(response_model=DocumentEvaluation,
            model=model,
            user_prompt=user_prompt,
            developer_prompt=developer_prompt,
            )

def summarize_eval_v1(
        *,
        user_prompt: str = None,
        rubric_type: str=None,
        mission_id: str=None,
        model: str="gpt-4o",
) -> "BaseModel":
    """
    evaluate_doc_v2에서 문서의 간단한 평가 내용만 생성해주는 서비스 입니다.
    :param user_prompt: 사용자가 작성한 문서
    :param rubric_type: 루브릭 타입
    :param mission_id: 미션 ID
    :param model: 사용할 gpt모델
    :return:
    """
    mission = get_mission(mission_id)

    rubric = get_rubric(rubric_type)
    rubric_prompt = convert_criteria_to_prompt_string(rubric.base_criteria)

    developer_prompt = build_summerize_prompt(rubric=rubric_prompt)

    return ask_gpt(response_model=SummaryEvaluation,
                   model=model,
                   user_prompt=user_prompt,
                   developer_prompt=developer_prompt,
                   )

def build_summerize_prompt(items: Optional[List[str]] = None,
                           rubric: Optional[str] = None) -> str:
    """
    gpt-4o 기준의 간결/고속 문서 평가 프롬프트 생성기.
    - 출력: SummaryEvaluation(BaseModel)에 맞는 JSON만 반환
      {
        "evaluations": [{"item": "...","score": 0}, ...],
        "summary": "..."  // 한국어 2~4문장
      }
    - 점수: 각 항목별 0~100 정수
    - 요약: 짧고 친절한 톤, 전반 강점 + 1~2개 개선 포인트
    """
    default_items = [
        "문서 구조·형식",
        "명료성·가독성",
        "완전성",
        "정확성·일관성",
        "실행 가능성(액셔너블)"
    ]
    items = items or default_items
    items_block = "\n".join(f"- {it}" for it in items)

    return f"""
You are GPT-4o acting as a fast, concise document quality reviewer.
Evaluate quickly and return compact output only.

Task:
- Score each requested item as an integer 0–100.
- Write a short Korean summary (2–4 sentences): friendly-neutral tone, overall strengths + 1–2 concrete improvements. Do not restate long content.
- Prefer the rubric if provided; otherwise use general document quality judgment.
- If information is insufficient, infer conservatively; do not output "N/A".
- Output JSON only with keys: evaluations, summary. No extra keys, no markdown, no commentary.

Scoring guide (for consistency; not to be printed):
95–100 탁월 / 90–94 우수 / 85–89 양호 / 80–84 적정 / 70–79 보통 / 60–69 미흡 / <60 불합격.

Rubric (optional):
{rubric or "없음"}

Return JSON only in this schema (example structure, not a template):
{{
  "evaluations": [
    {{"item": "{items[0]}", "score": 0}}
  ],
  "summary": "간단한 한국어 요약 2~4문장"
}}"""

def build_evaluation_prompt(rubric_markdown: str, mission: dict = None) -> str:
    """
    루브릭 + 미션 항목(문서 작성 템플릿)을 모두 반영한 평가 프롬프트.
    문서 품질뿐 아니라 필수 항목 누락 여부 및 보완 제안까지 포함.
    """

    mission_md = ""
    if mission:
        mission_md += "## 📑 문서 구성 필수 항목 (Mission Checklist)\n"
        for section, fields in mission.items():
            mission_md += f"\n### {section}\n"
            for field, info in fields.items():
                example = info.get("작성 내용 / 예시", "")
                tip = info.get("작성 팁", "")
                mission_md += f"- **{field}**  \n  예시: `{example}`  \n  작성 팁: {tip}\n"
        mission_md += "\n---\n"

    return f"""
당신은 **문서 품질 평가 전문가**입니다.  
입력으로 주어지는 문서를 아래 두 기준에 따라 평가하세요.

1. 📘 **루브릭 기준** — 문서의 품질(명료성, 완전성, 논리성 등)을 정량적으로 평가  


## 📘 루브릭 기준표
{rubric_markdown}

---

{mission_md if mission_md else "⚠️ 미션 항목 없음"}

---

## 🧩 평가 방식

1. 각 **소항목**을 조건 충족 여부에 따라 0~해당 항목 배점으로 채점하세요.  
2. 같은 **대항목**에 속한 소항목 점수를 합산하여 **대항목별 총점**을 계산합니다.  
3. 모든 대항목 점수를 합산하여 **총점(100점 만점)**으로 환산합니다.  
4. 문서 내에서 **미션 필드가 누락된 경우**, 해당 항목마다 -2점 감점합니다.  
5. 미션 항목이 누락되거나 불완전한 경우, `suggestions` 항목에 다음 형식으로 구체적인 보완 제안을 모두 포함합니다:
   - `"누락된 항목명: 필요한 내용 제안 또는 예시"`  
6. 총점을 기준으로 아래의 **등급표**에 따라 등급을 부여합니다.

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

## 📊 출력 형식 (BaseModel 준수)

아래 JSON 형식으로 출력하세요.

```json
{{
  "evaluations": [
    {{"item": "문서 구조·형식", "score": 18, "comment": "표·그림 캡션 일관성 부족"}},
    {{"item": "명료성·가독성", "score": 9, "comment": "전문용어 일부 설명 보완 필요"}}
  ],
  "mission_evaluation": [
    {{"section": "문서 기본 정보", "missing_fields": ["작성자", "버전"], "comment": "작성자/버전 정보 누락"}},
    {{"section": "주요 변경 사항", "missing_fields": ["기능 개선 요약"], "comment": "개선된 기능 요약이 부족"}}
  ],
  "total_score": 83,
  "grade": "B",
  "suggestions": [
    "작성자와 버전 정보를 명시하세요 (예: 홍길동, v1.0.1).",
    "주요 변경 사항 섹션에 '신규 기능/수정 내역'을 표 형식으로 작성하세요.",
    "Executive Summary를 2문장 이내로 요약문 형태로 추가하세요.
    "~한 내용이 누락되었습니다"
  ],
  "word_feedbacks": [
    {{"word": "보안 강화", "reason": "추상적 표현", "suggestion": "비밀번호 암호화 알고리즘 변경으로 구체화"}}
  ]
}}
"""

def get_mission(mission_id: str) -> dict:
    return mission_list.get(mission_id)