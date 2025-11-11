import pytest
import json
from app.services.get_openapi import *
from app.services.chat import *


from app.services import get_openapi

def test_get_openapi():
    message = "아첨이 무엇인지 궁금해"

    response = get_openapi.use_message(message=message, model="gpt-5")

    print(response)


def test_convert_json():
    print("\n\n#### test convert json ####\n\n")

    string = '{"단어": "아첨", "설명": "남을 기쁘게 하기 위해 비아냥거리고 잘맞추는 말이나 행동을 하는 것을 가리키는 단어입니다."}'

    python_dict = json.loads(string)

    print(python_dict)

def test_get_word_description():
    print("\n\n#### test get word description ####\n\n")

    message = "니코틴아마이드 아데닌 다이뉴클레오타이드"

    response = get_word_description(message=message)

    print(response, type(response))

def test_chat():
    print("\n\n#### test chat ####\n\n")

    message = "어떤 프로젝트가 있었지? 기억이 잘 나지 않네"

    response = chatting(message=message)

    print(response)



def test_check_action():
    class API:
        def __init__(self):
            pass

        def attack(self, a, b, c, d, rr):
            return f"상대를 공격합니다. {a}, {b}, {c}, {d}, {rr}"

        def defence(self, a, b, c, d, rr):
            return f"공격을 막습니다. {b}, {d}, {rr}, {a}, {c}"

    api = API()

    message="내앞에 도둑이 있다."

    response = check_action(model="gpt-4o-mini", message=message)

    method = response.method
    kwargs = response.kwargs.model_dump()
    print(response)

    fn = getattr(api, method)
    print(fn(**kwargs))

def test_get_document():

    message = """GitHub를 이용하는 방법
필자가 자주 애용하는 방식이다.
예를 들면 theorydb.github.io\assets\img\의 위치에 포스트 계층과 동일하게 폴더를 만들어 포스트 제목-일련번호의 형태로 파일을 저장한 후, https://theorydb.github.io/assets/img/think/2019-06-25-think-future-ai-1.png와 같은 방식으로 링크를 걸어 활용한다.
물론, 이미지 파일 관리에 있어 노가다가 첨가되고 GitHub에 이미지를 먼저 올리지 않으면 Markdown을 작성하며 실시간으로 확인할 수 없다는 불편한 점이 있다.
하지만 필자가 처음 블로그를 개발했을 때 가장 중요했던 목적 하나는 블로그 서비스가 종료되더라도 포스트와 이미지를 개인 DB화 하여 영구 보존하는 것이었기에 큰 불만이 없는 방식이다. 더불어 숙달되어 큰 불편을 느끼지 않는다.
기타
구글드라이브, 플리커, 드랍박스에 이미지를 체계적으로 관리하고 URL을 생성하여 연결하는 것도 한가지 방법이다.
큰 불편함을 느끼지 않아 더 찾아보지는 않았는데 이 부분을 쉽게 처리해 줄 Plug-in이 존재할 것으로 믿는다.ㅎㅎ"""

    response = get_markdown(message=message)

    print(response)

def test_generate_problems():

    developer_prompt = """
지금 나는 사회 초년생들이 릴리즈 노트 쓰는게 처음에 힘들 것 같아서 도와주는 연습문제를 만들려고 해. 사회 초년생이 릴리즈 노트 작성 시 알아야 하는 부분을 위주로 작업 연습을 할 수 있도록 문제를 만들어 주면 좋겠어
연습 문제에서는 무엇을 채워야하는지 명시해줘야해
아래는 내가 작성한 초안이야
그리고 템플릿 예시는 사용자가 이를 가지고 작성 연습을 하는 공간이야
이 템플릿에서는 사용자가 꼭 적지 않아도 되는 (기본적으로 있어야 하는) 것들이 채워져 있어    
```
당신은 사내 백엔드 개발팀의 개발자입니다.

새로운 프로젝트 **“첫걸음(FirstStep)”** 플랫폼의 **인증 모듈 v1.1 업데이트**가 완료되어, **릴리즈 노트(ReleaseNote)**초안을 작성해야 합니다.

## 필수 포함 항목

### 1. 문서 기본 정보 (필수)

- 제목: `FirstStep Platform - 인증 API 릴리즈 노트 v1.1`
- 작성일, 작성자(부서), 버전 정보 포함
- Semantic Versioning 형식 준수 (ex: v1.1.0)

### 2. 개요

- 릴리즈 목적 및 핵심 요약 50자 이내로 기술
- 예: “OTP 인증 절차 추가 및 Rate Limit 정책 조정”

### 3. 버전 정보 표

- 이전 버전, 현재 버전, 릴리즈 타입, 배포 대상, 버전 규칙 명시

### 4. 주요 변경 사항 (표로 정리)

| 구분 | 항목 | 변경 내용 | 영향도 |
| --- | --- | --- | --- |
| 신규 기능 | OTP 인증 추가 | 로그인 시 OTP 코드 입력 필드 추가 | 중간 |
| 수정 | Rate Limit 변경 | 분당 30회 → 20회로 수정 | 중간 |
| 기타 | 에러 코드 추가 | `401_OTP_REQUIRED`, `401_OTP_INVALID` 추가 | 낮음 |

### 5. Breaking Changes (하위 호환성 영향)

- v1.0 대비 변경된 응답 구조, 클라이언트 영향, 수정 필요 항목 명시
- 예시 JSON 포함

### 6. 마이그레이션 가이드

- 클라이언트 코드 수정 절차 또는 대응 단계별 안내
- 예상 작업 기간 포함 (예: “프론트엔드 수정 약 2일 소요”)

### 7. Known Issues (알려진 문제)

| ID | 구분 | 설명 | 우회 방안 |
| --- | --- | --- | --- |
| #FS-11 | OTP 서버 지연 | 특정 시간대 OTP 검증 지연 | 재시도 시 정상 처리 |

### 8. 향후 계획

- 차기 버전(v1.2, v2.0 등) 기능 및 일정 간략 명시

### 9. 참고 정보

- 검토자 / 참고 문서 (보안 가이드라인, 이전 버전 명세서 링크 등)

탬플릿 예시
```
# FirstStep Platform - 인증 API 릴리즈 노트 v1.1

**작성일:** 2025-11-04  
**작성자:** 김도현 / 백엔드팀  
**버전:** v1.1 (2025-Q1 예정)

---

## 1. 개요
> 본 릴리즈 노트는 FirstStep 플랫폼 인증 모듈의 **v1.1 업데이트 내용**을 설명한다.  
> 주요 변경사항은 **OTP(One-Time Password) 인증 절차 추가**이며, 기존 로그인 API와 회원가입 API에 하위 호환성을 유지한 상태로 기능이 확장되었다.

---

## 2. 버전 정보
| 항목 | 내용 |
|------|------|
| **이전 버전** | v1.0 |
| **현재 버전** | v1.1 |
| **버전 규칙** | Semantic Versioning (MAJOR.MINOR.PATCH) 준수 |
| **릴리즈 타입** | Minor Update |
| **배포 대상** | Backend API 서버 / 프론트엔드 연동 모듈 |

---

## 3. 주요 변경 사항 (Summary of Changes)

| 구분 | 항목 | 변경 내용 | 영향도 |
|------|------|------------|---------|
| 신규 기능 | OTP 인증 추가 | 로그인 시 OTP 인증 코드 입력 필드 추가 | 중간 |
| 수정 | 에러 메시지 개선 | 401 → 세분화된 코드(`401_OTP_REQUIRED`, `401_OTP_INVALID`) 추가 | 낮음 |
| 보안 | 비밀번호 재설정 로직 강화 | 재설정 토큰 만료시간 15분 → 10분 단축 | 낮음 |
| 기타 | Rate Limit 정책 수정 | 인증 관련 API: 분당 30회 → 20회로 조정 | 중간 |

---

## 4. Breaking Changes (하위 호환성 영향)

- 로그인 API 응답 구조가 일부 변경됨:
  ```json
  // v1.0
  {
    "token": "eyJhbGciOi..."
  }

  // v1.1
  {
    "token": "eyJhbGciOi...",
    "otp_required": true
  }
  ```
- OTP가 활성화된 계정의 경우 **2단계 인증 절차를 반드시 수행해야 함**.  
- 기존 클라이언트는 `otp_required` 필드 인식 로직을 추가해야 정상 작동.

**하위 호환성:** 부분적 영향 있음 (로그인 응답 구조 변경)

---

## 5. 마이그레이션 가이드 (Migration Guide)

1. 클라이언트 로그인 로직 수정:
   - `otp_required` 필드가 `true`인 경우 OTP 입력 화면으로 전환하도록 처리.
2. OTP 입력 후 인증 요청 API (`POST /api/v1/auth/otp-verify`) 추가 연동 필요.
3. Rate Limit 변경에 따른 API 호출 주기 재조정.

**예상 소요 시간:** 2~3일 (프론트엔드 반영 기준)

---

## 6. Known Issues (알려진 문제점)

| ID | 구분 | 설명 | 우회 방안 |
|----|------|------|------------|
| #FS-11 | OTP 서버 지연 | 특정 시간대 OTP 검증 지연 발생 가능 | 재시도 시 정상 처리 |
| #FS-12 | 비밀번호 재설정 시 이메일 중복 발송 | 동일 요청 중복 시 다중 메일 발송 가능 | 임시: 1분 제한 추가 예정 |
| #FS-13 | 일부 브라우저 캐시 문제 | Chrome 110 이하 버전에서 캐시로 OTP 미반영 | 캐시 초기화 필요 |

---

## 7. 향후 계획

| 버전 | 예정 기능 | 예상 일정 |
|------|-------------|------------|
| v1.2 | 로그인 시도 제한(Brute-force 방어) | 2025-Q3 |
| v2.0 | OAuth 통합 인증 (Google, Apple) | 2026-Q1 |

---

**검토자:** QA팀 이수진  
**참고 문서:** [Security Guideline v2.3](https://intranet.company.local/docs/security) / [API 명세서 v1.0](sandbox:/mnt/data/FirstStep_Auth_API_v1.0.md)

---

> © 2025 FirstStep Platform Backend Team. All rights reserved.

```

---
```


"""

    response = get_openapi.use_message("gpt-5", developer_prompt)
    print(response.output_text)