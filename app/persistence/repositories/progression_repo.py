from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.orm_models import ProgressionHistory


class ProgressionRepository:
    async def get_by_exercise(self, db: AsyncSession, exercise_name: str, limit: int = 10) -> list[ProgressionHistory]:
        result = await db.execute(
            select(ProgressionHistory)
            .where(ProgressionHistory.exercise_name == exercise_name)
            .order_by(ProgressionHistory.date.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
