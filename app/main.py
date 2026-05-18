from contextlib import asynccontextmanager
from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from app.persistence.database import init_db, AsyncSessionLocal
from app.api.routes import health, workout, progress, recommendations, notifications, metrics
from app.core.scheduler_engine.engine import SchedulerEngine
from app.core.recovery_engine.engine import RecoveryEngine
from app.core.recommendation_engine.engine import RecommendationEngine
from app.core.event_engine.dispatcher import dispatcher
from app.core.event_engine.handlers import (
    handle_workout_completed,
    handle_missed_workout,
    handle_plateau_detected,
    handle_recovery_poor,
)
from app.core.event_engine.events import FitnessEventType
from app.config.settings import settings

scheduler_engine = SchedulerEngine()
recovery_engine = RecoveryEngine()
recommendation_engine = RecommendationEngine()

dispatcher.subscribe(FitnessEventType.WORKOUT_COMPLETED, handle_workout_completed)
dispatcher.subscribe(FitnessEventType.MISSED_WORKOUT, handle_missed_workout)
dispatcher.subscribe(FitnessEventType.PLATEAU_DETECTED, handle_plateau_detected)
dispatcher.subscribe(FitnessEventType.RECOVERY_POOR, handle_recovery_poor)


async def check_missed_workouts():
    async with AsyncSessionLocal() as db:
        try:
            missed = await scheduler_engine.detect_missed_workout(db)
            if missed:
                from app.core.event_engine.events import FitnessEvent
                event = FitnessEvent(
                    event_type=FitnessEventType.MISSED_WORKOUT,
                    payload={"source": "scheduler"},
                )
                await dispatcher.dispatch_and_store(event, db)
                await db.commit()
        except Exception:
            pass


async def update_readiness():
    async with AsyncSessionLocal() as db:
        try:
            await recovery_engine.update_readiness_snapshot(db)
            await db.commit()
        except Exception:
            pass


async def generate_daily_recommendations():
    async with AsyncSessionLocal() as db:
        try:
            recs = await recommendation_engine.generate_recommendations(db)
            if recs:
                await recommendation_engine.save_recommendations(recs, db)
                await db.commit()
        except Exception:
            pass


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    apscheduler = AsyncIOScheduler()
    apscheduler.add_job(check_missed_workouts, IntervalTrigger(hours=1), id="check_missed")
    apscheduler.add_job(update_readiness, IntervalTrigger(hours=6), id="update_readiness")
    apscheduler.add_job(generate_daily_recommendations, IntervalTrigger(hours=24), id="daily_recs")
    apscheduler.start()
    yield
    apscheduler.shutdown(wait=False)


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
