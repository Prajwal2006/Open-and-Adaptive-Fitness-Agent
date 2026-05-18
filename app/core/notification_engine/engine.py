from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.orm_models import NotificationPayload
from app.core.scheduler_engine.engine import SchedulerEngine
from app.core.progression_engine.engine import ProgressionEngine
from datetime import datetime
import json


class NotificationEngine:
    def __init__(self):
        self.scheduler = SchedulerEngine()
        self.progression = ProgressionEngine()

    async def prepare_workout_reminder(self, db: AsyncSession) -> dict:
        workout = await self.scheduler.get_today_workout(db)
        return {
            "notif_type": "workout_reminder",
            "title": f"Time to train: {workout['split_type']}",
            "message": f"Today's workout is {workout['split_type']}. Let's go!",
            "metadata": workout,
        }

    async def prepare_missed_workout_alert(self, db: AsyncSession) -> dict:
        workout = await self.scheduler.get_today_workout(db)
        return {
            "notif_type": "missed_workout",
            "title": "Missed Workout Alert",
            "message": "You missed a scheduled workout. Schedule has been adjusted.",
            "metadata": {"date": str(workout["date"])},
        }

    async def prepare_progression_milestone(self, exercise_name: str, db: AsyncSession) -> dict:
        next_weight = await self.progression.suggest_next_weight(exercise_name, db)
        return {
            "notif_type": "progression_milestone",
            "title": f"Progress: {exercise_name}",
            "message": f"Great progress on {exercise_name}! Suggested next weight: {next_weight}kg.",
            "metadata": {"exercise": exercise_name, "suggested_weight": next_weight},
        }

    async def prepare_plateau_warning(self, exercise_name: str, db: AsyncSession) -> dict:
        return {
            "notif_type": "plateau_warning",
            "title": f"Plateau Detected: {exercise_name}",
            "message": f"Progress on {exercise_name} has stalled. Consider changing rep scheme or technique.",
            "metadata": {"exercise": exercise_name},
        }

    async def get_pending_notifications(self, db: AsyncSession) -> list[dict]:
        result = await db.execute(
            select(NotificationPayload)
            .where(NotificationPayload.sent == False)
            .order_by(NotificationPayload.created_at.desc())
        )
        notifs = result.scalars().all()
        return [
            {
                "id": n.id,
                "type": n.notif_type,
                "title": n.title,
                "message": n.message,
                "metadata": json.loads(n.metadata_json) if n.metadata_json else {},
                "created_at": n.created_at.isoformat(),
            }
            for n in notifs
        ]
