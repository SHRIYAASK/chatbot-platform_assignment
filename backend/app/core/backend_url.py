import os


def resolve_backend_internal_url(explicit: str) -> str:
    """Resolve the URL the embedded voice worker uses to call this API.

    On Render the web service listens on ``PORT`` (usually 10000), not 8002.
    When unset or left at the local default, use loopback + the runtime port.
    """
    port = (os.environ.get("PORT") or "8002").strip() or "8002"
    value = (explicit or "").strip().rstrip("/")

    if "${PORT}" in value:
        return value.replace("${PORT}", port)

    local_defaults = {
        "",
        "http://127.0.0.1:8002",
        "http://localhost:8002",
    }
    if os.environ.get("RENDER") and value in local_defaults:
        return f"http://127.0.0.1:{port}"

    return value or f"http://127.0.0.1:{port}"
