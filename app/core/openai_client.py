from __future__ import annotations

import time
import random
from typing import Union, List, Dict, Optional, Type, Iterable

from pydantic import BaseModel
from openai import OpenAI
from openai import (
    OpenAIError,
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    RateLimitError,
)

from app.core.config import config
from app.utils.logger import logger

client = OpenAI(
    api_key=config.OPENAI_API_KEY,
    timeout=30.0,
    max_retries=2
)

## 이러한 과정이 필요한 이유 찾아보기
_VALID_ROLES = {"system", "developer", "user", "assistant"}

def _sanitize_for_log(messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """로그에 민감정보가 남지 않도록 content 마스킹"""
    redacted = []
    for m in messages:
        content = m.get("content", "")
        redacted.append({
            "role": m.get("role", "unknown"),
            "content_preview": content[:80] + ("..." if len(content) > 80 else ""),
            "content_len": len(content),
        })
    return redacted

def _normalize_messages(
    user_prompt: str,
    developer_prompt: Optional[str],
    system_prompt: Optional[str],
    additional_messages: Optional[List[Dict[str, str]]],
) -> List[Dict[str, str]]:
    """role 기반 메시지 정규화"""
    messages: List[Dict[str, str]] = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    if developer_prompt:
        messages.append({"role": "developer", "content": developer_prompt})
    messages.append({"role": "user", "content": user_prompt})

    if additional_messages:
        for m in additional_messages:
            role = m.get("role")
            if role not in _VALID_ROLES:
                raise ValueError(f"Invalid role in additional_messages: {role}")
            messages.append({"role": role, "content": m.get("content", "")})
    return messages

def _as_stop_sequences(stop: Optional[Union[str, List[str]]]) -> Optional[List[str]]:
    """stop 문자열/리스트 정규화"""
    if stop is None:
        return None
    if isinstance(stop, str):
        return [stop]
    if isinstance(stop, list):
        return stop
    raise ValueError("stop must be None, str, or List[str]")

def _with_backoff_delays(retries: int) -> Iterable[float]:
    """지수 백오프 + 랜덤 지터"""
    base = 1.0
    for attempt in range(retries):
        jitter = random.uniform(0, 0.4)
        yield (base * (2 ** attempt)) + jitter

def ask_gpt(
        *,
        user_prompt: str,
        response_model: Type[BaseModel],
        model: str = "gpt-3.5-turbo",
        developer_prompt: Optional[str] = None,
        system_prompt: Optional[str] = None,
        additional_messages: Optional[List[Dict[str, str]]] = None,
        max_tokens: Optional[int] = None,
) -> "BaseModel":
    """
        GPT에 질의하고 Pydantic response_model로 파싱해서 결과를 반환합니다.

        :param user_prompt: 사용자 메시지
        :param response_model: 응답을 파싱할 Pydantic 모델 클래스
        :param model: 사용할 OpenAI 모델명 (기본값 gpt-3.5-turbo)
        :param developer_prompt: ‘developer’ 역할 프롬프트 (선택)
        :param system_prompt: ‘system’ 역할 프롬프트 (선택)
        :param additional_messages: 추가 메시지 리스트 [{"role": "...", "content": "..."}]
        :param max_tokens: 최대 토큰 수 제한
        :return: response_model 인스턴스
        :raises: APIError 등 예외 처리 필요
        """

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    if developer_prompt:
        messages.append({"role": "developer", "content": developer_prompt})
    messages.append({"role": "user", "content": user_prompt})
    if additional_messages:
        messages.extend(additional_messages)

    try:
        logger.info(f"OpenAI 요청\n model: {model} \n messages: {messages}")

        res = client.responses.parse(
            model=model,
            input=messages,
            max_output_tokens=max_tokens,
            text_format=response_model
        )

        return res.output_parsed

    except OpenAIError as e:
        logger.error(e)
        raise
    except APITimeoutError as e:
        logger.error(e)
        raise
    except Exception as e:
        logger.error(e)
        raise