from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.api.dependencies import get_db_session
from app.schemas.schemas import BodyMetricsCreate, BodyMetricsResponse
from app.models.orm_models import BodyMetrics, WorkoutSession, Recommendation, NotificationPayload
from datetime import datetime, timezone
from app.scheduler.runtime import scheduler_runtime

router = APIRouter()


@router.post("/body-metrics", response_model=BodyMetricsResponse)
async def log_body_metrics(request: BodyMetricsCreate, db: AsyncSession = Depends(get_db_session)):
    metrics = BodyMetrics(
        date=request.date,
        weight_kg=request.weight_kg,
        body_fat_pct=request.body_fat_pct,
        notes=request.notes,
        created_at=datetime.now(timezone.utc),
    )
    db.add(metrics)
    await db.flush()
    await db.refresh(metrics)
    return BodyMetricsResponse.model_validate(metrics)


@router.get("/metrics")
async def get_system_metrics(db: AsyncSession = Depends(get_db_session)):
    workouts = (await db.execute(select(func.count()).select_from(WorkoutSession))).scalar_one() or 0
    recommendations = (await db.execute(select(func.count()).select_from(Recommendation))).scalar_one() or 0
    unread = (
        await db.execute(
            select(func.count())
            .select_from(NotificationPayload)
            .where(NotificationPayload.is_read == False)
            .where(NotificationPayload.status != "dismissed")
        )
    ).scalar_one() or 0
    scheduler = scheduler_runtime.health()
    return {
        "workouts_total": workouts,
        "recommendations_total": recommendations,
        "notifications_unread": unread,
        "scheduler": scheduler,
    }
