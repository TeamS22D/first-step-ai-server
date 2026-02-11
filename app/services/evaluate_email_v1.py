import os
from app.core.openai_client import client
from app.models.EmailEvaluation import EmailEvaluationResult
from app.utils.rubric_manager.manager import RubricManager
from app.utils.logger import logger

# 루브릭 파일 경로
current_dir = os.path.dirname(__file__)
rubric_path = os.path.join(current_dir, '..', 'rubrics', 'email_evaluation_rubric.md')

def load_rubric_content():
    """루브릭 파일의 내용을 읽어 반환합니다."""
    try:
        with open(rubric_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        logger.error(f"Rubric file not found at: {rubric_path}")
        return "Rubric file not found."
    except Exception as e:
        logger.error(f"Error reading rubric file: {e}")
        return "Error reading rubric file."

EMAIL_RUBRIC = load_rubric_content()

async def evaluate_email_content(user_email: str) -> EmailEvaluationResult:
    """
    사용자가 작성한 이메일 내용을 바탕으로 평가를 수행하고 결과를 반환합니다.
    """
    system_prompt = f"""
    당신은 제출된 이메일을 평가하는 전문적인 평가자입니다.
    다음 평가 기준(rubric)을 참고하여 사용자가 작성한 이메일을 평가하고, 5가지 항목에 대해 각각 0점에서 100점 사이의 점수를 매겨주세요.
    모든 피드백은 한국어로 작성해야 합니다. 최종 결과는 반드시 지정된 JSON 형식으로 반환해야 합니다.

    <평가 기준>
    {EMAIL_RUBRIC}
    </평가 기준>

    ## 5대 평가 항목:
    1.  **구조·논리성**: 이메일 흐름의 체계성, 내용의 논리적 연결, 구조-내용-결론의 일관성을 평가합니다.
    2.  **목적 적합성**: 이메일 목적의 명확성, 핵심 배경·문제 정의의 적절성, 목적과 전체 문맥의 부합성을 평가합니다.
    3.  **내용 완성도**: 사실 근거의 정확성, 설명의 구체성, 표현의 명료성, 가독성을 평가합니다.
    4.  **실행 가능성**: (만약 제안이 포함된 경우) 제안의 현실적 수행 가능성, 설득력을 평가합니다.
    5.  **전문성·톤앤매너**: 조직/분야에 맞는 전문성, 이메일 종류에 부합하는 문체/톤, 불필요한 감정/미사여구 배제를 평가합니다.

    각 항목에 대해 긍정적인 점(good_points), 개선할 점(improvement_points), 그리고 이를 개선하기 위한 구체적인 제안(suggested_fix)을 포함한 상세한 피드백을 제공해야 합니다.
    마지막으로, 5개 항목의 점수 평균을 계산하여 'total_score'를 산출하고, 그에 맞는 'grade'와 종합적인 피드백('general_feedback')을 작성해주세요.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_email}
            ],
            response_model=EmailEvaluationResult,
            temperature=0.5,
        )

        if not response.total_score and response.evaluations:
            total = sum(item.score for item in response.evaluations)
            response.total_score = round(total / len(response.evaluations))

        return response

    except Exception as e:
        logger.error(f"이메일 평가 중 오류 발생: {e}")
        error_response = EmailEvaluationResult(
            evaluations=[],
            total_score=0,
            grade="Error",
            general_feedback=f"An error occurred during evaluation: {str(e)}"
        )
        return error_response
