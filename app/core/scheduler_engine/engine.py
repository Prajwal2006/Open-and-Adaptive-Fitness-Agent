from datetime import date, datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.orm_models import ScheduleState, WorkoutSession
from app.config.settings import settings
from typing import Optional


class SchedulerEngine:
    def __init__(self):
        self.split = settings.DEFAULT_SPLIT

    async def _get_or_create_state(self, db: AsyncSession) -> ScheduleState:
        result = await db.execute(select(ScheduleState).limit(1))
        state = result.scalar_one_or_none()
        if state is None:
            state = ScheduleState(
                current_position=0,
                consecutive_misses=0,
                shift_offset=0,
                updated_at=datetime.utcnow(),
            )
            db.add(state)
            await db.flush()
        return state

    async def get_split_position(self, db: AsyncSession) -> int:
        state = await self._get_or_create_state(db)
        return state.current_position % len(self.split)

    async def get_today_workout(self, db: AsyncSession) -> dict:
        position = await self.get_split_position(db)
        split_type = self.split[position]
        next_pos = (position + 1) % len(self.split)
        next_split = self.split[next_pos]
        return {
            "date": date.today(),
            "split_type": split_type,
            "position": position,
            "is_rest_day": split_type == "Rest",
            "next_workout": next_split,
        }

    async def get_next_workout(self, db: AsyncSession) -> dict:
        position = await self.get_split_position(db)
        next_pos = (position + 1) % len(self.split)
        split_type = self.split[next_pos]
        return {
            "date": (date.today() + timedelta(days=1)),
            "split_type": split_type,
            "position": next_pos,
            "is_rest_day": split_type == "Rest",
        }

    async def mark_workout_complete(self, db: AsyncSession, session_id: int) -> None:
        state = await self._get_or_create_state(db)
        state.current_position = (state.current_position + 1) % len(self.split)
        state.last_completed_date = date.today()
        state.consecutive_misses = 0
        state.updated_at = datetime.utcnow()
        await db.flush()

    async def shift_schedule_forward(self, db: AsyncSession, days: int = 1) -> None:
        state = await self._get_or_create_state(db)
        state.shift_offset = (state.shift_offset or 0) + days
        state.updated_at = datetime.utcnow()
        await db.flush()

    async def detect_missed_workout(self, db: AsyncSession) -> bool:
        state = await self._get_or_create_state(db)
        if state.last_completed_date is None:
            return False
        yesterday = date.today() - timedelta(days=1)
        if state.last_completed_date < yesterday:
            yesterday_split_pos = (state.current_position - 1) % len(self.split)
            yesterday_split = self.split[yesterday_split_pos]
            if yesterday_split != "Rest":
                return True
        return False
