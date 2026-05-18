import asyncio
import json
from typing import Callable, Awaitable
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.event_engine.events import FitnessEvent, FitnessEventType
from app.models.orm_models import EventHistory
from datetime import datetime, timezone


HandlerType = Callable[[FitnessEvent, AsyncSession], Awaitable[None]]


class EventDispatcher:
    def __init__(self):
        self._subscribers: dict[FitnessEventType, list[HandlerType]] = {}
        self._queue: asyncio.Queue = asyncio.Queue()

    def subscribe(self, event_type: FitnessEventType, handler: HandlerType) -> None:
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)

    async def dispatch(self, event: FitnessEvent, db: AsyncSession) -> None:
        handlers = self._subscribers.get(event.event_type, [])
        for handler in handlers:
            try:
                await handler(event, db)
            except Exception:
                pass
        event.processed = True

    async def dispatch_and_store(self, event: FitnessEvent, db: AsyncSession) -> None:
        await self.dispatch(event, db)
        history = EventHistory(
            event_type=event.event_type.value,
            payload_json=json.dumps(event.payload),
            processed=event.processed,
            created_at=event.timestamp or datetime.now(timezone.utc),
        )
        db.add(history)
        await db.flush()


dispatcher = EventDispatcher()
