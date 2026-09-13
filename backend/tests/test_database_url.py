from app.core.database_url import database_url_mode, resolve_database_url


def test_normalizes_postgres_scheme():
    url = resolve_database_url("postgres://user:pass@localhost:5432/db")
    assert url.startswith("postgresql://")


def test_keeps_render_internal_url_without_ssl():
    url = resolve_database_url(
        "postgresql://user:pass@dpg-d9hsg984n6ts73bf6t7g-a/chatbot"
    )
    assert url == "postgresql://user:pass@dpg-d9hsg984n6ts73bf6t7g-a/chatbot"
    assert "sslmode" not in url
    assert database_url_mode(url) == "render-internal"


def test_external_url_adds_sslmode():
    url = resolve_database_url(
        "postgresql://user:pass@dpg-example-a.singapore-postgres.render.com/chatbot"
    )
    assert "sslmode=require" in url
    assert database_url_mode(url) == "render-external"


def test_database_external_url_env_takes_precedence():
    external = (
        "postgresql://user:pass@dpg-example-a.singapore-postgres.render.com/chatbot"
    )
    url = resolve_database_url(
        "postgresql://user:pass@dpg-old-a/chatbot",
        external=external,
    )
    assert "singapore-postgres.render.com" in url
    assert "sslmode=require" in url


def test_leaves_localhost_unchanged():
    url = resolve_database_url("postgresql://postgres:postgres@localhost:5432/chatbot")
    assert url == "postgresql://postgres:postgres@localhost:5432/chatbot"
    assert database_url_mode(url) == "standard"
