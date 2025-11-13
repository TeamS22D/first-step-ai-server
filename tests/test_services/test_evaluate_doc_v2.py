import pytest
from app.services.evaluate_doc_v2 import evaluate_doc_v2, summarize_eval_v1
from pprint import pprint



def test_evaluate_doc_v2_id_1():
    user_prompt = """
# FirstStep Platform - 인증 API 릴리즈 노트 v2.0.0
작성일: 2024-06-14  
작성자: 홍길동 / Backend팀  
버전: v2.0.0 (분류: Major)

---

1. 개요 - 50자 이내 요약:  
토큰 암호방식 개선 및 신규 API 경로 적용(간략 전환 안내)

2. 버전 정보

| 항목         | 내용         |
|--------------|--------------|
| 이전 버전    | v1.2         |
| 현재 버전    | v2.0.0       |
| 버전 규칙    | SemVer 2.0   |
| 릴리즈 타입  | 전체         |
| 배포 대상    | API 서버     |

3. 주요 변경 사항

| 구분   | 항목      | 변경 내용                       | 영향도      |
|--------|-----------|----------------------------------|-------------|
| 보안   | 토큰 포맷 | JWT에서 PASETO로 암호 알고리즘 변경 | 낮음        |
| 신규   | 경로 변경 | /api/v2 경로 신설                | 보통        |

4. Breaking Changes(하위 호환성 영향)

- 설명: 기존 토큰 및 사용자 정보 응답 포맷이 호환되지 않음
- 변경 전/후 예시(JSON 등):
  // Before
  { "token": "eyJ...", "user": {"id": 3, "email": "test@abc.com"} }
  // After
  { "token": "v2.local...", "tokenType": "PASETO" }
- 클라이언트 영향: 엔드포인트만 변경, 응답 파서 일부 조정 필요
- 수정 필요 항목: 사용자 ID

5. 마이그레이션 가이드

- 단계별 변경 지침:
   1) 토큰 검증 로직만 새 포맷(PASETO)으로 수정
- 예상 소요 시간: 약 1일
- 추가 고려사항: v1 API 사용 시 자동 리디렉션 없음

6. Known Issues(알려진 문제)

| ID | 구분   | 설명                  | 우회 방안                 |
|----|--------|----------------------|---------------------------|
| #FS-21 | API응답 | v2 token_type 값 미반환 | 별도 null 체크 권장         |

7. 향후 계획

| 버전 | 예정 기능    | 예상 일정   |
|------|-------------|-------------|
| v2.1 | 세션만료알림 | 하반기 중   |

8. 참고 정보

- 검토자: 김승현
- 참고 문서: 없음

---

© FirstStep Platform Backend Team. All rights reserved.

---
"""

    pprint(
        evaluate_doc_v2(
            user_prompt=user_prompt,
            document_type="report_evaluation_criteria",
            mission_id="id_1").__dict__
    )

def test_evaluate_doc_v2_id_2():
    user_prompt = """
    # FirstStep Platform - 인증 API 릴리즈 노트 v1.1.1

    작성일: 2025-11-12
    작성자: 
    버전: v1.1.1 (분류: Patch)

    ---

    1. 개요
    - 50자 이내 요약: 토큰 갱신 충돌 핫픽스 및 에러 코드 보정

    2. 버전 정보
    | 항목 | 내용 |
    |------|------|
    | 이전 버전 | v1.1 |
    | 현재 버전 | v1.1.1 |
    | 버전 규칙 | Semantic Versioning (MAJOR.MINOR.PATCH) |
    | 릴리즈 타입 | Patch |
    | 배포 대상 | Backend API 서버 |

    3. 주요 변경 사항
    | 구분 | 항목 | 변경 내용 | 영향도 |
    |------|------|-----------|--------|
    | 수정 | 토큰 갱신 충돌 처리 (POST /api/v1/auth/token/refresh) | 동시 갱신 시 저장소 충돌 해결: 낙관적 잠금 도입, 지수 백오프 재시도 | 중간 |
    | 기타 | 에러 코드 추가 | 일부 500_INTERNAL_ERROR → 409_REFRESH_CONFLICT 신규 코드 도입(스펙 동일) | 중간 |
    | 기타 | 응답 헤더 추가 | X-Request-Id 응답 헤더 및 로그 필드 request_id 추가 | 낮음 |

    4. Breaking Changes(하위 호환성 영향)
    - 설명: 없음
    - 변경 전/후 예시(JSON 등):
      // Before

      // After

    - 클라이언트 영향: 
    - 수정 필요 항목: 

    5. 마이그레이션 가이드
    - 단계별 변경 지침:
      1) 409_REFRESH_CONFLICT 수신 시 지수 백오프(초기 200ms, 최대 2s, Jitter 포함)로 최대 3회까지 재시도 로직 추가
      2) 재시도 실패 시 사용자 안내 메시지 노출, 요청·응답 로그에 X-Request-Id 포함해 추적성 확보
    - 예상 소요 시간: 0.5~1일
    - 추가 고려사항(레이트 제한, 리트라이, 롤백 등): 레이트 제한 준수(분당 요청 한도 확인), 타임아웃 3s→5s 권장, 동시 갱신 요청 합치기(Coalescing) 고려, 문제 발생 시 v1.1로 롤백 플랜 유지

    6. Known Issues(알려진 문제)
    | ID | 구분 | 설명 | 우회 방안 |
    |----|------|------|-----------|
    | #FS-247 | API | 토큰 저장소 지연 시 간헐적 409 지속 가능 | 최대 3회 재시도, 지수 백오프+Jitter 적용, 동시 요청 합치기 |

    7. 향후 계획
    | 버전 | 예정 기능 | 예상 일정 |
    |------|-----------|-----------|
    | v1.2 | 소셜 로그인(OAuth2) 지원 | 2025-12 |
    | v1.1.2 | 모니터링/로그 대시보드 개선 | 2025-11 |

    8. 참고 정보
    - 검토자: 
    - 참고 문서: 장애 리포트 FS-1234, 로그 포맷 가이드(https://confluence.firststep.local/incident/FS-1234, https://confluence.firststep.local/logging/request-id)

    ---
    © FirstStep Platform Backend Team. All rights reserved."""

    pprint(
        evaluate_doc_v2(
            model="gpt-4.1",
            user_prompt=user_prompt,
            document_type="report_evaluation_criteria",
            mission_id="id_2").__dict__
    )

def test_summarize_eval_v1():
    user_prompt = """
        # FirstStep Platform - 인증 API 릴리즈 노트 v1.1.1

        작성일: 2025-11-12
        작성자: 
        버전: v1.1.1 (분류: Patch)

        ---

        1. 개요
        - 50자 이내 요약: 토큰 갱신 충돌 핫픽스 및 에러 코드 보정

        2. 버전 정보
        | 항목 | 내용 |
        |------|------|
        | 이전 버전 | v1.1 |
        | 현재 버전 | v1.1.1 |
        | 버전 규칙 | Semantic Versioning (MAJOR.MINOR.PATCH) |
        | 릴리즈 타입 | Patch |
        | 배포 대상 | Backend API 서버 |

        3. 주요 변경 사항
        | 구분 | 항목 | 변경 내용 | 영향도 |
        |------|------|-----------|--------|
        | 수정 | 토큰 갱신 충돌 처리 (POST /api/v1/auth/token/refresh) | 동시 갱신 시 저장소 충돌 해결: 낙관적 잠금 도입, 지수 백오프 재시도 | 중간 |
        | 기타 | 에러 코드 추가 | 일부 500_INTERNAL_ERROR → 409_REFRESH_CONFLICT 신규 코드 도입(스펙 동일) | 중간 |
        | 기타 | 응답 헤더 추가 | X-Request-Id 응답 헤더 및 로그 필드 request_id 추가 | 낮음 |

        4. Breaking Changes(하위 호환성 영향)
        - 설명: 없음
        - 변경 전/후 예시(JSON 등):
          // Before

          // After

        - 클라이언트 영향: 
        - 수정 필요 항목: 

        5. 마이그레이션 가이드
        - 단계별 변경 지침:
          1) 409_REFRESH_CONFLICT 수신 시 지수 백오프(초기 200ms, 최대 2s, Jitter 포함)로 최대 3회까지 재시도 로직 추가
          2) 재시도 실패 시 사용자 안내 메시지 노출, 요청·응답 로그에 X-Request-Id 포함해 추적성 확보
        - 예상 소요 시간: 0.5~1일
        - 추가 고려사항(레이트 제한, 리트라이, 롤백 등): 레이트 제한 준수(분당 요청 한도 확인), 타임아웃 3s→5s 권장, 동시 갱신 요청 합치기(Coalescing) 고려, 문제 발생 시 v1.1로 롤백 플랜 유지

        6. Known Issues(알려진 문제)
        | ID | 구분 | 설명 | 우회 방안 |
        |----|------|------|-----------|
        | #FS-247 | API | 토큰 저장소 지연 시 간헐적 409 지속 가능 | 최대 3회 재시도, 지수 백오프+Jitter 적용, 동시 요청 합치기 |

        7. 향후 계획
        | 버전 | 예정 기능 | 예상 일정 |
        |------|-----------|-----------|
        | v1.2 | 소셜 로그인(OAuth2) 지원 | 2025-12 |
        | v1.1.2 | 모니터링/로그 대시보드 개선 | 2025-11 |

        8. 참고 정보
        - 검토자: 
        - 참고 문서: 장애 리포트 FS-1234, 로그 포맷 가이드(https://confluence.firststep.local/incident/FS-1234, https://confluence.firststep.local/logging/request-id)

        ---
        © FirstStep Platform Backend Team. All rights reserved."""

    pprint(
        summarize_eval_v1(
            model="gpt-4.1",
            user_prompt=user_prompt,
            mission_id="id_2",
            rubric_type="report_evaluation_criteria").__dict__
    )
