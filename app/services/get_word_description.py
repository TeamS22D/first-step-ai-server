from json import JSONDecodeError

from fastapi import Response
from openai import APIConnectionError
from .get_openapi import  use_message
from app.utils.logger import logger
import json




async def get_word_description(model: str = "gpt-3.5-turbo", message: str = None) -> Response:
    try:
        logger.info(f"Getting word description for {model}")
        content = await use_message(model=model, message=message)
        return Response(json.loads(content.output_text).message, status_code=200)
    except JSONDecodeError as e:
        logger.error(f"Failed to get word description for {model}: {e}")
        return Response("json변환 도중 오류가 발생했습니다.", status_code=500)

    except APIConnectionError as e:
        logger.error(f"Can't connect to {model}: {e}")
        return Response("인터넷에 연결할 수 없습니다.", status_code=500)


