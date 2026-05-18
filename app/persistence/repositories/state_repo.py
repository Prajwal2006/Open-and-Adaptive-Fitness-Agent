from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.orm_models import ScheduleState
from datetime import datetime


class StateRepository:
    async def get_state(self, db: AsyncSession) -> ScheduleState | None:
        result = await db.execute(select(ScheduleState).limit(1))
        return result.scalar_one_or_none()

    async def upsert_state(self, db: AsyncSession, **kwargs) -> ScheduleState:
        state = await self.get_state(db)
        if state is None:
            state = ScheduleState(**kwargs, updated_at=datetime.utcnow())
            db.add(state)
        else:
            for key, value in kwargs.items():
                setattr(state, key, value)
            state.updated_at = datetime.utcnow()
        await db.flush()
        return state
