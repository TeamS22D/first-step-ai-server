from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from typing import List, Dict, Any
import json
import re
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

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
    rubric_content = load_rubric()  # 변수명을 rubric_content로 변경하여 RAG용으로 명확히 구분
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

    rubric_doc = Document(page_content=rubric_content, metadata={"source": "email_rubric"})

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents([rubric_doc])

    embeddings = OpenAIEmbeddings()
    vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

    system_template = """
                        당신은 사회초년생의 이메일 작성을 돕는 전문 AI 평가관입니다.
                        주어진 미션 내용, 평가 가이드라인, 그리고 아래 '참고 자료'로 검색된 **상세 평가 기준**을 참고하여 사용자의 이메일을 체계적으로 평가하세요.
                        
                        ## 미션 내용:
                        {mission_scenario}
                        
                        ## 평가 가이드라인:
                        {evaluation_guideline}
                        
                        ---
                        **[핵심 지침]: 당신은 평가 기준표를 참고하되, 응답 JSON의 'evaluations' 목록에는 반드시 다음 5개의 항목(category)만 포함해야 합니다.**
                        1. 구조·형식
                        2. 목적·핵심성
                        3. 완결성
                        4. 명료성·가독성
                        5. 어조·매너
                        
                        각 'EvaluationItem'의 'item' 필드에는 반드시 위에 명시된 5개 항목 중 하나를 사용해야 합니다.
                        ---
                        ## 참고 자료 (RAG 검색 결과 - 상세 평가 기준):
                        {context}
                        ---
                        ## 출력 형식 지침:
                        {format_instructions}
                        """

    # ChatPromptTemplate 생성
    evaluation_prompt = ChatPromptTemplate.from_messages([
        ("system", system_template),
        ("user", "다음 이메일을 평가해주세요. 이메일 예시: {mission_examples}\n\n사용자 이메일:\n{user_email}")
    ])

    question_answer_chain = create_stuff_documents_chain(llm, evaluation_prompt)
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)

    response = rag_chain.invoke({
        "input": user_email,

        "mission_scenario": mission_scenario,
        "evaluation_guideline": evaluation_guideline,
        "format_instructions": parser.get_format_instructions(),
        "mission_examples": mission_examples,
        "user_email": user_email
    })

    raw_content = response["answer"]

    if "```json" in raw_content:
        match = re.search(r"```json\s*(\{.*?\})\s*```", raw_content, re.DOTALL)
        if match:
            json_string = match.group(1)
        else:
            first_brace = raw_content.find('{')
            last_brace = raw_content.rfind('}')
            if first_brace != -1 and last_brace != -1:
                json_string = raw_content[first_brace:last_brace + 1]
            else:
                raise ValueError("Could not extract JSON from the response.")
    else:
        first_brace = raw_content.find('{')
        last_brace = raw_content.rfind('}')
        if first_brace != -1 and last_brace != -1:
            json_string = raw_content[first_brace:last_brace + 1]
        else:
            raise ValueError("Could not find a JSON object in the response.")

    return parser.parse(json_string)