from __future__ import annotations

from datetime import date, datetime, timezone

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.recommendation_engine.engine import RecommendationEngine
from app.core.recovery_engine.engine import RecoveryEngine
from app.core.scheduler_engine.engine import SchedulerEngine
from app.models.orm_models import NotificationPayload, WorkoutSession

scheduler = SchedulerEngine()
recovery = RecoveryEngine()
recommendations = RecommendationEngine()


async def get_today_workout(db: AsyncSession) -> dict:
    return await scheduler.get_today_workout(db)


async def get_training_state(db: AsyncSession) -> dict:
    readiness = await recovery.calculate_readiness_score(db)
    fatigue = await recovery.calculate_fatigue_load(db)
    return {
        "readiness": round(readiness, 3),
        "fatigue": round(fatigue, 3),
        "recovery": round(1.0 - fatigue, 3),
    }


async def get_notifications(db: AsyncSession, unread_only: bool = True, limit: int = 20) -> list[dict]:
    stmt = select(NotificationPayload).order_by(
        NotificationPayload.priority.desc(), NotificationPayload.created_at.desc()
    )
    if unread_only:
        stmt = stmt.where(NotificationPayload.is_read == False)
    result = await db.execute(stmt.limit(limit))
    rows = result.scalars().all()
    return [
        {
            "id": n.id,
            "title": n.title,
            "message": n.message,
            "severity": n.severity,
            "priority": n.priority,
            "status": n.status,
        }
        for n in rows
    ]


async def generate_workout_plan(db: AsyncSession) -> dict:
    recs = await recommendations.generate_recommendations(db)
    await recommendations.save_recommendations(recs, db)
    return {"count": len(recs), "recommendations": recs}


async def get_recovery_recommendation(db: AsyncSession) -> dict:
    message = await recovery.get_recovery_recommendation(db)
    return {"recommendation": message}


async def log_workout(
    db: AsyncSession,
    split_type: str,
    duration_minutes: int | None = None,
    notes: str | None = None,
) -> dict:
    session = WorkoutSession(
        date=date.today(),
        split_type=split_type,
        completed=True,
        duration_minutes=duration_minutes,
        notes=notes,
        created_at=datetime.now(timezone.utc),
    )
    db.add(session)
    await db.flush()
    await scheduler.mark_workout_complete(db, session.id)
    return {"session_id": session.id, "split_type": split_type, "date": session.date.isoformat()}


async def log_habit(db: AsyncSession, habit_name: str, completed: bool) -> dict:
    signal = "habit_completed" if completed else "habit_broken"
    return {"habit": habit_name, "signal": signal, "timestamp": datetime.now(timezone.utc).isoformat()}
