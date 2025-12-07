from pydantic import BaseModel

class DocumentEvaluationRequest(BaseModel):
    mission_id: str
    user_mission: str