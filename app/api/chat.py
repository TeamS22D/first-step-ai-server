from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import os
from openai import OpenAI
from app.core.config import config

app = FastAPI()
load_dotenv()


client = OpenAI(api_key=config.OPENAI_API_KEY)

conversation_history = []

class UserMessage(BaseModel):
    message: str

@app.post("/chat/")
async def chat_with_gpt(request: UserMessage):
    try:
        system_prompt = {
            "role": "system",
            "content": (
                "넌 고집이 세상에서 가장 쎈 어떤 회사의 팀장이야. "
                "항상 고집 센 성격으로 답하고, 절대 유저 말에 쉽게 동의하지 않아."
            )
        }

        messages = [system_prompt] + conversation_history + [{"role": "user", "content": request.message}]

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
        )

        reply = response.choices[0].message.content

        conversation_history.append({"role": "user", "content": request.message})
        conversation_history.append({"role": "assistant", "content": reply})

        return {"response": reply}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

