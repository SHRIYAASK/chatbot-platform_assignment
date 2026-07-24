"""Rate limiting setup using slowapi.

Per-endpoint limits are applied in auth and chat routers via @limiter.limit().
There is no global default limit — read routes like GET /projects are unrestricted.
Limiting can be disabled entirely via RATE_LIMIT_ENABLED for local/dev/tests.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import settings

# Per-endpoint limits only (auth, chat). No global default — it was throttling
# read routes like GET /projects and masking 429s as CORS errors in the browser.
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[],
    enabled=settings.RATE_LIMIT_ENABLED,
)
