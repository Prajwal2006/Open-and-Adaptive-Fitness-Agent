from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.api.dependencies import get_db_session
from app.schemas.schemas import (
    TodayWorkoutResponse, LogWorkoutRequest, LogWorkoutResponse,
    ExerciseLogCreate, ExerciseLogResponse, TrainingStateResponse
)
from app.core.scheduler_engine.engine import SchedulerEngine
from app.core.analytics_engine.engine import AnalyticsEngine
from app.core.recovery_engine.engine import RecoveryEngine
from app.core.events import Event, EventType, lightweight_dispatcher
from app.models.orm_models import WorkoutSession, ExerciseLog, Recommendation
from datetime import date, datetime, timezone

router = APIRouter()
scheduler = SchedulerEngine()
analytics = AnalyticsEngine()
recovery = RecoveryEngine()


@router.get("/today-workout", response_model=TodayWorkoutResponse)
async def get_today_workout(db: AsyncSession = Depends(get_db_session)):
    workout = await scheduler.get_today_workout(db)
    return TodayWorkoutResponse(**workout)


@router.post("/log-workout", response_model=LogWorkoutResponse)
async def log_workout(request: LogWorkoutRequest, db: AsyncSession = Depends(get_db_session)):
    session = WorkoutSession(
        date=date.today(),
        split_type=request.split_type,
        completed=True,
        duration_minutes=request.duration_minutes,
        notes=request.notes,
        created_at=datetime.now(timezone.utc),
    )
    db.add(session)
    await db.flush()

    if request.exercises:
        for ex_data in request.exercises:
            ex_log = ExerciseLog(
                session_id=session.id,
                exercise_name=ex_data.exercise_name,
                sets_completed=ex_data.sets_completed,
                reps_completed=ex_data.reps_completed,
                weight_kg=ex_data.weight_kg,
                rpe=ex_data.rpe,
                created_at=datetime.now(timezone.utc),
            )
            db.add(ex_log)

    await scheduler.mark_workout_complete(db, session.id)
    await lightweight_dispatcher.emit(
        Event(
            event_type=EventType.PLAN_UPDATED,
            payload={"session_id": session.id, "split_type": request.split_type},
        )
    )
    next_w = await scheduler.get_next_workout(db)

    return LogWorkoutResponse(
        session_id=session.id,
        split_type=request.split_type,
        date=date.today(),
        message="Workout logged successfully.",
        next_workout=next_w["split_type"],
    )


@router.post("/log-exercise", response_model=ExerciseLogResponse)
async def log_exercise(request: ExerciseLogCreate, db: AsyncSession = Depends(get_db_session)):
    result = await db.execute(select(WorkoutSession).where(WorkoutSession.id == request.session_id))
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Workout session not found.")
    ex = ExerciseLog(
        session_id=request.session_id,
        exercise_name=request.exercise_name,
        sets_completed=request.sets_completed,
        reps_completed=request.reps_completed,
        weight_kg=request.weight_kg,
        rpe=request.rpe,
        created_at=datetime.now(timezone.utc),
    )
    db.add(ex)
    await db.flush()
    await db.refresh(ex)
    return ExerciseLogResponse.model_validate(ex)


@router.get("/training-state", response_model=TrainingStateResponse)
async def get_training_state(db: AsyncSession = Depends(get_db_session)):
    readiness = await recovery.calculate_readiness_score(db)
    fatigue = await recovery.calculate_fatigue_load(db)
    consistency = await analytics.calculate_consistency(db)
    result = await db.execute(select(func.count()).select_from(Recommendation))
    recs_count = result.scalar_one() or 0
    return TrainingStateResponse(
        fatigue_level=round(fatigue, 3),
        recovery_score=round(1.0 - fatigue, 3),
        readiness_score=round(readiness, 3),
        consistency_score=round(consistency, 3),
        plateau_detected=False,
        recommendations_count=recs_count,
    )
