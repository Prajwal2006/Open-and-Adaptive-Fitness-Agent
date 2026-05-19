from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db_session
from app.config.settings import settings
from app.db.health import check_database_health
from app.scheduler.runtime import scheduler_runtime

router = APIRouter()


@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db_session)):
    db_health = await check_database_health(db)
    scheduler_health = scheduler_runtime.health()
    status = "healthy" if db_health.get("ok") else "degraded"
    return {
        "status": status,
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "database": db_health,
        "scheduler": scheduler_health,
    }
