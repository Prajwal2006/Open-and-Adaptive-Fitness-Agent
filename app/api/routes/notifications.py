from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.api.dependencies import get_db_session
from app.schemas.schemas import NotificationResponse, NotificationLifecycleRequest, NotificationReadResponse
from app.models.orm_models import NotificationPayload
from app.notifications.service import NotificationService
from typing import List

router = APIRouter()
notification_service = NotificationService()


@router.get("/notifications", response_model=List[NotificationResponse])
async def get_notifications(unread_only: bool = True, db: AsyncSession = Depends(get_db_session)):
    filters = [NotificationPayload.status != "dismissed"]
    if unread_only:
        filters.append(NotificationPayload.is_read == False)
    result = await db.execute(
        select(NotificationPayload)
        .where(*filters)
        .order_by(NotificationPayload.priority.desc(), NotificationPayload.created_at.desc())
    )
    notifs = result.scalars().all()
    return [NotificationResponse.model_validate(n) for n in notifs]


@router.post("/notifications/{notification_id}/read", response_model=NotificationReadResponse)
async def mark_notification_read(notification_id: int, db: AsyncSession = Depends(get_db_session)):
    row = await notification_service.mark_read(db, notification_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Notification not found")
    return NotificationReadResponse(id=row.id, is_read=row.is_read, status=row.status)


@router.post("/notifications/{notification_id}/lifecycle", response_model=NotificationResponse)
async def update_notification_lifecycle(
    notification_id: int,
    request: NotificationLifecycleRequest,
    db: AsyncSession = Depends(get_db_session),
):
    row = await notification_service.update_lifecycle(db, notification_id, request.status)
    if row is None:
        raise HTTPException(status_code=404, detail="Notification not found")
    return NotificationResponse.model_validate(row)
