from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.orm_models import Recommendation, WorkoutSession
from app.core.progression_engine.engine import ProgressionEngine
from app.core.recovery_engine.engine import RecoveryEngine
from app.core.analytics_engine.engine import AnalyticsEngine
from app.core.scheduler_engine.engine import SchedulerEngine
from datetime import date, timedelta
from datetime import datetime, timezone
from typing import Optional


class RecommendationEngine:
    def __init__(self):
        self.progression_engine = ProgressionEngine()
        self.recovery_engine = RecoveryEngine()
        self.analytics_engine = AnalyticsEngine()
        self.scheduler_engine = SchedulerEngine()

    async def check_inactivity(self, db: AsyncSession) -> Optional[dict]:
        inactive_days = await self.scheduler_engine.inactivity_days(db)
        if inactive_days >= 2:
            return {
                "rec_type": "inactivity",
                "message": f"No completed workout logged for {inactive_days} day(s). Schedule a light restart session.",
                "priority": 3,
            }
        return None

    async def check_missed_workouts(self, db: AsyncSession) -> Optional[dict]:
        missed = await self.scheduler_engine.detect_missed_workout(db)
        if missed:
            return {
                "rec_type": "missed_workout",
                "message": "A planned workout appears to have been missed. Consider a short catch-up session.",
                "priority": 3,
            }
        return None

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

    async def check_consistency_trend(self, db: AsyncSession) -> Optional[dict]:
        trends = await self.analytics_engine.detect_training_trends(db)
        if trends.get("trend") == "declining":
            return {
                "rec_type": "consistency_trend",
                "message": "Consistency trend is declining. Reduce plan complexity and set one anchor workout this week.",
                "priority": 2,
            }
        return None

    async def check_goal_progress(self, db: AsyncSession) -> Optional[dict]:
        # A lightweight goal proxy: recent completion ratio over last 14 days.
        cutoff = date.today() - timedelta(days=14)
        result = await db.execute(
            select(func.count(WorkoutSession.id))
            .where(WorkoutSession.completed == True)
            .where(WorkoutSession.date >= cutoff)
            .where(WorkoutSession.split_type != "Rest")
        )
        completed = result.scalar_one() or 0
        target = 10
        if completed < max(1, int(target * 0.5)):
            return {
                "rec_type": "goal_progress",
                "message": "Goal progress is behind target cadence. Focus on consistency before increasing intensity.",
                "priority": 2,
            }
        return None

    async def generate_recommendations(self, db: AsyncSession) -> list[dict]:
        recs = []
        for checker in [
            self.check_inactivity,
            self.check_missed_workouts,
            self.check_deload_needed,
            self.check_progression_opportunity,
            self.check_schedule_adjustment,
            self.check_recovery_change,
            self.check_consistency_trend,
            self.check_goal_progress,
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
