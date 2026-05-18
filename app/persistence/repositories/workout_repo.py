from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.orm_models import WorkoutSession
from datetime import date


class WorkoutRepository:
    async def get_by_date(self, db: AsyncSession, workout_date: date) -> WorkoutSession | None:
        result = await db.execute(
            select(WorkoutSession).where(WorkoutSession.date == workout_date)
        )
        return result.scalar_one_or_none()

    async def get_recent(self, db: AsyncSession, limit: int = 10) -> list[WorkoutSession]:
        result = await db.execute(
            select(WorkoutSession).order_by(WorkoutSession.date.desc()).limit(limit)
        )
        return list(result.scalars().all())

    async def create(self, db: AsyncSession, session: WorkoutSession) -> WorkoutSession:
        db.add(session)
        await db.flush()
        return session
