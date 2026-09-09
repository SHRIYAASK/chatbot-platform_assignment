import json
from collections.abc import AsyncIterator

import httpx


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

    async with httpx.AsyncClient(timeout=httpx.Timeout(120.0, connect=10.0)) as client:
        async with client.stream(
            "POST",
            url,
            json={"content": content},
            headers=headers,
        ) as response:
            if response.status_code >= 400:
                body = await response.aread()
                raise RuntimeError(
                    f"Backend stream failed ({response.status_code}): {body.decode(errors='replace')}"
                )

            async for line in response.aiter_lines():
                if not line.startswith("data:"):
                    continue
                data = line[len("data:") :].strip()
                if not data or data == "[DONE]":
                    break

                payload = json.loads(data)
                if "error" in payload:
                    raise RuntimeError(str(payload["error"]))
                delta = payload.get("delta")
                if delta:
                    yield delta
