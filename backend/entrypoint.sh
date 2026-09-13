#!/bin/sh

PORT="${PORT:-8002}"
export BACKEND_INTERNAL_URL="${BACKEND_INTERNAL_URL:-http://127.0.0.1:${PORT}}"
DATABASE_URL_FILE="/tmp/working_database_url"

rm -f "$DATABASE_URL_FILE"

echo "Checking database connectivity..."
if DATABASE_URL_FILE="$DATABASE_URL_FILE" python - <<'PY'
import os
import subprocess
import sys
import time
from urllib.parse import urlparse

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text

from app.core.database_url import database_url_mode, resolve_database_url

DATABASE_URL_FILE = os.environ.get("DATABASE_URL_FILE", "/tmp/working_database_url")


def _candidate_urls():
    urls = []
    primary = (os.environ.get("DATABASE_URL") or "").strip()
    external = (os.environ.get("DATABASE_EXTERNAL_URL") or "").strip()
    # Try linked internal URL first — it is the canonical credential on Render.
    if primary:
        resolved = resolve_database_url(primary, "")
        urls.append(resolved)
    if external:
        resolved = resolve_database_url("", external)
        if resolved not in urls:
            urls.append(resolved)
    return urls


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


def _run_migrations(url: str) -> None:
    migration_env = os.environ.copy()
    migration_env["DATABASE_URL"] = url
    migration_env.pop("DATABASE_EXTERNAL_URL", None)

    cfg = Config("alembic.ini")
    cfg.set_main_option("sqlalchemy.url", url)
    command.upgrade(cfg, "head")


working_url = None
for url in _candidate_urls():
    for attempt in range(1, 6):
        try:
            if _try_connect(url):
                working_url = url
                break
        except Exception as exc:  # noqa: BLE001
            message = str(exc)
            print(f"Database not ready ({attempt}/5): {exc}")
            if "could not translate host name" in message:
                break
            if "password authentication failed" in message:
                print(
                    "Password rejected for this URL. "
                    "Remove stale DATABASE_EXTERNAL_URL or refresh DATABASE_URL from Render Postgres → Connect."
                )
                break
            time.sleep(2)
    if working_url:
        break

if not working_url:
    print(
        "ERROR: Could not connect to PostgreSQL.\n"
        "Fix on Render (Web Service → Environment):\n"
        "  1. Remove DATABASE_EXTERNAL_URL if it has an old/wrong password.\n"
        "  2. Postgres → Connect → copy Internal Database URL into DATABASE_URL.\n"
        "  3. Or unlink/re-link the database to refresh credentials.\n"
        "  4. Save and redeploy.\n"
        "Starting HTTP server anyway; /health/ready will stay not_ready until DB works."
    )
    sys.exit(1)

print("Database is ready.")
print("Running database migrations...")
_run_migrations(working_url)

with open(DATABASE_URL_FILE, "w", encoding="utf-8") as handle:
    handle.write(working_url)

print("Migrations complete.")
sys.exit(0)
PY
then
    if [ -f "$DATABASE_URL_FILE" ]; then
        export DATABASE_URL="$(cat "$DATABASE_URL_FILE")"
        unset DATABASE_EXTERNAL_URL
        rm -f "$DATABASE_URL_FILE"
    fi
else
    echo "Skipping migrations until database is available."
fi

echo "Starting API server on 0.0.0.0:${PORT}..."
echo "Voice worker backend URL: ${BACKEND_INTERNAL_URL}"
exec uvicorn app.main:app --host 0.0.0.0 --port "$PORT"
