from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.orm_models import Recommendation
from app.core.progression_engine.engine import ProgressionEngine
from app.core.recovery_engine.engine import RecoveryEngine
from app.core.analytics_engine.engine import AnalyticsEngine
from datetime import datetime, timezone
from typing import Optional


class RecommendationEngine:
    def __init__(self):
        self.progression_engine = ProgressionEngine()
        self.recovery_engine = RecoveryEngine()
        self.analytics_engine = AnalyticsEngine()

    async def check_deload_needed(self, db: AsyncSession) -> Optional[dict]:
        needs_deload = await self.progression_engine.recommend_deload(db)
        if needs_deload:
            return {
                "rec_type": "deload",
                "message": "You've been training consistently. A deload week is recommended.",
                "priority": 3,
            }
        return None

    async def check_progression_opportunity(self, db: AsyncSession) -> Optional[dict]:
        consistency = await self.analytics_engine.calculate_consistency(db)
        if consistency >= 0.8:
            return {
                "rec_type": "progression",
                "message": "Excellent consistency! Consider increasing weights this week.",
                "priority": 2,
            }
        return None

    async def check_schedule_adjustment(self, db: AsyncSession) -> Optional[dict]:
        consistency = await self.analytics_engine.calculate_consistency(db)
        if consistency < 0.5:
            return {
                "rec_type": "schedule",
                "message": "Consistency is low. Consider a more flexible training schedule.",
                "priority": 2,
            }
        return None

    async def check_recovery_change(self, db: AsyncSession) -> Optional[dict]:
        warnings = await self.recovery_engine.get_recovery_warnings(db)
        if warnings:
            return {
                "rec_type": "recovery",
                "message": warnings[0],
                "priority": 3,
            }
        return None

    async def generate_recommendations(self, db: AsyncSession) -> list[dict]:
        recs = []
        for checker in [
            self.check_deload_needed,
            self.check_progression_opportunity,
            self.check_schedule_adjustment,
            self.check_recovery_change,
        ]:
            rec = await checker(db)
            if rec:
                recs.append(rec)
        return recs

    async def save_recommendations(self, recommendations: list[dict], db: AsyncSession) -> None:
        for rec_data in recommendations:
            rec = Recommendation(
                rec_type=rec_data["rec_type"],
                message=rec_data["message"],
                priority=rec_data.get("priority", 1),
                is_read=False,
                created_at=datetime.now(timezone.utc),
            )
            db.add(rec)
        await db.flush()
