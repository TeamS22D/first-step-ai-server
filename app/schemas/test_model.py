from pydantic import BaseModel

class TestRequest(BaseModel):
    id: str
    content: str

class AnswerRequest(BaseModel):
    mission_id: str
    rubric_id: str
    content: str

class EvaluationRequest(BaseModel):
    user_answer: str
    question: str
    rubric: str
    reference_answer: str = ""