"""Test harness.

Runs the full app against an isolated SQLite database so tests need no
external Postgres. Environment is configured before app modules import so
settings pick up the test values.
"""

import os
from uuid import uuid4

os.environ["DATABASE_URL"] = "sqlite:///./test_app.db"
os.environ["SECRET_KEY"] = "test-secret-key-that-is-long-enough-1234567890"
os.environ["MODERATION_ENABLED"] = "false"
os.environ["GROQ_API_KEY"] = ""
os.environ["STORAGE_PROVIDER"] = "local"
os.environ["EMBEDDING_PROVIDER"] = "hash"
os.environ["RAG_ENABLED"] = "true"
os.environ["AUTO_MIGRATE"] = "false"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import event  # noqa: E402

import app.main as main_module  # noqa: E402
from app.core.database import Base, engine  # noqa: E402


@event.listens_for(engine, "connect")
def _enable_sqlite_foreign_keys(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


@pytest.fixture(scope="session", autouse=True)
def _setup_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    if os.path.exists("test_app.db"):
        try:
            os.remove("test_app.db")
        except OSError:
            pass


@pytest.fixture()
def client():
    with TestClient(main_module.app) as test_client:
        yield test_client


@pytest.fixture()
def auth_headers(client):
    email = f"user_{uuid4().hex[:8]}@example.com"
    password = "Passw0rd!"
    register = client.post(
        "/auth/register",
        json={
            "name": "Test User",
            "email": email,
            "password": password,
            "confirm_password": password,
        },
    )
    assert register.status_code == 201, register.text

    login = client.post("/auth/login", json={"email": email, "password": password})
    assert login.status_code == 200, login.text
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
