from __future__ import annotations

from datetime import date

from apscheduler.triggers.interval import IntervalTrigger

from app.core.events import Event, EventType, lightweight_dispatcher
from app.core.recommendation_engine.engine import RecommendationEngine
from app.core.scheduler_engine.engine import SchedulerEngine
from app.config.settings import settings
from app.memory.memory_service import MemoryService
from app.notifications.service import NotificationService
from app.persistence.database import AsyncSessionLocal
from app.scheduler.runtime import SchedulerRuntime

scheduler_engine = SchedulerEngine()
recommendation_engine = RecommendationEngine()
memory_service = MemoryService()
notification_service = NotificationService()


async def proactive_daily_check() -> None:
    async with AsyncSessionLocal() as db:
        recs = await recommendation_engine.generate_recommendations(db)
        if recs:
            await recommendation_engine.save_recommendations(recs, db)
            for rec in recs:
                await notification_service.queue_notification(
                    db,
                    notif_type="proactive_recommendation",
                    title="Training adjustment available",
                    message=rec["message"],
                    severity="info",
                    priority=rec.get("priority", 1),
                    metadata={"rec_type": rec.get("rec_type")},
                )
        await db.commit()


async def weekly_summary_job() -> None:
    async with AsyncSessionLocal() as db:
        await memory_service.create_weekly_summary(db)
        await notification_service.queue_notification(
            db,
            notif_type="weekly_summary",
            title="Weekly training summary ready",
            message="Your weekly summary has been generated for OpenClaw review.",
            severity="info",
            priority=1,
        )
        await db.commit()


async def inactivity_detection_job() -> None:
    async with AsyncSessionLocal() as db:
        inactive_days = await scheduler_engine.inactivity_days(db)
        if inactive_days >= 2:
            await lightweight_dispatcher.emit(
                Event(
                    event_type=EventType.USER_INACTIVE,
                    payload={"inactive_days": inactive_days, "date": date.today().isoformat()},
                )
            )
            await notification_service.queue_notification(
                db,
                notif_type="inactivity",
                title="Training inactivity detected",
                message=f"No workouts logged for {inactive_days} day(s).",
                severity="warning",
                priority=3,
                metadata={"inactive_days": inactive_days},
            )
        await db.commit()


def register_jobs(runtime: SchedulerRuntime) -> None:
    scheduler = runtime.scheduler
    scheduler.add_job(
        proactive_daily_check,
        IntervalTrigger(hours=settings.SCHEDULER_DAILY_CHECK_HOURS),
        id="proactive_daily_check",
        replace_existing=True,
    )
    scheduler.add_job(
        weekly_summary_job,
        IntervalTrigger(days=settings.SCHEDULER_WEEKLY_SUMMARY_DAYS),
        id="weekly_summary",
        replace_existing=True,
    )
    scheduler.add_job(
        inactivity_detection_job,
        IntervalTrigger(hours=settings.SCHEDULER_INACTIVITY_CHECK_HOURS),
        id="inactivity_detection",
        replace_existing=True,
    )
