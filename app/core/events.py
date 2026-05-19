from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Awaitable, Callable


class EventType(str, Enum):
    WORKOUT_MISSED = "WORKOUT_MISSED"
    GOAL_STREAK = "GOAL_STREAK"
    RECOVERY_LOW = "RECOVERY_LOW"
    PLAN_UPDATED = "PLAN_UPDATED"
    HABIT_BROKEN = "HABIT_BROKEN"
    USER_INACTIVE = "USER_INACTIVE"


@dataclass(slots=True)
class Event:
    event_type: EventType
    user_id: str = "default"
    payload: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


Handler = Callable[[Event], Awaitable[None]]


class EventDispatcher:
    def __init__(self) -> None:
        self._subscribers: dict[EventType, list[Handler]] = defaultdict(list)

    def subscribe(self, event_type: EventType, handler: Handler) -> None:
        self._subscribers[event_type].append(handler)

    async def emit(self, event: Event) -> None:
        handlers = self._subscribers.get(event.event_type, [])
        for handler in handlers:
            await handler(event)


lightweight_dispatcher = EventDispatcher()
