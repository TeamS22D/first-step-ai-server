from typing import Union
from fastapi import FastAPI

from app.core.config import config
from app.utils.logger import setup_logging, logger

## import routes
from app.api.v1 import routes_ai, routes_word_description

## init
setup_logging()
app = FastAPI(title=config.APP_NAME, debug=config.DEBUG)

## register routes
app.include_router(routes_ai.router, prefix="/api/v1/ai", tags=["AI"])
app.include_router(routes_word_description.router, prefix="/api/v1/gpt", tags=["AI-2"])


@app.get("/")
def read_root():

    return "Hello, World!!"


@app.get("/user/{item_id}")
def read_id(item_id: int, q: Union[str, None] = None):
    return {'item_id': item_id, "query": q}


