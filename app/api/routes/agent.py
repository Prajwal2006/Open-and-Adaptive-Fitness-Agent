from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db_session
from app.core.recommendation_engine.engine import RecommendationEngine
from app.integrations.openclaw.responses import safe_agent_response
from app.memory.memory_service import MemoryService
from app.notifications.service import NotificationService
from app.services.fitness_service import FitnessService

router = APIRouter(prefix="/agent", tags=["Agent"])
fitness_service = FitnessService()
recommendation_engine = RecommendationEngine()
notification_service = NotificationService()
memory_service = MemoryService()


@router.get("/summary")
async def get_agent_summary(db: AsyncSession = Depends(get_db_session)):
    context = await fitness_service.get_full_context(db)
    long_term = await memory_service.get_long_term_state(db)
    return safe_agent_response(
        "agent_summary",
        {
            "today": context.get("today", {}),
            "readiness": context.get("readiness"),
            "state": context.get("state", {}),
            "long_term": long_term,
        },
    )


@router.get("/recommendations")
async def get_agent_recommendations(db: AsyncSession = Depends(get_db_session)):
    recs = await recommendation_engine.generate_recommendations(db)
    return safe_agent_response("agent_recommendations", {"count": len(recs), "items": recs})


@router.get("/notifications")
async def get_agent_notifications(db: AsyncSession = Depends(get_db_session)):
    unread = await notification_service.get_unread(db)
    payload = [
        {
            "id": n.id,
            "title": n.title,
            "message": n.message,
            "severity": n.severity,
            "priority": n.priority,
            "status": n.status,
        }
        for n in unread
    ]
    return safe_agent_response("agent_notifications", {"count": len(payload), "items": payload})


@router.get("/state")
async def get_agent_state(db: AsyncSession = Depends(get_db_session)):
    context = await fitness_service.get_full_context(db)
    return safe_agent_response("agent_state", context)


@router.post("/checkin")
async def agent_checkin(db: AsyncSession = Depends(get_db_session)):
    result = await fitness_service.run_daily_update(db)
    summary = await memory_service.create_structured_summary(db)
    await db.commit()
    return safe_agent_response(
        "agent_checkin",
        {
            "daily_update": result,
            "memory_summary_id": summary.id,
        },
    )
