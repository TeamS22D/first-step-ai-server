from typing import Union
from fastapi import FastAPI

from app.core.config import config
from app.utils.logger import setup_logging, logger

# import routes
from app.api.v1 import routes_ai, routes_log
from app.api import chat  # chat 라우터 import 추가

## import routes
from app.api.v1 import routes_document_evaluate

## init
setup_logging()
app = FastAPI(title=config.APP_NAME, debug=config.DEBUG)

## register routes
app.include_router(chat.router)
app.include_router(routes_document_evaluate.router, prefix="/api/v1/document", tags=["document_evaluation"])


@app.get("/")
def read_root():

    return "Hello, World!!"


@app.get("/user/{item_id}")
def read_id(item_id: int, q: Union[str, None] = None):
    return {'item_id': item_id, "query": q}


