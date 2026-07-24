"""Helpers to ensure browser clients always receive CORS headers on error responses."""

import re

from starlette.requests import Request
from starlette.responses import Response

from app.core.config import settings

_VERCEL_ORIGIN = re.compile(r"^https://.*\.vercel\.app$")


def is_allowed_cors_origin(origin: str | None) -> bool:
    if not origin:
        return False
    return origin in settings.cors_origins_list or bool(_VERCEL_ORIGIN.match(origin))


def apply_cors_headers(request: Request, response: Response) -> Response:
    """Attach CORS headers when missing (e.g. custom exception handler responses)."""
    origin = request.headers.get("origin")
    if not origin or not is_allowed_cors_origin(origin):
        return response

    if "access-control-allow-origin" not in response.headers:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Vary"] = "Origin"
    return response
