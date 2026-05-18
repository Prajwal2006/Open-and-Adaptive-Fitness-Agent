from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.event_engine.events import FitnessEvent
from app.models.orm_models import ScheduleState, Recommendation
from datetime import datetime


async def handle_workout_completed(event: FitnessEvent, db: AsyncSession) -> None:
    result = await db.execute(select(ScheduleState).limit(1))
    state = result.scalar_one_or_none()
    if state:
        state.last_completed_date = event.payload.get("date")
        state.consecutive_misses = 0
        state.updated_at = datetime.utcnow()
        await db.flush()


async def handle_missed_workout(event: FitnessEvent, db: AsyncSession) -> None:
    result = await db.execute(select(ScheduleState).limit(1))
    state = result.scalar_one_or_none()
    if state:
        state.consecutive_misses = (state.consecutive_misses or 0) + 1
        state.updated_at = datetime.utcnow()
        await db.flush()


async def handle_plateau_detected(event: FitnessEvent, db: AsyncSession) -> None:
    exercise = event.payload.get("exercise_name", "Unknown")
    rec = Recommendation(
        rec_type="plateau",
        message=f"Plateau detected for {exercise}. Consider deload or technique change.",
        priority=2,
        is_read=False,
        created_at=datetime.utcnow(),
    )
    db.add(rec)
    await db.flush()


async def handle_recovery_poor(event: FitnessEvent, db: AsyncSession) -> None:
    rec = Recommendation(
        rec_type="recovery",
        message="Recovery score is low. Consider rest day or reduced intensity.",
        priority=3,
        is_read=False,
        created_at=datetime.utcnow(),
    )
    db.add(rec)
    await db.flush()
