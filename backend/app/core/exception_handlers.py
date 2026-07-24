"""Centralized exception handlers.

Keeps HTTP error mapping in one place so routers stay focused on the happy path
and internal errors never leak stack traces to clients.
"""

import logging

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from jose import ExpiredSignatureError, JWTError
from sqlalchemy.exc import OperationalError

from app.shared.exceptions import (
    AppException,
    AuthorizationError,
    DuplicateResourceError,
    ResourceNotFoundError,
)
from app.shared.guardrails.exceptions import InputValidationError

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(OperationalError)
    async def _database_error(request: Request, exc: OperationalError):
        logger.error("Database connection failure: %s", exc)
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"detail": "Database connection failure"},
        )

    @app.exception_handler(ExpiredSignatureError)
    async def _expired_token(request: Request, exc: ExpiredSignatureError):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Token has expired"},
            headers={"WWW-Authenticate": "Bearer"},
        )

    @app.exception_handler(JWTError)
    async def _jwt_error(request: Request, exc: JWTError):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Invalid token"},
            headers={"WWW-Authenticate": "Bearer"},
        )

    @app.exception_handler(InputValidationError)
    async def _input_validation(request: Request, exc: InputValidationError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": str(exc)},
        )

    @app.exception_handler(DuplicateResourceError)
    async def _duplicate(request: Request, exc: DuplicateResourceError):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": exc.message},
        )

    @app.exception_handler(ResourceNotFoundError)
    async def _not_found(request: Request, exc: ResourceNotFoundError):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": exc.message},
        )

    @app.exception_handler(AuthorizationError)
    async def _authorization(request: Request, exc: AuthorizationError):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"detail": exc.message},
        )

    @app.exception_handler(AppException)
    async def _app_exception(request: Request, exc: AppException):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": exc.message},
        )

    @app.exception_handler(Exception)
    async def _unhandled(request: Request, exc: Exception):
        logger.exception("Unhandled error on %s %s", request.method, request.url.path)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
        )
