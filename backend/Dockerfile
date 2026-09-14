FROM python:3.13-slim

# Render injects PORT at runtime; default 8002 keeps local Docker Compose working.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MALLOC_ARENA_MAX=2 \
    PORT=8002 \
    RENDER=true \
    VOICE_AGENT_LOW_RESOURCES=true

WORKDIR /app

# System deps kept minimal; psycopg2-binary ships as a wheel.
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]

