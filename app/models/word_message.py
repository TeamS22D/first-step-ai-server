from pydantic import BaseModel


class WordMessage(BaseModel):
    message: str