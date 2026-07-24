"""Centralized exception handlers.

Keeps HTTP error mapping in one place so routers stay focused on the happy path
and internal errors never leak stack traces to clients.
"""

import logging

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from jose import ExpiredSignatureError, JWTError
from sqlalchemy.exc import OperationalError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.cors import apply_cors_headers
from app.shared.exceptions import (
    AppException,
    AuthorizationError,
    DuplicateResourceError,
    ResourceNotFoundError,
)
from app.shared.guardrails.exceptions import InputValidationError

logger = logging.getLogger(__name__)


def _json_response(request: Request, status_code: int, content: dict, headers: dict | None = None):
    response = JSONResponse(status_code=status_code, content=content, headers=headers or {})
    return apply_cors_headers(request, response)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def _request_validation(request: Request, exc: RequestValidationError):
        return _json_response(
            request,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            {"detail": jsonable_encoder(exc.errors())},
        )

    @app.exception_handler(StarletteHTTPException)
    async def _http_exception(request: Request, exc: StarletteHTTPException):
        headers = dict(exc.headers) if exc.headers else None
        return _json_response(request, exc.status_code, {"detail": exc.detail}, headers=headers)

    @app.exception_handler(OperationalError)
    async def _database_error(request: Request, exc: OperationalError):
        logger.error("Database connection failure: %s", exc)
        return _json_response(
            request,
            status.HTTP_503_SERVICE_UNAVAILABLE,
            {"detail": "Database connection failure"},
        )

    @app.exception_handler(ExpiredSignatureError)
    async def _expired_token(request: Request, exc: ExpiredSignatureError):
        return _json_response(
            request,
            status.HTTP_401_UNAUTHORIZED,
            {"detail": "Token has expired"},
            headers={"WWW-Authenticate": "Bearer"},
        )

    @app.exception_handler(JWTError)
    async def _jwt_error(request: Request, exc: JWTError):
        return _json_response(
            request,
            status.HTTP_401_UNAUTHORIZED,
            {"detail": "Invalid token"},
            headers={"WWW-Authenticate": "Bearer"},
        )

    @app.exception_handler(InputValidationError)
    async def _input_validation(request: Request, exc: InputValidationError):
        return _json_response(
            request,
            status.HTTP_400_BAD_REQUEST,
            {"detail": str(exc)},
        )

    @app.exception_handler(DuplicateResourceError)
    async def _duplicate(request: Request, exc: DuplicateResourceError):
        return _json_response(
            request,
            status.HTTP_409_CONFLICT,
            {"detail": exc.message},
        )

    @app.exception_handler(ResourceNotFoundError)
    async def _not_found(request: Request, exc: ResourceNotFoundError):
        return _json_response(
            request,
            status.HTTP_404_NOT_FOUND,
            {"detail": exc.message},
        )

    @app.exception_handler(AuthorizationError)
    async def _authorization(request: Request, exc: AuthorizationError):
        return _json_response(
            request,
            status.HTTP_403_FORBIDDEN,
            {"detail": exc.message},
        )

    @app.exception_handler(AppException)
    async def _app_exception(request: Request, exc: AppException):
        return _json_response(
            request,
            status.HTTP_400_BAD_REQUEST,
            {"detail": exc.message},
        )

    @app.exception_handler(Exception)
    async def _unhandled(request: Request, exc: Exception):
        logger.exception("Unhandled error on %s %s", request.method, request.url.path)
        return _json_response(
            request,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            {"detail": "Internal server error"},
        )
