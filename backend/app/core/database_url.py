import os
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
    return host.startswith("dpg-") and host.endswith("-a") and "." not in host


def expand_render_postgres_host(url: str) -> str:
    """Render internal DB URLs use short hostnames that may not resolve.

    Expand ``dpg-xxxxx-a`` to ``dpg-xxxxx-a.<region>-postgres.render.com`` when
    running on Render so DNS lookup succeeds from the web service.
    """
    parsed = urlparse(url)
    host = parsed.hostname or ""
    if not _is_render_internal_postgres_host(host):
        return url

    region = os.environ.get("RENDER_REGION", "").strip().lower()
    if not region:
        return url

    external_host = f"{host}.{region}-postgres.render.com"
    if parsed.port:
        netloc = f"{parsed.username}:{parsed.password}@{external_host}:{parsed.port}"
    elif parsed.username:
        password = f":{parsed.password}" if parsed.password else ""
        netloc = f"{parsed.username}{password}@{external_host}"
    else:
        netloc = external_host

    return urlunparse(parsed._replace(netloc=netloc))


def ensure_ssl_for_render(url: str) -> str:
    parsed = urlparse(url)
    host = parsed.hostname or ""
    if host.endswith(".render.com"):
        return _ensure_query_param(url, "sslmode", "require")
    return url


def resolve_database_url(primary: str, external: str = "") -> str:
    url = normalize_postgres_scheme((external or primary or "").strip())
    url = expand_render_postgres_host(url)
    url = ensure_ssl_for_render(url)
    return url
