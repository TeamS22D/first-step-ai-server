from typing import Union
from fastapi import FastAPI
from app.core.config import config
from app.utils.logger import setup_logging, logger

# import routes
from app.api.v1 import routes_ai, routes_log
from app.api import chat
from fastapi.middleware.cors import CORSMiddleware

setup_logging()
app = FastAPI(title=config.APP_NAME, debug=config.DEBUG)

## 2. CORS 설정
origins = [
    "http://localhost:3000",
    "https://*.ngrok-free.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes_ai.router, prefix="/api/v1/ai", tags=["AI"])
app.include_router(routes_log.router, prefix="/api/v1/log", tags=["AI-log"])
app.include_router(chat.router)

@app.get("/")
def read_root():
    return "Hello, World!!"

@app.get("/user/{item_id}")
def read_id(item_id: int, q: Union[str, None] = None):
    return {'item_id': item_id, "query": q}