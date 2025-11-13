from app.models.DocumentEvaluation import DocumentEvaluation
evaluate_log = []


def save_evaluate_log(rubric_id: str, mission_id: str, user_prompt: str, result: DocumentEvaluation):
    """사용자가 작성한 문서를 로그로 저장합니다. 서버가 중단되면 기록도 삭제됩니다."""
    user_log = {"rubric_id": rubric_id, "mission_id": mission_id, "user_prompt": user_prompt, "result": result}
    evaluate_log.append(user_log)

def get_all_evaluate_log():
    return evaluate_log