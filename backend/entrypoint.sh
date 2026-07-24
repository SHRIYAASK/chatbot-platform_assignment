#!/bin/sh
set -e

echo "Waiting for database to become available..."
python - <<'PY'
import sys
import time

from sqlalchemy import create_engine, text

from app.core.config import settings

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
    sys.exit("Database was not reachable in time.")
PY

echo "Running database migrations..."
alembic upgrade head

echo "Starting API server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8002
