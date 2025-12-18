from app.models.DocumentEvaluation import *
from app.utils.calculate_score import parse_scores, calculate_basic_score, get_grade
from app.core.config import config

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI


grading_prompt = ChatPromptTemplate.from_messages(
[
    (
        "system",
            """
                너는 엄격하지만 공정한 문서 채점관이다.
                다음 '평가 루브릭'을 기준으로 사용자의 보고서를 평가하라.
                
                규칙:
                - 루브릭에 없는 기준으로 임의로 감점하지 마라.
                - 각 평가 항목별로 점수와 그 이유를 한국어로 명확하게 작성하라.
                - summary_feedback은 사용자가 읽는 최종 요약 피드백으로, 존댓말 한 문단으로 작성하라.
                - internal_note에는 시스템 내부용 메모만 남기고, 사용자가 읽을 내용을 쓰지 마라.
                - 최종 결과는 아래 스키마(DocumentEvaluation)에 맞게 구조화하여 출력하라.
            """
    ),
    (
        "human",
            """
            [문제]
            {question}
            
            [평가 루브릭(JSON 또는 텍스트)]
            {rubric}
            
            [참고용 모범답안(없으면 빈 문자열)]
            {reference_answer}
            
            [사용자 답안]
            {user_answer}
            """
        ),
    ]
)

base_llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    api_key=config.OPENAI_API_KEY
)

grading_llm = base_llm.with_structured_output(DocumentEvaluation)

grading_chain = grading_prompt | grading_llm

#TODO: response Model
#TODO: 예시 만들기, 예시 바탕으로 good, suggested 예시 만들기
#TODO: 템플릿 생성

def evaluate_document(
    user_answer: str,
    question: str,
    rubric: str,
    reference_answer: str = "",
)-> EvaluationResult:
    """
        사용자가 작성한 문서를 평가합니다.
        :param reference_answer:
        :param user_answer:
        :param question:
        :param rubric:
        :return:

    """

    evaluation_grade: DocumentEvaluation = grading_chain.invoke(
        {
            "question": question,
            "reference_answer": reference_answer or "",
            "user_answer": user_answer,
            "rubric": rubric,
        }
    )

    total_score = calculate_basic_score("document_v2", "project_report", parse_scores(evaluation_grade))
    grade = get_grade(total_score)
    evaluation_result = EvaluationResult(**evaluation_grade.model_dump(), total_score=total_score, grade=grade)
    return evaluation_result
