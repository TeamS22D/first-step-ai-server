from typing import List
from app.utils.cosine_sim import calculate_cosine_sim
import mistune

"""
mission_xx.json 요소

document_elements:
    document_name: 문서의 이름이 들어가는 란 입니다. type: heading, attrs: level: 1을 참고함

"""

mission_01 = {
    "document_elements": {
    "document_name": "스마트홈 IoT 앱 개발 프로젝트"
  },
    "required_sections": {
    "project_basic_info": {
    "project_name": "스마트홈 IoT 앱 개발 프로젝트",
    "period": "2025.06 ~ 2025.09 (3개월)",
    "purpose": "팀장 보고용 프로젝트 결과 보고서 작성",
    "background": "스마트홈 기기 수요와 종류가 증가하는 데 비해 다양한 기기를 통합 제어할 수 있는 맞춤형 앱 서비스가 부족하여 프로젝트를 추진함."
  },
    "execution_process": {
    "problem_definition": "스마트홈 기기는 늘어나고 있으나 이를 통합 관리할 수 있는 앱이 부족하다는 문제를 확인해 이를 해결하기 위한 앱 개발 필요성을 도출함.",
    "planning_design": "각 스마트홈 기기를 개별적으로 제어할 수 있는 주요 기능 기획, 알림/자동화/계정 등 부가 기능 분리 설계, UI·UX를 사용자 중심으로 구조화.",
    "implementation": "React Native / Expo, Flutter를 활용한 iOS/Android 크로스 플랫폼 앱 개발 및 주요 제조사의 스마트홈 기기 API 연동.",
    "testing_and_improvement": "실제 스마트홈 거주자 대상 베타 테스트를 진행하고 피드백에 따라 UI/UX 개선을 수행함. 일부 기기 연결 안정성 문제를 보완함."
  },
    "team_tech_info": {
    "team_members": "총 4명 (개발 2, 기획 1, 디자인 1)",
    "tech_stack": "React Native / Expo, Flutter, 스마트홈 기기 API 연동"
  },
    "project_results": {
    "functional_results": "여러 제조사의 스마트홈 기기 연결 및 일부 제어 기능 구현 성공. 대다수 기기에서 기본 제어 기능 동작.",
    "issues_or_failures": "일부 기기는 연결은 가능하지만 제어 기능 동작 실패.",
    "user_metrics": {
      "user_satisfaction": "92%",
      "downloads": "3,200회"
    }
  },
    "improvements": {
    "compatibility_issues": "특정 제조사 기기와의 호환성 문제 발생.",
    "performance_issues": "동시 기기 제어 시 서버 부하 문제 확인.",
    "feature_refinement": "알림 기능 정확도 및 안정성 개선 필요."
  },
    "future_plans": {
    "enhancement_plan": "일부 기기의 제어 기능까지 완전 지원하도록 기능 강화.",
    "technical_improvements": "서버 부하 개선 및 알림 기능 고도화.",
    "long_term_strategy": "사용자 패턴을 분석하여 자동 제어 시나리오를 추천하는 스마트 자동화 기능 추가."
  }
  }
}

def check_report_document_section(
        doc: str,
        mission_id: str = None,
)-> dict:
    """문서 내용을 임시로 확인하는 함수입니다."""
    section_score = {}
    # 문서
    parser = mistune.create_markdown(renderer='ast')
    ast = parser(doc)

    # 문서 이름 확인
    document_name = mission_01["document_elements"]["document_name"]

    #TODO: 일단 h1을 무조건 하나만 쓰도록 규제하고 싶은데 일단.. 그  작업은 나중에 하는편이 좋을 듯
    user_doc_name = get_raw_text(ast)
    scores = calculate_cosine_sim(user_doc_name, document_name)
    section_score["document_name"] = scores[0][0]





def get_heading(
    doc: List[dict],
    level: int = 1
) -> List[dict]:
    return [e.get("children")
            for e in doc
            if e.get("type") == "heading" and e.get("attrs", {}).get("level") == level
    ]

def get_raw_text(
    doc: List[dict],
    level: int = 1
) -> List[str]:
    children = get_heading(doc, level)
    text_lst = []

    #TODO: 안쪽 children도 있지만, 일단 나중에 처리
    for child in children:
        s = ""
        for c in child:
            s += c.get("raw", "")
        text_lst.append(s)

    return text_lst