from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from typing import List
import json
import re

class Feedback(BaseModel):
    good_points: str = Field(description="이 평가 항목과 관련하여 사용자의 이메일에서 잘한 점에 대한 칭찬. (1-2문장)")
    improvement_points: str = Field(description="아쉬운 점에 대한 구체적인 지적. 반드시 이메일 내용에서 직접 예시를 인용해야 함.")
    suggested_fix: str = Field(description="개선할 점으로 꼽은 예시를 더 좋은 표현으로 수정한 제안.")

class EvaluationItem(BaseModel):
    item: str = Field(description="평가 항목 (예: 구조·형식, 목적·핵심성 등)")
    score: int = Field(description="해당 항목의 점수 (배점 기준)")
    feedback: Feedback = Field(description="해당 항목에 대한 상세 피드백 (칭찬, 개선점, 수정 제안 포함)")

class FinalEvaluation(BaseModel):
    evaluations: List[EvaluationItem] = Field(description="5개 항목별 평가 결과 목록")
    total_score: int = Field(description="모든 항목의 점수를 합산하여 산출한 최종 총점 (100점 만점)")
    grade: str = Field(description="총점에 따른 등급 (예: A+, A, B+, ...)")
    general_feedback: str = Field(description="이메일 전체에 대한 종합 피드백")


parser = JsonOutputParser(pydantic_object=FinalEvaluation)

def load_rubric():
    with open("email_evaluation_rubric.md", "r", encoding="utf-8") as f:
        return f.read()

import json

def load_missions():
    with open("app/missions.json", "r", encoding="utf-8") as f:
        return json.load(f)

def load_mission_examples(file_path: str):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "예시 파일을 찾을 수 없습니다."

def evaluate_mission_email(mission_id: str, user_email: str):
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    rubric = load_rubric()
    missions = load_missions()

    mission_map = {
        "mail_ex_1": "mail_1",
        "mail_ex_2": "mail_2",
        "mail_ex_3": "mail_3"
    }
    
    actual_mission_id = mission_map.get(mission_id)
    if not actual_mission_id:
        raise ValueError(f"Invalid mission_id: {mission_id}")

    mission = missions.get(actual_mission_id)
    if not mission:
        raise ValueError(f"Mission with ID {actual_mission_id} not found.")

    mission_scenario = mission.get("scenario", "미션 내용이 지정되지 않았습니다.")
    evaluation_guideline = mission.get("evaluation_guideline", "No specific evaluation guideline provided.")
    example_file_path = mission.get("example_file")
    
    mission_examples = ""
    if example_file_path:
        mission_examples = load_mission_examples(example_file_path)

    # 1. 변수를 포함한 프롬프트 "템플릿" 정의
    system_template = """
당신은 사회초년생의 이메일 작성을 도와주는 AI 평가관입니다.
주어진 미션 내용, 평가 기준, 작성 예시를 참고하여 사용자의 이메일을 체계적으로 평가하세요.
당신의 응답은 반드시 아래에 명시된 JSON 형식과 일치해야 합니다. 다른 부가적인 설명 없이 JSON 객체만 반환하세요.

## 미션 내용
{mission_scenario}

## 평가 가이드라인
{evaluation_guideline}

## 작성 예시
{mission_examples}

## 전체 평가 기준표
{rubric}

---
## 출력 형식
{format_instructions}
"""

    # ChatPromptTemplate 생성
    evaluation_prompt = ChatPromptTemplate.from_messages([
        ("system", system_template),
        ("user", "다음은 사용자가 작성한 이메일입니다. 평가를 진행해주세요:\n\n{user_email}")
    ])

    # LCEL 체인 구성
    chain = evaluation_prompt | llm

    # invoke 단계에서 모든 변수 값을 전달
    response = chain.invoke({
        "mission_scenario": mission_scenario,
        "evaluation_guideline": evaluation_guideline,
        "mission_examples": mission_examples,
        "rubric": rubric,
        "format_instructions": parser.get_format_instructions(),
        "user_email": user_email
    })
    raw_content = response.content

    if "```json" in raw_content:
        match = re.search(r"```json\s*(\{.*?\})\s*```", raw_content, re.DOTALL)
        if match:
            json_string = match.group(1)
        else:
            first_brace = raw_content.find('{')
            last_brace = raw_content.rfind('}')
            if first_brace != -1 and last_brace != -1:
                json_string = raw_content[first_brace:last_brace+1]
            else:
                raise ValueError("Could not extract JSON from the response.")
    else:
        first_brace = raw_content.find('{')
        last_brace = raw_content.rfind('}')
        if first_brace != -1 and last_brace != -1:
            json_string = raw_content[first_brace:last_brace+1]
        else:
            raise ValueError("Could not find a JSON object in the response.")

    return parser.parse(json_string)
