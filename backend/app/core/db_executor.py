"""Run blocking SQLAlchemy work off the async event loop.

The chat send path is async (Groq HTTP) but uses the sync Session API.
Each helper opens its own session so work can safely run via anyio.to_thread.
"""

from collections.abc import Callable
from typing import TypeVar

import anyio

T = TypeVar("T")


async def run_sync_db(operation: Callable[[], T]) -> T:
    """Execute a sync DB callable in a worker thread."""
    return await anyio.to_thread.run_sync(operation)
