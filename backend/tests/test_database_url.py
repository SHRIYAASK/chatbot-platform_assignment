import os
import socket

from app.core.database_url import resolve_database_url


def test_normalizes_postgres_scheme():
    url = resolve_database_url("postgres://user:pass@localhost:5432/db")
    assert url.startswith("postgresql://")


def test_expands_render_internal_host_with_region_env(monkeypatch):
    monkeypatch.setenv("RENDER_POSTGRES_REGION", "oregon")
    url = resolve_database_url(
        "postgresql://user:pass@dpg-d9hsg984n6ts73bf6t7g-a/chatbot"
    )
    assert (
        url
        == "postgresql://user:pass@dpg-d9hsg984n6ts73bf6t7g-a.oregon-postgres.render.com/chatbot?sslmode=require"
    )


def test_expands_render_internal_host_via_dns_discovery(monkeypatch):
    monkeypatch.delenv("RENDER_REGION", raising=False)
    monkeypatch.delenv("RENDER_POSTGRES_REGION", raising=False)
    monkeypatch.delenv("DATABASE_EXTERNAL_URL", raising=False)

    def fake_getaddrinfo(host, port, *args, **kwargs):
        if host.endswith(".singapore-postgres.render.com"):
            return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("10.0.0.1", 5432))]
        raise socket.gaierror("Name or service not known")

    monkeypatch.setattr(socket, "getaddrinfo", fake_getaddrinfo)

    url = resolve_database_url(
        "postgresql://user:pass@dpg-d9hsg984n6ts73bf6t7g-a/chatbot"
    )
    assert "dpg-d9hsg984n6ts73bf6t7g-a.singapore-postgres.render.com" in url
    assert "sslmode=require" in url


def test_external_url_takes_precedence(monkeypatch):
    monkeypatch.setenv("RENDER_POSTGRES_REGION", "oregon")
    external = (
        "postgresql://user:pass@dpg-example-a.singapore-postgres.render.com/chatbot"
    )
    url = resolve_database_url(
        "postgresql://user:pass@dpg-old-a/chatbot",
        external=external,
    )
    assert "singapore-postgres.render.com" in url
    assert "sslmode=require" in url


def test_region_from_database_external_url_env(monkeypatch):
    monkeypatch.delenv("RENDER_POSTGRES_REGION", raising=False)
    monkeypatch.setenv(
        "DATABASE_EXTERNAL_URL",
        "postgresql://user:pass@dpg-d9hsg984n6ts73bf6t7g-a.frankfurt-postgres.render.com/chatbot",
    )
    url = resolve_database_url(
        "postgresql://user:pass@dpg-d9hsg984n6ts73bf6t7g-a/chatbot"
    )
    assert "frankfurt-postgres.render.com" in url


def test_leaves_localhost_unchanged(monkeypatch):
    monkeypatch.delenv("RENDER_REGION", raising=False)
    url = resolve_database_url("postgresql://postgres:postgres@localhost:5432/chatbot")
    assert url == "postgresql://postgres:postgres@localhost:5432/chatbot"
