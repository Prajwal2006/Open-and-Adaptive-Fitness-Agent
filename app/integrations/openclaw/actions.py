from __future__ import annotations

from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.orchestration_bridge.bridge import OrchestrationBridge
from app.core.recommendation_engine.engine import RecommendationEngine
from app.core.recovery_engine.engine import RecoveryEngine
from app.memory.memory_service import MemoryService
from app.notifications.service import NotificationService
from app.schemas.schemas import LogWorkoutRequest

bridge = OrchestrationBridge()
recommender = RecommendationEngine()
recovery = RecoveryEngine()
notifications = NotificationService()
memory = MemoryService()


async def get_today_workout_action(db: AsyncSession) -> dict:
    return await bridge.get_today_workout_response(db)


async def get_training_state_action(db: AsyncSession) -> dict:
    return await bridge.get_agent_context(db)


async def get_notifications_action(db: AsyncSession, limit: int = 10) -> dict:
    unread = await notifications.get_unread(db)
    items = [
        {
            "id": n.id,
            "title": n.title,
            "message": n.message,
            "severity": n.severity,
            "priority": n.priority,
            "created_at": n.created_at.isoformat(),
        }
        for n in unread[:limit]
    ]
    return {"items": items, "count": len(items)}


async def generate_workout_plan_action(db: AsyncSession) -> dict:
    recs = await recommender.generate_recommendations(db)
    return {"generated": len(recs), "recommendations": recs}


async def get_recovery_recommendation_action(db: AsyncSession) -> dict:
    recommendation = await recovery.get_recovery_recommendation(db)
    return {"recommendation": recommendation}


async def log_workout_action(db: AsyncSession, payload: LogWorkoutRequest) -> dict:
    response = await bridge.log_workout_response(payload.model_dump(), db)
    return response


async def log_habit_action(db: AsyncSession, habit_name: str, completed: bool, notes: str | None = None) -> dict:
    status = "completed" if completed else "broken"
    await memory.set_preference(
        db,
        key=f"habit::{habit_name}",
        value={"status": status, "notes": notes, "date": date.today().isoformat()},
    )
    return {"habit_name": habit_name, "status": status}
