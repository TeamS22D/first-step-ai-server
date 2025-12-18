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
        다음에 제공되는 '평가 루브릭'을 기준으로 사용자의 이메일 답안을 평가하라.

        [채점 원칙]
        - 루브릭에 명시된 항목과 점수 기준만 사용하여 평가한다.
        - 루브릭에 없는 기준으로 임의로 가점 또는 감점하지 않는다.
        - 요구사항이 명시된 항목이 답안에 없을 경우 해당 항목은 0점 처리한다.
        - 부분적으로만 충족한 경우, 해당 기준 점수 내에서 합리적으로 감점한다.
        - 감정적 평가, 주관적 인상평은 배제한다.

        [평가 방식]
        - 루브릭의 basic_rubric에 정의된 category 단위로 평가를 진행한다.
        - 각 category 하위 criteria별로:
          · 배점(score)
          · 실제 부여 점수
          · 감점 또는 부여 사유
          를 명확히 작성한다.
        - category 점수는 해당 criteria 점수의 합으로 계산한다.
        - 전체 총점은 모든 category 점수의 합으로 계산한다.

        [출력 규칙]
        - 최종 결과는 반드시 아래 스키마(DocumentEvaluation)에 맞춰 구조화하여 출력한다.
        - summary_feedback은 사용자가 읽는 최종 종합 피드백으로,
          정중한 존댓말, 한 문단 분량으로 작성한다.
        - internal_note에는 시스템 내부 판단 메모만 작성하며,
          사용자에게 보이는 내용은 절대 포함하지 않는다.
        - 점수 계산 과정이나 내부 판단 기준을 외부로 노출하지 않는다.
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
    model="gpt-4o",
    temperature=0,
    api_key=config.OPENAI_API_KEY
)

grading_llm = base_llm.with_structured_output(DocumentEvaluation)

grading_chain = grading_prompt | grading_llm

#TODO: response Model
#TODO: 예시 만들기, 예시 바탕으로 good, suggested 예시 만들기
#TODO: 템플릿 생성

def evaluate_email(
    user_answer: str,
    question: str,
    rubric: str,
    reference_answer: str = "",
)-> EvaluationResult:
    """
        사용자가 작성한 이메일을 평가합니다.
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

    total_score = calculate_basic_score("email_mission_weighted_v2", "email_request", parse_scores(evaluation_grade))
    print(total_score)
    grade = get_grade(total_score)
    evaluation_result = EvaluationResult(**evaluation_grade.model_dump(), total_score=total_score, grade=grade)
    evaluation_result.total_score = total_score
    print(evaluation_result)
    return evaluation_result
