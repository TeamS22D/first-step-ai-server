from pprint import pprint
import pytest
from app.services.eval_document_v1 import eval_document_v1

def test_eval_release():
    release_note_rubric = """
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
    """

    user_prompt = """
    # 🚀 Release Note - v3.1.0 (2025-10-31)

## 📦 주요 변경사항
- 사용자 인증 모듈 개선  
  - 로그인 세션 유지 로직 최적화 (JWT 기반 세션 캐싱 적용)  
  - 비밀번호 초기화 절차를 단순화하고 보안 수준 강화 (SHA-512 → bcrypt 변경)
- 대시보드 UI 리뉴얼  
  - 통계 카드와 그래프의 반응형 디자인 적용  
  - 접근성(Accessibility) 개선: 색상 대비 향상 및 키보드 포커스 추가

## 🐞 버그 수정
- iOS Safari 환경에서 이미지 업로드 실패 문제 해결  
- 알림 설정 시 저장 오류(null 예외) 수정  
- 프로필 이미지 변경 후 즉시 반영되지 않던 문제 수정  

## ⚠️ 주의사항
- 이번 버전부터 로그인 토큰 정책이 변경되어 **기존 세션이 모두 만료**됩니다.  
- 커스텀 API 클라이언트를 사용하는 경우, 새 인증 헤더(`Authorization: Bearer`) 규격을 적용해야 합니다.

## 🗓️ 배포 정보
- 배포 일시: 2025-10-31 19:00 (KST)  
- 배포 환경: Production  
- 담당자: SEED Team (배포 승인자: @seed-admin)

## 🔗 참고 자료
- 관련 JIRA: [PROJ-1423](https://jira.seed.io/browse/PROJ-1423)  
- 관련 PR: [#245](https://github.com/seed/app/pull/245)  
- 테스트 보고서: [Test Summary](https://seed.io/test/v3.1.0)

## 💡 요약
이번 릴리즈는 **보안 강화, 사용자 경험 개선, 접근성 향상**을 중심으로 진행되었습니다.  
모든 주요 기능은 Stage 환경에서 검증 완료되었으며, 배포 후 영향 범위는 제한적입니다.
"""

    pprint(eval_document_v1("gpt-5", release_note_rubric, user_prompt).__dict__)


def test_eval_technical():
    technical_design_rubric = """
    | 번호 | 항목명 | 평가 내용 | 점검 포인트 | 배점 |
    |------|---------|-------------|---------------|------|
    | 1 | 문제 정의 (Problem Definition) | 해결하려는 문제를 명확히 정의했는가 | 배경 설명, 목표 명시 | 1~5 |
    | 2 | 설계 논리성 (Design Logic) | 제안된 구조가 논리적이고 근거가 충분한가 | 흐름의 일관성, 기술 선택 이유 | 1~5 |
    | 3 | 아키텍처 적합성 (Architecture Suitability) | 시스템 요구사항과 아키텍처가 부합하는가 | 확장성, 유지보수성 고려 | 1~5 |
    | 4 | 기술 명세 정확성 (Technical Accuracy) | API, DB 스키마, 알고리즘 명세가 정확한가 | 데이터 흐름 일관성, 타입 정확성 | 1~5 |
    | 5 | 리스크 식별 (Risk Identification) | 잠재적 위험 요소를 충분히 분석했는가 | 보안, 성능, 장애 포인트 등 | 1~5 |
    | 6 | 가독성 (Readability) | 문서의 구조와 표현이 명료한가 | 제목, 다이어그램, 일관된 용어 | 1~5 |
    | 7 | 참고 자료 (References) | 참고 문헌/링크가 충분히 제시되었는가 | 표준 문서, RFC, 외부 리소스 | 1~5 |
    """

    user_prompt = """
    # 🧠 Authentication System Redesign - Technical Design Document  
**Version:** 1.0.0  
**Date:** 2025-10-25  
**Author:** SEED Backend Team  

---

## 1. 개요 (Overview)
이 문서는 **인증(Authentication) 시스템 리팩토링 설계안**을 다룹니다.  
기존 세션 기반 구조를 **JWT + Redis 캐싱 구조로 전환**하여 확장성과 보안성을 개선하는 것이 목적입니다.

---

## 2. 아키텍처 개요 (Architecture Overview)

```mermaid
flowchart TD
  A[Client] -->|Login Request| B[Auth Service]
  B -->|Verify User| C[User DB]
  B -->|Generate JWT| D[Redis Cache]
  D -->|Store Token Metadata| E[Monitoring System]
"""

    pprint(eval_document_v1("gpt-5", technical_design_rubric, user_prompt).__dict__)