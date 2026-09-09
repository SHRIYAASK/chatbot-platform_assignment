import os

from app.core.database_url import resolve_database_url


def test_normalizes_postgres_scheme():
    url = resolve_database_url("postgres://user:pass@localhost:5432/db")
    assert url.startswith("postgresql://")


def test_expands_render_internal_host(monkeypatch):
    monkeypatch.setenv("RENDER_REGION", "oregon")
    url = resolve_database_url(
        "postgresql://user:pass@dpg-d9hsg984n6ts73bf6t7g-a/chatbot"
    )
    assert (
        url
        == "postgresql://user:pass@dpg-d9hsg984n6ts73bf6t7g-a.oregon-postgres.render.com/chatbot?sslmode=require"
    )


def test_external_url_takes_precedence(monkeypatch):
    monkeypatch.setenv("RENDER_REGION", "oregon")
    external = (
        "postgresql://user:pass@dpg-example-a.singapore-postgres.render.com/chatbot"
    )
    url = resolve_database_url(
        "postgresql://user:pass@dpg-old-a/chatbot",
        external=external,
    )
    assert "singapore-postgres.render.com" in url
    assert "sslmode=require" in url


def test_leaves_localhost_unchanged(monkeypatch):
    monkeypatch.delenv("RENDER_REGION", raising=False)
    url = resolve_database_url("postgresql://postgres:postgres@localhost:5432/chatbot")
    assert url == "postgresql://postgres:postgres@localhost:5432/chatbot"
