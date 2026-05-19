from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI

from app.api.routes import agent, health, workout, progress, recommendations, notifications, metrics
from app.config.settings import settings
from app.persistence.database import init_db
from app.scheduler.jobs import register_jobs
from app.scheduler.runtime import scheduler_runtime
from app.utils.logging import configure_logging
from app.utils.retry import run_with_retry

logger = logging.getLogger(__name__)
configure_logging()



@asynccontextmanager
async def lifespan(app: FastAPI):
    await run_with_retry(init_db)
    register_jobs(scheduler_runtime)
    scheduler_runtime.start()
    logger.info("OpenFitnessAgent started", extra={"env": settings.ENV, "local_first": settings.LOCAL_FIRST_MODE})
    yield
    scheduler_runtime.shutdown()
    logger.info("OpenFitnessAgent shutdown complete")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="A proactive autonomous fitness intelligence backend for AI orchestrators",
    lifespan=lifespan,
)

app.include_router(health.router, tags=["Health"])
app.include_router(workout.router, tags=["Workout"])
app.include_router(progress.router, tags=["Progress"])
app.include_router(recommendations.router, tags=["Recommendations"])
app.include_router(notifications.router, tags=["Notifications"])
app.include_router(metrics.router, tags=["Metrics"])
app.include_router(agent.router)
