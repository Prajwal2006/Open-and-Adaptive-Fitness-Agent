from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.orm_models import WorkoutSession, ExerciseLog
from app.config.settings import settings
from datetime import date, timedelta
from typing import Optional


class AnalyticsEngine:
    async def calculate_consistency(self, db: AsyncSession, days: int = 30) -> float:
        cutoff = date.today() - timedelta(days=days)
        result = await db.execute(
            select(func.count(WorkoutSession.id))
            .where(WorkoutSession.completed == True)
            .where(WorkoutSession.date >= cutoff)
            .where(WorkoutSession.split_type != "Rest")
        )
        done = result.scalar_one() or 0
        planned = int(days * (5 / 7))
        if planned == 0:
            return 0.0
        return min(1.0, round(done / planned, 3))

    async def summarize_recent_workouts(self, db: AsyncSession, limit: int = 5) -> list[dict]:
        result = await db.execute(
            select(WorkoutSession)
            .order_by(WorkoutSession.date.desc())
            .limit(limit)
        )
        sessions = result.scalars().all()
        return [
            {
                "date": s.date.isoformat(),
                "type": s.split_type,
                "done": s.completed,
                "duration": s.duration_minutes,
            }
            for s in sessions
        ]

    async def detect_training_trends(self, db: AsyncSession) -> dict:
        cutoff_recent = date.today() - timedelta(days=14)
        cutoff_prior = date.today() - timedelta(days=28)

        result_recent = await db.execute(
            select(func.count(WorkoutSession.id))
            .where(WorkoutSession.completed == True)
            .where(WorkoutSession.date >= cutoff_recent)
        )
        recent_count = result_recent.scalar_one() or 0

        result_prior = await db.execute(
            select(func.count(WorkoutSession.id))
            .where(WorkoutSession.completed == True)
            .where(WorkoutSession.date >= cutoff_prior)
            .where(WorkoutSession.date < cutoff_recent)
        )
        prior_count = result_prior.scalar_one() or 0

        if prior_count == 0:
            trend = "insufficient_data"
        elif recent_count > prior_count * 1.1:
            trend = "improving"
        elif recent_count < prior_count * 0.9:
            trend = "declining"
        else:
            trend = "stable"

        return {"trend": trend, "recent_2w": recent_count, "prior_2w": prior_count}

    async def get_progress_summary(self, db: AsyncSession) -> dict:
        result = await db.execute(
            select(func.count(WorkoutSession.id)).where(WorkoutSession.completed == True)
        )
        total = result.scalar_one() or 0
        consistency = await self.calculate_consistency(db)
        recent = await self.summarize_recent_workouts(db, limit=5)
        trends = await self.detect_training_trends(db)
        return {
            "total_workouts": total,
            "consistency": consistency,
            "recent": recent,
            "trends": trends,
        }
