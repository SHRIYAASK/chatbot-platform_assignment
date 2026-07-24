import asyncio
import logging
from typing import Any

import httpx

from app.core.config import settings
from app.modules.chat.services.llm_types import LLMResult

logger = logging.getLogger(__name__)

_http_client: httpx.AsyncClient | None = None


class LLMServiceError(Exception):
    """Raised when the LLM provider cannot produce a response."""


class LLMService:
    PLACEHOLDER_KEYS = {
        "",
        "your-groq-api-key",
        "changeme",
        "replace-me",
    }

    RETRIABLE_STATUS_CODES = {408, 429, 500, 502, 503, 504}

    @classmethod
    def _is_configured(cls) -> bool:
        api_key = settings.GROQ_API_KEY.strip()
        return api_key.lower() not in cls.PLACEHOLDER_KEYS

    @classmethod
    async def _get_client(cls) -> httpx.AsyncClient:
        global _http_client
        if _http_client is None or _http_client.is_closed:
            _http_client = httpx.AsyncClient(
                timeout=httpx.Timeout(60.0, connect=10.0),
                limits=httpx.Limits(max_connections=20, max_keepalive_connections=10),
            )
        return _http_client

    @classmethod
    async def close(cls) -> None:
        global _http_client
        if _http_client is not None and not _http_client.is_closed:
            await _http_client.aclose()
            _http_client = None

    @classmethod
    def _extract_error_detail(cls, response: httpx.Response) -> str:
        try:
            payload = response.json()
        except ValueError:
            return "The AI service returned an unexpected error."

        if not isinstance(payload, dict):
            return "The AI service returned an unexpected error."

        error = payload.get("error")
        if isinstance(error, dict):
            message = error.get("message")
            return str(message or error)
        if isinstance(error, str):
            return error

        detail = payload.get("detail")
        if detail:
            return str(detail)

        message = payload.get("message")
        if message:
            return str(message)

        return "The AI service returned an unexpected error."

    @classmethod
    def _parse_response(cls, data: dict[str, Any], model: str) -> LLMResult:
        try:
            choice = data["choices"][0]
            content = choice["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise LLMServiceError("The AI service returned an invalid response.") from exc

        token_count = None
        usage = data.get("usage")
        if isinstance(usage, dict):
            total_tokens = usage.get("total_tokens")
            if isinstance(total_tokens, int):
                token_count = total_tokens

        normalized_content = (content or "").strip()
        if not normalized_content:
            raise LLMServiceError("The AI service returned an empty response.")

        return LLMResult(
            content=normalized_content,
            model_used=data.get("model") or model,
            token_count=token_count,
        )

    @classmethod
    def _should_fallback(cls, response: httpx.Response | None, exc: Exception | None) -> bool:
        if exc is not None:
            return isinstance(
                exc,
                (
                    httpx.TimeoutException,
                    httpx.NetworkError,
                    httpx.RemoteProtocolError,
                    httpx.ReadError,
                    httpx.ConnectError,
                ),
            )

        if response is None:
            return True

        if response.status_code in cls.RETRIABLE_STATUS_CODES:
            return True

        detail = cls._extract_error_detail(response).lower()
        retriable_phrases = (
            "rate limit",
            "timeout",
            "temporarily unavailable",
            "model not found",
            "does not exist",
            "do not have access",
            "overloaded",
        )
        if response.status_code == 404:
            return True
        return any(phrase in detail for phrase in retriable_phrases)

    @classmethod
    async def _call_model(
        cls,
        model: str,
        messages: list[dict[str, str]],
    ) -> tuple[LLMResult | None, httpx.Response | None, Exception | None]:
        headers = {
            "Authorization": f"Bearer {settings.GROQ_API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model,
            "messages": messages,
            "temperature": 0.7,
        }
        url = f"{settings.GROQ_BASE_URL.rstrip('/')}/chat/completions"

        try:
            client = await cls._get_client()
            response = await client.post(url, json=payload, headers=headers)
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            logger.warning("Groq request failed for model %s: %s", model, exc)
            return None, None, exc

        if response.status_code >= 400:
            logger.warning(
                "Groq request returned %s for model %s: %s",
                response.status_code,
                model,
                cls._extract_error_detail(response),
            )
            return None, response, None

        try:
            return cls._parse_response(response.json(), model), response, None
        except LLMServiceError as exc:
            logger.warning("Groq response parsing failed for model %s: %s", model, exc)
            return None, response, exc

    @classmethod
    async def generate_reply(
        cls,
        messages: list[dict[str, str]],
        primary_model: str | None = None,
        fallback_model: str | None = None,
    ) -> LLMResult:
        if not cls._is_configured():
            raise LLMServiceError(
                "AI service is unavailable. Configure GROQ_API_KEY in backend/.env."
            )

        primary = primary_model or settings.PRIMARY_MODEL
        fallback = fallback_model or settings.FALLBACK_MODEL

        primary_result, primary_response, primary_exc = await cls._call_model(primary, messages)
        if primary_result is not None:
            return primary_result

        if not cls._should_fallback(primary_response, primary_exc):
            raise LLMServiceError(
                "The AI service is temporarily unavailable. Please try again."
            )

        logger.info("Primary model failed (%s). Retrying with fallback model.", primary)

        fallback_result, fallback_response, fallback_exc = await cls._call_model(fallback, messages)
        if fallback_result is not None:
            return fallback_result

        if fallback_response is not None:
            raise LLMServiceError(
                "The AI service is temporarily unavailable. Please try again."
            )

        if fallback_exc is not None:
            if isinstance(fallback_exc, httpx.TimeoutException):
                raise LLMServiceError("The AI service timed out. Please try again.") from fallback_exc
            raise LLMServiceError(
                "The AI service is temporarily unavailable. Please try again."
            ) from fallback_exc

        raise LLMServiceError("The AI service is temporarily unavailable. Please try again.")
