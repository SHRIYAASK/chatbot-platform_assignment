"""Rate limiting setup using slowapi.

A single shared limiter is created here so routers can apply per-endpoint limits.
Limiting can be disabled entirely via RATE_LIMIT_ENABLED for local/dev/tests.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import settings

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[settings.RATE_LIMIT_DEFAULT] if settings.RATE_LIMIT_ENABLED else [],
    enabled=settings.RATE_LIMIT_ENABLED,
)
