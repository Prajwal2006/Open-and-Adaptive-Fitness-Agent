from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.orm_models import WorkoutSession, ReadinessSnapshot
from app.config.settings import settings
from datetime import date, datetime, timedelta, timezone
from typing import Optional


class RecoveryEngine:
    async def calculate_fatigue_load(self, db: AsyncSession, days: int = 7) -> float:
        cutoff = date.today() - timedelta(days=days)
        result = await db.execute(
            select(func.count(WorkoutSession.id))
            .where(WorkoutSession.completed == True)
            .where(WorkoutSession.date >= cutoff)
        )
        count = result.scalar_one() or 0
        max_expected = days * 0.85
        return min(1.0, count / max_expected) if max_expected > 0 else 0.0

    async def calculate_readiness_score(self, db: AsyncSession) -> float:
        fatigue = await self.calculate_fatigue_load(db, days=7)
        readiness = 1.0 - (fatigue * 0.7)
        return max(0.0, min(1.0, round(readiness, 3)))

    async def get_recovery_warnings(self, db: AsyncSession) -> list[str]:
        warnings = []
        fatigue = await self.calculate_fatigue_load(db, days=7)
        readiness = await self.calculate_readiness_score(db)
        if fatigue > 0.8:
            warnings.append("High training density detected. Consider a rest day.")
        if readiness < 0.4:
            warnings.append("Low readiness score. Reduce intensity or take rest.")
        if fatigue > 0.9:
            warnings.append("Extreme fatigue load. Deload week strongly recommended.")
        return warnings

    async def get_recovery_recommendation(self, db: AsyncSession) -> str:
        readiness = await self.calculate_readiness_score(db)
        if readiness >= 0.8:
            return "Fully recovered. Ready for high-intensity training."
        elif readiness >= 0.6:
            return "Moderately recovered. Normal training intensity recommended."
        elif readiness >= 0.4:
            return "Partial recovery. Consider reduced volume or intensity."
        else:
            return "Poor recovery. Rest day or active recovery strongly recommended."

    async def update_readiness_snapshot(self, db: AsyncSession) -> None:
        fatigue = await self.calculate_fatigue_load(db)
        readiness = await self.calculate_readiness_score(db)
        recovery = 1.0 - fatigue
        snap = ReadinessSnapshot(
            date=date.today(),
            readiness_score=readiness,
            fatigue_level=fatigue,
            recovery_score=round(recovery, 3),
            created_at=datetime.now(timezone.utc),
        )
        db.add(snap)
        await db.flush()
