from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.api.dependencies import get_db_session
from app.schemas.schemas import NotificationResponse
from app.models.orm_models import NotificationPayload
from typing import List

router = APIRouter()


@router.get("/notifications", response_model=List[NotificationResponse])
async def get_notifications(db: AsyncSession = Depends(get_db_session)):
    result = await db.execute(
        select(NotificationPayload)
        .where(NotificationPayload.sent == False)
        .order_by(NotificationPayload.created_at.desc())
    )
    notifs = result.scalars().all()
    return [NotificationResponse.model_validate(n) for n in notifs]
