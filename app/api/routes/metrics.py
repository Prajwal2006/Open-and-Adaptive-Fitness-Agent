from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies import get_db_session
from app.schemas.schemas import BodyMetricsCreate, BodyMetricsResponse
from app.models.orm_models import BodyMetrics
from datetime import datetime, timezone

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
