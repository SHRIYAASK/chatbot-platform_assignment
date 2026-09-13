#!/bin/sh

PORT="${PORT:-8002}"
export BACKEND_INTERNAL_URL="${BACKEND_INTERNAL_URL:-http://127.0.0.1:${PORT}}"

echo "Checking database connectivity..."
if python - <<'PY'
import os
import sys
import time
from urllib.parse import urlparse

from sqlalchemy import create_engine, text

from app.core.config import settings
from app.core.database_url import database_url_mode, resolve_database_url

def _candidate_urls():
    urls = []
    primary = (os.environ.get("DATABASE_URL") or "").strip()
    external = (os.environ.get("DATABASE_EXTERNAL_URL") or "").strip()
    if external:
        urls.append(resolve_database_url("", external))
    if primary:
        resolved = resolve_database_url(primary, "")
        if resolved not in urls:
            urls.append(resolved)
    return urls or [settings.DATABASE_URL]

def _try_connect(url: str) -> bool:
    host = urlparse(url).hostname
    print(f"Trying database host: {host} ({database_url_mode(url)})")
    engine = create_engine(url, pool_pre_ping=True, pool_recycle=300)
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    finally:
        engine.dispose()

for url in _candidate_urls():
    for attempt in range(1, 6):
        try:
            if _try_connect(url):
                if url != os.environ.get("DATABASE_URL"):
                    os.environ["DATABASE_URL"] = url
                print("Database is ready.")
                sys.exit(0)
        except Exception as exc:  # noqa: BLE001
            message = str(exc)
            print(f"Database not ready ({attempt}/5): {exc}")
            if "could not translate host name" in message:
                break
            if "password authentication failed" in message:
                print(
                    "Password rejected — DATABASE_URL is stale. "
                    "On Render: Postgres → Connect → copy a fresh Internal or External URL, "
                    "replace DATABASE_URL on the web service (or unlink/re-link the database), then redeploy."
                )
                break
            time.sleep(2)

print(
    "ERROR: Could not connect to PostgreSQL.\n"
    "Fix on Render (Web Service → Environment):\n"
    "  1. Postgres → Connect → copy the current Internal Database URL.\n"
    "  2. Replace DATABASE_URL on the web service with that exact value.\n"
    "     (Or remove DATABASE_URL and Add from Database again to re-link.)\n"
    "  3. If using external access, set DATABASE_EXTERNAL_URL with ?sslmode=require.\n"
    "  4. Save and redeploy.\n"
    "Starting HTTP server anyway; /health/ready will stay not_ready until DB works."
)
sys.exit(1)
PY
then
    echo "Running database migrations..."
    alembic upgrade head
else
    echo "Skipping migrations until database is available."
fi

echo "Starting API server on 0.0.0.0:${PORT}..."
echo "Voice worker backend URL: ${BACKEND_INTERNAL_URL}"
exec uvicorn app.main:app --host 0.0.0.0 --port "$PORT"
