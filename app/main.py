from typing import Union
from fastapi import FastAPI

from app.core.config import config
from app.utils.logger import setup_logging, logger

# import routes
from app.api.v1 import routes_ai

## init
setup_logging()
app = FastAPI(title=config.APP_NAME, debug=config.DEBUG)

## register routes
app.include_router(routes_ai.router, prefix="/api/v1/ai", tags=["AI"])


@app.get("/")
def read_root():

    return "Hello, World!!"


@app.get("/user/{item_id}")
def read_id(item_id: int, q: Union[str, None] = None):
    return {'item_id': item_id, "query": q}


