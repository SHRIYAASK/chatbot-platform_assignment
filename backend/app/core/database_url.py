from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse


def normalize_postgres_scheme(url: str) -> str:
    value = (url or "").strip()
    if value.startswith("postgres://"):
        return "postgresql://" + value[len("postgres://") :]
    return value


def _ensure_query_param(url: str, key: str, value: str) -> str:
    parsed = urlparse(url)
    params = dict(parse_qsl(parsed.query, keep_blank_values=True))
    params.setdefault(key, value)
    return urlunparse(parsed._replace(query=urlencode(params)))


def _is_render_internal_postgres_host(host: str) -> bool:
    """Render private-network hostname, e.g. dpg-xxxxx-a (no domain suffix)."""
    return host.startswith("dpg-") and host.endswith("-a") and "." not in host


def ensure_ssl_for_external_render(url: str) -> str:
    """External Render Postgres requires TLS."""
    parsed = urlparse(url)
    host = parsed.hostname or ""
    if host.endswith(".render.com"):
        return _ensure_query_param(url, "sslmode", "require")
    return url


def resolve_database_url(primary: str, external: str = "") -> str:
    """Resolve the database URL for the current environment.

    Render guidance:
    - Same-region web service + Postgres: use Internal Database URL as-is (no SSL).
    - External connections: use External Database URL with ``?sslmode=require``.
    - When both are set, prefer the linked internal ``DATABASE_URL``.
    """
    primary_url = normalize_postgres_scheme((primary or "").strip())
    explicit_external = normalize_postgres_scheme((external or "").strip())

    if primary_url:
        host = urlparse(primary_url).hostname or ""
        if _is_render_internal_postgres_host(host):
            return primary_url
        if host.endswith(".render.com"):
            return ensure_ssl_for_external_render(primary_url)
        return primary_url

    if explicit_external:
        return ensure_ssl_for_external_render(explicit_external)

    return ""


def database_url_mode(url: str) -> str:
    host = urlparse(url).hostname or ""
    if _is_render_internal_postgres_host(host):
        return "render-internal"
    if host.endswith(".render.com"):
        return "render-external"
    return "standard"
