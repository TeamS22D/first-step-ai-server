from pydantic import BaseModel

class WordDescription(BaseModel):
    name: str
    description: str