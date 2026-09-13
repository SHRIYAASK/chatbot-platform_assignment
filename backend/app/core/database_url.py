import os
import socket
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

# Render Postgres external hostnames use: dpg-<id>-a.<region>-postgres.render.com
RENDER_POSTGRES_REGIONS = (
    "oregon",
    "ohio",
    "frankfurt",
    "singapore",
    "virginia",
)


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


def _region_from_external_url() -> str | None:
    external = os.environ.get("DATABASE_EXTERNAL_URL", "").strip()
    if not external:
        return None

    host = urlparse(normalize_postgres_scheme(external)).hostname or ""
    parts = host.split(".")
    if len(parts) >= 2 and parts[1].endswith("-postgres"):
        return parts[1].removesuffix("-postgres").lower()
    return None


def _configured_render_region() -> str | None:
    for key in ("RENDER_POSTGRES_REGION", "RENDER_REGION"):
        value = os.environ.get(key, "").strip().lower()
        if value:
            return value
    return _region_from_external_url()


def _discover_region_for_host(internal_host: str) -> str | None:
    for region in RENDER_POSTGRES_REGIONS:
        candidate = f"{internal_host}.{region}-postgres.render.com"
        try:
            socket.getaddrinfo(candidate, 5432, type=socket.SOCK_STREAM)
            return region
        except OSError:
            continue
    return None


def _replace_hostname(url: str, new_host: str) -> str:
    parsed = urlparse(url)
    if parsed.username:
        auth = parsed.username
        if parsed.password:
            auth = f"{parsed.username}:{parsed.password}"
        netloc = f"{auth}@{new_host}"
        if parsed.port:
            netloc = f"{netloc}:{parsed.port}"
    elif parsed.port:
        netloc = f"{new_host}:{parsed.port}"
    else:
        netloc = new_host
    return urlunparse(parsed._replace(netloc=netloc))


def expand_render_postgres_host(url: str) -> str:
    """Expand Render internal DB hostnames to resolvable external hostnames."""
    parsed = urlparse(url)
    host = parsed.hostname or ""
    if not _is_render_internal_postgres_host(host):
        return url

    region = _configured_render_region() or _discover_region_for_host(host)
    if not region:
        return url

    external_host = f"{host}.{region}-postgres.render.com"
    return _replace_hostname(url, external_host)


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
