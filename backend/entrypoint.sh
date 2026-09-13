#!/bin/sh
set -e

echo "Waiting for database to become available..."
python - <<'PY'
import sys
import time
from urllib.parse import urlparse

from sqlalchemy import create_engine, text

from app.core.config import settings

parsed = urlparse(settings.DATABASE_URL)
print(f"Database host: {parsed.hostname}")

for attempt in range(1, 31):
    try:
        engine = create_engine(settings.DATABASE_URL)
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        print("Database is ready.")
        break
    except Exception as exc:  # noqa: BLE001
        print(f"Database not ready ({attempt}/30): {exc}")
        time.sleep(2)
else:
    sys.exit(
        "Database was not reachable in time. "
        "On Render, link the Postgres instance to this service or set "
        "DATABASE_EXTERNAL_URL to the External Database URL from the Postgres dashboard."
    )
PY

echo "Running database migrations..."
alembic upgrade head

echo "Starting API server..."
PORT="${PORT:-8002}"
export BACKEND_INTERNAL_URL="${BACKEND_INTERNAL_URL:-http://127.0.0.1:${PORT}}"
echo "Voice worker backend URL: ${BACKEND_INTERNAL_URL}"
exec uvicorn app.main:app --host 0.0.0.0 --port "$PORT"
