from sqlalchemy.ext.asyncio import AsyncSession
from app.core.scheduler_engine.engine import SchedulerEngine
from app.core.analytics_engine.engine import AnalyticsEngine
from app.core.recovery_engine.engine import RecoveryEngine
from app.core.state_engine.engine import StateEngine
from app.core.recommendation_engine.engine import RecommendationEngine
from datetime import date


class OrchestrationBridge:
    def __init__(self):
        self.scheduler = SchedulerEngine()
        self.analytics = AnalyticsEngine()
        self.recovery = RecoveryEngine()
        self.state = StateEngine()
        self.recommender = RecommendationEngine()

    async def get_today_workout_response(self, db: AsyncSession) -> dict:
        workout = await self.scheduler.get_today_workout(db)
        return {
            "date": workout["date"],
            "split_type": workout["split_type"],
            "position": workout["position"],
            "is_rest_day": workout["is_rest_day"],
            "next_workout": workout["next_workout"],
        }

    async def log_workout_response(self, session_data: dict, db: AsyncSession) -> dict:
        next_w = await self.scheduler.get_next_workout(db)
        return {
            "session_id": session_data.get("session_id"),
            "split_type": session_data.get("split_type"),
            "date": date.today().isoformat(),
            "message": "Workout logged successfully.",
            "next_workout": next_w["split_type"],
        }

    async def get_progress_response(self, db: AsyncSession) -> dict:
        summary = await self.analytics.get_progress_summary(db)
        position = await self.scheduler.get_split_position(db)
        return {
            "consistency_score": summary["consistency"],
            "total_workouts": summary["total_workouts"],
            "recent_workouts": summary["recent"],
            "trends": summary["trends"],
            "split_position": position,
        }

    async def get_agent_context(self, db: AsyncSession) -> dict:
        await self.state.load_state(db)
        state_summary = self.state.get_compact_summary()
        workout = await self.scheduler.get_today_workout(db)
        readiness = await self.recovery.calculate_readiness_score(db)
        recs = await self.recommender.generate_recommendations(db)
        return {
            "state": state_summary,
            "today": {"split": workout["split_type"], "rest": workout["is_rest_day"]},
            "readiness": round(readiness, 2),
            "recs": [r["rec_type"] for r in recs],
        }

    def normalize_response(self, data: dict, response_type: str) -> dict:
        return {"type": response_type, "data": data, "version": "0.1.0"}
