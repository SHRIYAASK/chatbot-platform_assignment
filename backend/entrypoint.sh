#!/bin/sh

PORT="${PORT:-8002}"
export BACKEND_INTERNAL_URL="${BACKEND_INTERNAL_URL:-http://127.0.0.1:${PORT}}"

echo "Checking database connectivity..."
if python - <<'PY'
import sys
import time
from urllib.parse import urlparse

from sqlalchemy import create_engine, text

from app.core.config import settings
from app.core.database_url import database_url_mode

parsed = urlparse(settings.DATABASE_URL)
print(f"Database host: {parsed.hostname} ({database_url_mode(settings.DATABASE_URL)})")

for attempt in range(1, 11):
    try:
        engine = create_engine(
            settings.DATABASE_URL,
            pool_pre_ping=True,
            pool_recycle=300,
        )
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        engine.dispose()
        print("Database is ready.")
        sys.exit(0)
    except Exception as exc:  # noqa: BLE001
        print(f"Database not ready ({attempt}/10): {exc}")
        time.sleep(2)

print(
    "WARNING: Database was not reachable after 10 attempts. "
    "Starting HTTP server anyway; /health/ready will return not_ready until the DB is up. "
    "On Render: link Postgres to this service and use the Internal Database URL, "
    "or set DATABASE_EXTERNAL_URL with ?sslmode=require."
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
