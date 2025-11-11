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
루브릭 하나만 만들어주소 이 루브릭은 사회초년생이 쓰는 문서를 분석하는 서비스에서 사용될 예정입니다. 기본적으로 문서에서 공통적으로 지켜야하는 루브릭이 있어야 합니다 문서별로 기본 루브릭에서 가중치를 다르게 해서 배점을 합니다 문서별 세부적인 사항을 배점합니다. 이 둘은 각자 모두 100점이고 이둘의 비율을 조정해서 최종적으로 점수를 환산합니다 예를 들어 릴리즈 문서에서 기본 항목이 있고 세부 사항이 있을 때 기본 20%, 세부 80% 이런식으로 할 수 있습니다. 현재 있는 기본 문서 루브릭은 대항목 배점 세부 항목 세부배점 평가 기준 측정 포인트 평가 방식 문서 구조·형식 20 제목·파일명 규칙 4 [유형]_[제목]_[날짜]_v1.0 형식 명명 규칙 일관성 regex pattern 목차 및 섹션 구조 4 개요-성과-문제-계획-결론 논리적 순서 Heading hierarchy DOM tree analysis 시각적 서식 3 표, 구분선, 불릿, 강조 통일 Formatting ratio style check 문단 길이·정렬 3 단락 5줄 이내, 정렬 일관 Sentence/line ratio line counter 표·그림·캡션 3 표/그림 제목·번호·출처 표시 Caption presence element detection 페이지 레이아웃 3 여백, 헤더/푸터 일관성 Layout consistency document analysis 목적·핵심성 15 보고 목적 명확성 5 첫 단락에 '무엇을 왜' 명시 Purpose sentence first para analysis 핵심요약 (Executive Summary) 4 150-250자 요약 존재 Summary presence word count 주요 결과/성과 핵심화 3 KPI 중심, 불필요 세부 제거 Keyword coverage keyword density 문서 제목·내용 일치 3 제목과 본문 주제 일관성 Topic similarity TF-IDF cosine 완결성·논리성 20 필수 항목 충족 5 과제 요구사항 모두 포함 Section checklist requirement match 정보 누락 없음 4 일정, 담당, 수치, 기한 완비 Required field fill field validation 논리적 전개 4 배경→문제→해결→결과 흐름 Logical order sequence check 인과관계 명시 4 원인-결과, 조치-성과 연결 Causal phrases relation extraction 결론·다음 단계 3 향후 계획/개선점/후속일정 Future section section detection 구체성·정확성 15 수치·지표 활용 5 %, 일정, 단가, 버전 등 정량화 Number/date density regex extraction 근거자료 제시 4 스크린샷, 로그, 표, 인용 Evidence reference attachment check 객관적 표현 3 '좋았다'→'87% 향상' 객관화 Adjective-to-data sentiment ratio 오류/모호 표현 없음 3 '적당히, 대체로' 등 최소화 Unclear term ratio vague word count 명료성·가독성 10 문장 길이 적정 3 평균 20어절 이하 Readability index sentence analyzer 용어 통일성 3 '사용자/유저' 혼용 금지 Term consistency dictionary check 문장 구조 간결성 2 한 문장 2절 이하 Clause count syntax parser 전문용어 설명 2 약어 풀네임, 용어 정의 Glossary presence acronym check 실행가능성 10 실현 가능한 계획 4 구체 일정·담당자 포함 Action completeness task extraction 리스크·한계 언급 3 위험요소, 제약사항 명시 Risk presence risk keyword 개선 방향 현실성 3 구체적 후속조치 계획 Feasibility check timeline check 어조·매너 10 객관적 보고 어조 2 감정/평가 표현 없이 중립 Politeness ratio emotion analysis 1인칭 자제 2 조직 중심 표현 Pronoun ratio pronoun count 감사·마무리 표현 1 확인 부탁, 감사 표현 Closing presence closing check 오탈자·맞춤법 2 맞춤법 검사 95% 이상 Spellcheck ratio spell checker 문체 일관성 2 시제/경어 통일 Style consistency style analysis 서명/부서 표기 1 작성자·소속 명시 Signature presence signature check 데이터 품질 10 변경 이력 추적 2 문서 버전/수정일 기록 Version control metadata check 관련 문서 참조 2 링크/레퍼런스 제공 Reference links hyperlink check 시각자료 품질 2 해상도/가독성 확보 Image quality resolution check 데이터 시각화 2 차트/그래프 적절 활용 Visualization use chart detection 부록/첨부 구성 2 별첨 자료 체계적 구성 Appendix structure attachment org 합계 110 이거이고 릴리즈 노트 버전 넘버링 Semantic Versioning 준수 5 version format Breaking Changes 하위 호환성 영향 강조 10 breaking highlight 마이그레이션 가이드 업그레이드 방법 제시 5 migration guide Known Issues 알려진 문제점 공개 5 issue disclosure 릴리즈 문서의 세부특화 항목입니다. 문서를 평가하는 기준에서 필요한 항목과 필요없는 항목을 구분하여 필요없으면 제외, 필요한 것이 있으면 삽입하여 주십시오 또한 문제를 평가할 때는 문제에 제시된 조건이 들어가 이쓴ㄴ지 없는지를 확인해야 합니다. 이를 명시해주십시오 예시 릴리즈 문서 문제 입니다 | 평가 영역 | 핵심 키워드 | 핵심 질문 | | --- | --- | --- | | 구조·형식 | 일관성 / 체계성 | 문서가 정형화되어 있는가? | | 목적·핵심성 | 의도 / 중요도 구분 | 릴리즈 목적이 한눈에 보이는가? | | 완결성·논리성 | 누락 없음 / 흐름 | 변경 내용이 논리적으로 이어지는가? | | 구체성·정확성 | 사실성 / 구체성 | 내용이 모호하지 않고 정확한가? | | 명료성·가독성 | 간결함 / 시각적 명확성 | 읽기 쉽고 바로 이해되는가? | | 실행가능성 | 대응력 / 실무 활용성 | 문서만 보고 조치가 가능한가? | | 전문성·톤앤매너 | 공식성 / 신뢰성 | 문서가 공식적이고 신뢰감 있는가? | 당신은 사내 백엔드 개발팀의 개발자입니다. 새로운 프로젝트 **“첫걸음(FirstStep)”** 플랫폼의 **인증 모듈 v1.1 업데이트**가 완료되어, **릴리즈 노트(ReleaseNote)**초안을 작성해야 합니다. ## 필수 포함 항목 ### 1. 문서 기본 정보 (필수) - 제목: FirstStep Platform - 인증 API 릴리즈 노트 v1.1 - 작성일, 작성자(부서), 버전 정보 포함 - Semantic Versioning 형식 준수 (ex: v1.1.0) ### 2. 개요 - 릴리즈 목적 및 핵심 요약 50자 이내로 기술 - 예: “OTP 인증 절차 추가 및 Rate Limit 정책 조정” ### 3. 버전 정보 표 - 이전 버전, 현재 버전, 릴리즈 타입, 배포 대상, 버전 규칙 명시 ### 4. 주요 변경 사항 (표로 정리) | 구분 | 항목 | 변경 내용 | 영향도 | | --- | --- | --- | --- | | 신규 기능 | OTP 인증 추가 | 로그인 시 OTP 코드 입력 필드 추가 | 중간 | | 수정 | Rate Limit 변경 | 분당 30회 → 20회로 수정 | 중간 | | 기타 | 에러 코드 추가 | 401_OTP_REQUIRED, 401_OTP_INVALID 추가 | 낮음 | ### 5. Breaking Changes (하위 호환성 영향) - v1.0 대비 변경된 응답 구조, 클라이언트 영향, 수정 필요 항목 명시 - 예시 JSON 포함 ### 6. 마이그레이션 가이드 - 클라이언트 코드 수정 절차 또는 대응 단계별 안내 - 예상 작업 기간 포함 (예: “프론트엔드 수정 약 2일 소요”) ### 7. Known Issues (알려진 문제) | ID | 구분 | 설명 | 우회 방안 | | --- | --- | --- | --- | | #FS-11 | OTP 서버 지연 | 특정 시간대 OTP 검증 지연 | 재시도 시 정상 처리 | ### 8. 향후 계획 - 차기 버전(v1.2, v2.0 등) 기능 및 일정 간략 명시 ### 9. 참고 정보 - 검토자 / 참고 문서 (보안 가이드라인, 이전 버전 명세서 링크 등) 탬플릿 예시 markdown # FirstStep Platform - 인증 API 릴리즈 노트 v1.1 **작성일:** 2025-11-04 **작성자:** 김도현 / 백엔드팀 **버전:** v1.1 (2025-Q1 예정) --- ## 1. 개요 > 본 릴리즈 노트는 FirstStep 플랫폼 인증 모듈의 **v1.1 업데이트 내용**을 설명한다. > 주요 변경사항은 **OTP(One-Time Password) 인증 절차 추가**이며, 기존 로그인 API와 회원가입 API에 하위 호환성을 유지한 상태로 기능이 확장되었다. --- ## 2. 버전 정보 | 항목 | 내용 | |------|------| | **이전 버전** | v1.0 | | **현재 버전** | v1.1 | | **버전 규칙** | Semantic Versioning (MAJOR.MINOR.PATCH) 준수 | | **릴리즈 타입** | Minor Update | | **배포 대상** | Backend API 서버 / 프론트엔드 연동 모듈 | --- ## 3. 주요 변경 사항 (Summary of Changes) | 구분 | 항목 | 변경 내용 | 영향도 | |------|------|------------|---------| | 신규 기능 | OTP 인증 추가 | 로그인 시 OTP 인증 코드 입력 필드 추가 | 중간 | | 수정 | 에러 메시지 개선 | 401 → 세분화된 코드(401_OTP_REQUIRED, 401_OTP_INVALID) 추가 | 낮음 | | 보안 | 비밀번호 재설정 로직 강화 | 재설정 토큰 만료시간 15분 → 10분 단축 | 낮음 | | 기타 | Rate Limit 정책 수정 | 인증 관련 API: 분당 30회 → 20회로 조정 | 중간 | --- ## 4. Breaking Changes (하위 호환성 영향) - 로그인 API 응답 구조가 일부 변경됨: json // v1.0 { "token": "eyJhbGciOi..." } // v1.1 { "token": "eyJhbGciOi...", "otp_required": true } - OTP가 활성화된 계정의 경우 **2단계 인증 절차를 반드시 수행해야 함**. - 기존 클라이언트는 otp_required 필드 인식 로직을 추가해야 정상 작동. **하위 호환성:** 부분적 영향 있음 (로그인 응답 구조 변경) --- ## 5. 마이그레이션 가이드 (Migration Guide) 1. 클라이언트 로그인 로직 수정: - otp_required 필드가 true인 경우 OTP 입력 화면으로 전환하도록 처리. 2. OTP 입력 후 인증 요청 API (POST /api/v1/auth/otp-verify) 추가 연동 필요. 3. Rate Limit 변경에 따른 API 호출 주기 재조정. **예상 소요 시간:** 2~3일 (프론트엔드 반영 기준) --- ## 6. Known Issues (알려진 문제점) | ID | 구분 | 설명 | 우회 방안 | |----|------|------|------------| | #FS-11 | OTP 서버 지연 | 특정 시간대 OTP 검증 지연 발생 가능 | 재시도 시 정상 처리 | | #FS-12 | 비밀번호 재설정 시 이메일 중복 발송 | 동일 요청 중복 시 다중 메일 발송 가능 | 임시: 1분 제한 추가 예정 | | #FS-13 | 일부 브라우저 캐시 문제 | Chrome 110 이하 버전에서 캐시로 OTP 미반영 | 캐시 초기화 필요 | --- ## 7. 향후 계획 | 버전 | 예정 기능 | 예상 일정 | |------|-------------|------------| | v1.2 | 로그인 시도 제한(Brute-force 방어) | 2025-Q3 | | v2.0 | OAuth 통합 인증 (Google, Apple) | 2026-Q1 | --- **검토자:** QA팀 이수진 **참고 문서:** [Security Guideline v2.3](https://intranet.company.local/docs/security) / [API 명세서 v1.0](sandbox:/mnt/data/FirstStep_Auth_API_v1.0.md) --- > © 2025 FirstStep Platform Backend Team. All rights reserved. 이는 문제의 예시입니다. 마찬가지로 예시 문제도 함께 루브릭을 기반으로 평가가능하도록 만들 수 있는 프롬프트를 작성해주십시오. 이때 필요하다면 프롬프트 루브릭을 작성해도 좋습니다. 문제를 만들 시, SW개발자라는 것을 명심해 프론트, 백 등의 직업군을 생각하여 만들 수 있도록 해야합니다


또한 문제에서는 문제 상황과 문제안에 들어가야 하는 요소가 포함되어야 합니다. 문제 작성 프롬프트를 생성 시 이가 들어갈 수 있도록 만들어 주시고, 또한 문제 평가 프롬프트에서 어떤 항목이 들어갔는지 확인할 수 있도록 내용 안에 들어가야 하는 항목이 있어야 합니다.

사용자가 작성할 수 있도록 문제를 작성할 수 있는 릴리즈 문서 템플릿도 출력할 수 있도록 문제 프롬프트를 만들어주세요

현재 제가 준 상황에서 당신은 **문제 생성 프롬프트**를 만드는 것이 목표입니다
"""

    response = get_openapi.use_message("gpt-5", developer_prompt)
    print(response.output_text)