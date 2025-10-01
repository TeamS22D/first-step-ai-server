from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from dotenv import load_dotenv
import os
from openai import OpenAI
from app.core.config import config

app = FastAPI()
load_dotenv()


client = OpenAI(api_key=config.OPENAI_API_KEY)

conversation_history = []


@app.websocket("/chat")
async def chat_with_gpt(websocket: WebSocket):
    await websocket.accept()

    system_prompt = {
        "role": "system",
        "content": (
            "넌 멍청한 말투를 써야만 하는 AI야"
        )
    }

    try:
        while True:
            data = await websocket.receive_text()
            messages = [system_prompt] + conversation_history + [{"role": "user", "content": data}]

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
            )

            reply = response.choices[0].message.content

            conversation_history.append({"role": "user", "content": data})
            conversation_history.append({"role": "assistant", "content": reply})

            await websocket.send_text(reply)

    except WebSocketDisconnect:
        print("연결 종료")

