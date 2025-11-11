from pydantic import BaseModel

class TestRequest(BaseModel):
    id: str
    content: str