from fastapi import APIRouter

from app.services.get_word_description import get_word_description

from app.models.word_message import WordMessage

router = APIRouter()


@router.get("/word-description")
async def word_description(message: WordMessage):
    return await get_word_description(message=message.message)