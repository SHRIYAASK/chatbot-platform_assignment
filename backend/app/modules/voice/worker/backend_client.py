import json
import logging
from collections.abc import AsyncIterator

import httpx

logger = logging.getLogger("voice-backend-client")


async def stream_chat(
    *,
    backend_url: str,
    project_id: int,
    conversation_id: int,
    service_token: str,
    content: str,
) -> AsyncIterator[str]:
    url = (
        f"{backend_url.rstrip('/')}/projects/{project_id}/conversations/"
        f"{conversation_id}/voice/messages/stream"
    )
    headers = {
        "Authorization": f"Bearer {service_token}",
        "Content-Type": "application/json",
        "Accept": "text/event-stream",
    }

    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(120.0, connect=10.0)) as client:
            async with client.stream(
                "POST",
                url,
                json={"content": content},
                headers=headers,
            ) as response:
                if response.status_code >= 400:
                    body = await response.aread()
                    error_msg = f"Backend stream failed ({response.status_code}) on {url}: {body.decode(errors='replace')}"
                    logger.error(error_msg)
                    raise RuntimeError(error_msg)

                async for line in response.aiter_lines():
                    if not line.startswith("data:"):
                        continue
                    data = line[len("data:") :].strip()
                    if not data or data == "[DONE]":
                        break

                    payload = json.loads(data)
                    if "error" in payload:
                        error_msg = f"Backend SSE error: {payload['error']}"
                        logger.error(error_msg)
                        raise RuntimeError(error_msg)
                    delta = payload.get("delta")
                    if delta:
                        yield delta
    except Exception as exc:
        logger.error("stream_chat error connecting to %s: %s", url, exc)
        raise
