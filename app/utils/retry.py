from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import TypeVar

from app.config.settings import settings

T = TypeVar("T")


async def run_with_retry(fn: Callable[[], Awaitable[T]]) -> T:
    last_error: Exception | None = None
    for attempt in range(1, settings.RETRY_ATTEMPTS + 1):
        try:
            return await fn()
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            if attempt >= settings.RETRY_ATTEMPTS:
                break
            await asyncio.sleep(settings.RETRY_BACKOFF_SECONDS * attempt)
    assert last_error is not None
    raise last_error
