from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.orm_models import NotificationPayload


class NotificationService:
    async def queue_notification(
        self,
        db: AsyncSession,
        notif_type: str,
        title: str,
        message: str,
        severity: str = "info",
        priority: int = 1,
        metadata: dict[str, Any] | None = None,
        user_id: str = "default",
    ) -> NotificationPayload:
        row = NotificationPayload(
            user_id=user_id,
            notif_type=notif_type,
            title=title,
            message=message,
            severity=severity,
            priority=priority,
            status="queued",
            metadata_json=json.dumps(metadata or {}),
            sent=False,
            created_at=datetime.now(timezone.utc),
        )
        db.add(row)
        await db.flush()
        return row

    async def get_unread(self, db: AsyncSession, user_id: str = "default") -> list[NotificationPayload]:
        result = await db.execute(
            select(NotificationPayload)
            .where(NotificationPayload.user_id == user_id)
            .where(NotificationPayload.is_read == False)
            .where(NotificationPayload.status != "dismissed")
            .order_by(NotificationPayload.priority.desc(), NotificationPayload.created_at.desc())
        )
        return result.scalars().all()

    async def mark_read(self, db: AsyncSession, notification_id: int) -> NotificationPayload | None:
        result = await db.execute(
            select(NotificationPayload).where(NotificationPayload.id == notification_id)
        )
        row = result.scalar_one_or_none()
        if row is None:
            return None
        row.is_read = True
        row.read_at = datetime.now(timezone.utc)
        if row.status == "queued":
            row.status = "read"
        await db.flush()
        return row

    async def update_lifecycle(
        self,
        db: AsyncSession,
        notification_id: int,
        status: str,
    ) -> NotificationPayload | None:
        result = await db.execute(
            select(NotificationPayload).where(NotificationPayload.id == notification_id)
        )
        row = result.scalar_one_or_none()
        if row is None:
            return None
        row.status = status
        if status == "sent":
            row.sent = True
            row.sent_at = datetime.now(timezone.utc)
        if status == "dismissed":
            row.dismissed_at = datetime.now(timezone.utc)
        await db.flush()
        return row
