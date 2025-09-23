from typing import Union
from fastapi import FastAPI

from app.utils.logger import setup_logging, logger

setup_logging()
app = FastAPI()

@app.get("/")
def read_root():

    return "Hello, World!!"

@app.get("/user/{item_id}")
def read_id(item_id: int, q: Union[str, None] = None):
    return {'item_id': item_id, "query": q}


