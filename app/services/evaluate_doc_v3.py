import json
from pathlib import Path
from typing import Dict, List, Optional, Any

from app.core.openai_client import ask_gpt
from app.models.DocumentEvaluation import DocumentEvaluation
from app.utils.rubric_manager.manager import RubricManager
from app.utils.rubric_manager.models import Category, CriteriaItem


class MissionManager:
    def __init__(self, missions_dir: str = "app/missions/templates"):
        self.missions_dir = Path(missions_dir)

    def get_mission(self, mission_id: str) -> Optional[Dict[str, Any]]:
        """Loads a mission from a JSON file."""
        mission_dir = self.missions_dir / mission_id
        mission_file = mission_dir / f"{mission_id}.json"

        if not mission_file.exists():
            return None

        with open(mission_file, "r", encoding="utf-8") as f:
            return json.load(f)


# Instantiate managers
rubric_manager = RubricManager()
mission_manager = MissionManager()


def evaluate_project_report(
        user_document: str,
        mission_id: str,
        model: str = "gpt-4o"
) -> DocumentEvaluation:
    """
    프로젝트 보고서를 평가하는 함수

    :param user_document: 사용자가 작성한 문서
    :param mission_id: 미션 ID
    :param model: 사용할 GPT 모델

    :return: ProjectReportEvaluation: 평가 결과
    """
    # 미션 가져오기
    mission = mission_manager.get_mission(mission_id)
    if not mission:
        raise ValueError(f"Mission '{mission_id}' not found")

    mission_type = mission.get("mission_type")
    if not mission_type:
        raise ValueError(f"Mission type not found in mission '{mission_id}'")

    rubric_name = "document"  # Or derive this from mission if needed
    special_type_name = mission.get("mission_type")

    # RubricManager에서 basic_rubric과 special_rubric 가져오기
    basic_rubric = rubric_manager.get_basic_rubric(rubric_name)
    special_rubric = rubric_manager.get_special_rubric(rubric_name, special_type_name)

    if not basic_rubric:
        raise ValueError(f"Rubric type '{rubric_name}' not found")

    # 루브릭을 마크다운 문자열로 변환
    basic_rubric_markdown = convert_criteria_to_prompt_string(basic_rubric)
    special_rubric_markdown = convert_special_rubric_to_prompt_string(special_rubric)

    # 프롬프트 생성
    developer_prompt = build_project_report_evaluation_prompt(
        rubric_markdown=basic_rubric_markdown + special_rubric_markdown,
        required_sections=mission.get("required_sections")
    )

    # GPT 호출
    return ask_gpt(
        response_model=DocumentEvaluation,
        model=model,
        user_prompt=user_document,
        developer_prompt=developer_prompt
    )


def convert_criteria_to_prompt_string(basic_rubric: Dict[str, Category]) -> str:
    """
    RubricManager의 basic_rubric (Dict[str, Category])을
    프롬프트용 마크다운 문자열로 변환
    """
    if not basic_rubric:
        return "루브릭 정보 없음"
    markdown = ""
    for category_name, category in basic_rubric.items():
        markdown += f"\n### {category_name} ({category.total_score}점)\n"
        for criteria in category.criteria:
            markdown += f"- **{criteria.name}** ({criteria.score}점): {criteria.description}\n"
    return markdown


def convert_special_rubric_to_prompt_string(special_rubric: List[CriteriaItem]) -> str:
    """
    special_rubric (List[CriteriaItem])을 마크다운 문자열로 변환
    """
    if not special_rubric:
        return ""
    markdown = "\n### 📌 특수 항목 평가 기준\n"
    for criteria in special_rubric:
        markdown += f"- **{criteria.name}** ({criteria.score}점): {criteria.description}\n"
    return markdown


def build_project_report_evaluation_prompt(rubric_markdown: str, required_sections: dict) -> str:
    """
    프로젝트 보고서 전용 평가 프롬프트.
    """
    sections_md = ""
    if required_sections:
        sections_md += "## 📋 프로젝트 보고서 필수 구성 항목\n\n"
        for section_key, section_data in required_sections.items():
            section_title = section_key.replace("_", " ").title()
            sections_md += f"### {section_title}\n"
            if isinstance(section_data, dict):
                for field, value in section_data.items():
                    field_name = field.replace("_", " ").title()
                    if isinstance(value, dict):
                        sections_md += f"- **{field_name}**\n"
                        for sub_key, sub_value in value.items():
                            sections_md += f"  - {sub_key}: `{sub_value}`\n"
                    else:
                        sections_md += f"- **{field_name}**: `{value}`\n"
            sections_md += "\n"
        sections_md += "---\n\n"

    return f"""
당신은 **프로젝트 보고서 평가 전문가**입니다.
사회 초년생이 작성한 프로젝트 보고서를 아래 두 기준으로 평가하세요.

## 평가 기준
{rubric_markdown}
{sections_md if sections_md else "⚠️ 필수 구성 항목 정보 없음"}

---

## 📊 채점 방식
1.  **일반 루브릭 (80점)**
    - 각 대항목의 배점 내에서 조건 충족 여부에 따라 채점
2.  **프로젝트 보고서 특화 항목 (20점)**
    - 위 6개 항목을 배점에 따라 채점
3.  **총점 = basic_rubric 합계 + special_rubric 합계**
4.  **등급 부여**

| 등급 | 점수 | 품질 수준 |
|---|---|---|
| A+ | 95~100 | 탁월함 |
| A | 90~94 | 우수함 |
| B+ | 85~89 | 양호함 |
| B | 80~84 | 적정함 |
| C | 70~79 | 보통 |
| D | 60~69 | 미흡함 |
| F | <60 | 불합격 |

---

## 📋 출력 형식 (JSON)
**중요: 반드시 아래 JSON 형식만 출력하세요. 다른 텍스트, 마크다운, 설명은 포함하지 마세요.**

```json
{{
  "evaluations": [
    {{
      "item": "문서 구조·형식",
      "score": 17,
      "comment": "전반적으로 구조가 잘 잡혀있으나, 일부 문단 길이가 길어 가독성을 해칩니다."
    }},
    {{
      "item": "목적·핵심성",
      "score": 12,
      "comment": "프로젝트의 목적과 배경이 명확하게 서술되었습니다."
    }}
  ],
  "mission_evaluation": [
    {{
      "section": "프로젝트 기본 정보",
      "missing_fields": ["작성자"],
      "comment": "작성자 정보가 누락되었습니다."
    }}
  ],
  "total_score": 82,
  "grade": "B",
  "suggestions": [
    "보고서 상단에 150-250자 Executive Summary를 추가하여 핵심 내용을 요약하세요.",
    "문단 길이를 5줄 이내로 조절하여 가독성을 높이세요."
  ],
  "word_feedbacks": [
    {{
      "word": "일부 기기",
      "reason": "모호한 표현",
      "suggestion": "구체적 제조사와 모델명 명시 (예: '샤오미 스마트 플러그 모델 X')"
    }}
  ]
}}
```
"""


if __name__ == "__main__":
    # To run this script for testing, execute it as a module from the project root:
    # python -m app.services.evaluate_doc_v3

    try:
        with open("app/missions/templates/mission_01/example_02.md", "r", encoding="utf-8") as f:
            sample_document = f.read()

        evaluation_result = evaluate_project_report(
            user_document=sample_document,
            mission_id="mission_01"
        )

        print(evaluation_result.model_dump_json(indent=2))

    except FileNotFoundError:
        print("Error: example_02.md not found. Make sure the file exists in app/missions/templates/mission_01/")
    except Exception as e:
        print(f"An error occurred: {e}")
