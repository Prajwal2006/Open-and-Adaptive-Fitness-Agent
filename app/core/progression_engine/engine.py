from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.orm_models import ExerciseLog, WorkoutSession, ProgressionHistory
from app.config.settings import settings
from datetime import date, datetime
from typing import Optional


class ProgressionEngine:
    DEFAULT_WEIGHT_KG = 20.0

    async def get_exercise_history(self, exercise_name: str, db: AsyncSession, limit: int = 5) -> list:
        result = await db.execute(
            select(ExerciseLog)
            .join(WorkoutSession, ExerciseLog.session_id == WorkoutSession.id)
            .where(ExerciseLog.exercise_name == exercise_name)
            .where(WorkoutSession.completed == True)
            .order_by(WorkoutSession.date.desc())
            .limit(limit)
        )
        logs = result.scalars().all()
        return [
            {
                "weight_kg": log.weight_kg,
                "sets": log.sets_completed,
                "reps": log.reps_completed,
                "rpe": log.rpe,
                "volume": log.weight_kg * log.sets_completed * log.reps_completed,
            }
            for log in logs
        ]

    async def suggest_next_weight(self, exercise_name: str, db: AsyncSession) -> float:
        history = await self.get_exercise_history(exercise_name, db, limit=3)
        if not history:
            return self.DEFAULT_WEIGHT_KG
        latest = history[0]
        if latest.get("rpe") is not None and latest["rpe"] <= 8.0:
            return round(latest["weight_kg"] + settings.PROGRESSION_INCREMENT_KG, 2)
        if len(history) >= 2:
            all_progressed = all(
                h["reps"] >= 8 and (h.get("rpe") is None or h["rpe"] <= 8)
                for h in history
            )
            if all_progressed:
                return round(latest["weight_kg"] + settings.PROGRESSION_INCREMENT_KG, 2)
        return latest["weight_kg"]

    async def detect_plateau(self, exercise_name: str, db: AsyncSession) -> bool:
        history = await self.get_exercise_history(exercise_name, db, limit=settings.PLATEAU_THRESHOLD)
        if len(history) < settings.PLATEAU_THRESHOLD:
            return False
        weights = [h["weight_kg"] for h in history]
        return len(set(weights)) == 1

    async def calculate_volume_progression(self, exercise_name: str, db: AsyncSession) -> dict:
        history = await self.get_exercise_history(exercise_name, db, limit=10)
        if not history:
            return {"trend": "no_data", "avg_volume": 0.0, "sessions": 0}
        volumes = [h["volume"] for h in history]
        avg = sum(volumes) / len(volumes)
        trend = "stable"
        if len(volumes) >= 2:
            if volumes[0] > volumes[-1] * 1.05:
                trend = "increasing"
            elif volumes[0] < volumes[-1] * 0.95:
                trend = "decreasing"
        return {"trend": trend, "avg_volume": round(avg, 2), "sessions": len(volumes)}

    async def recommend_deload(self, db: AsyncSession) -> bool:
        result = await db.execute(
            select(func.count(WorkoutSession.id))
            .where(WorkoutSession.completed == True)
        )
        total = result.scalar_one() or 0
        return total > 0 and total % (settings.DELOAD_THRESHOLD * 4) == 0
