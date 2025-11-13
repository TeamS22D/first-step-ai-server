from pydantic import BaseModel

class TestRequest(BaseModel):
    id: str
    content: str

class AnswerRequest(BaseModel):
    mission_id: str
    rubric_id: str
    content: str