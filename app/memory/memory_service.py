from __future__ import annotations

import json
from datetime import date, datetime, timedelta, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.analytics_engine.engine import AnalyticsEngine
from app.core.recovery_engine.engine import RecoveryEngine
from app.models.orm_models import MemorySummary, UserPreference


class MemoryService:
    def __init__(self) -> None:
        self.analytics = AnalyticsEngine()
        self.recovery = RecoveryEngine()

    async def set_preference(
        self,
        db: AsyncSession,
        key: str,
        value: Any,
        user_id: str = "default",
    ) -> UserPreference:
        result = await db.execute(
            select(UserPreference)
            .where(UserPreference.user_id == user_id)
            .where(UserPreference.preference_key == key)
        )
        pref = result.scalar_one_or_none()
        if pref is None:
            pref = UserPreference(
                user_id=user_id,
                preference_key=key,
                preference_value_json=json.dumps(value),
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            db.add(pref)
        else:
            pref.preference_value_json = json.dumps(value)
            pref.updated_at = datetime.now(timezone.utc)
        await db.flush()
        return pref

    async def get_preferences(self, db: AsyncSession, user_id: str = "default") -> dict[str, Any]:
        result = await db.execute(select(UserPreference).where(UserPreference.user_id == user_id))
        prefs = result.scalars().all()
        return {p.preference_key: json.loads(p.preference_value_json) for p in prefs}

    async def create_structured_summary(self, db: AsyncSession, user_id: str = "default") -> MemorySummary:
        progress = await self.analytics.get_progress_summary(db)
        readiness = await self.recovery.calculate_readiness_score(db)
        summary_payload = {
            "consistency": progress["consistency"],
            "total_workouts": progress["total_workouts"],
            "trend": progress["trends"].get("trend"),
            "readiness": readiness,
        }
        summary = MemorySummary(
            user_id=user_id,
            summary_type="structured",
            period_start=date.today(),
            period_end=date.today(),
            summary_json=json.dumps(summary_payload),
            created_at=datetime.now(timezone.utc),
        )
        db.add(summary)
        await db.flush()
        return summary

    async def create_weekly_summary(self, db: AsyncSession, user_id: str = "default") -> MemorySummary:
        end = date.today()
        start = end - timedelta(days=6)
        progress = await self.analytics.get_progress_summary(db)
        recovery_note = await self.recovery.get_recovery_recommendation(db)
        summary_payload = {
            "window_days": 7,
            "consistency": progress["consistency"],
            "total_workouts": progress["total_workouts"],
            "recent_workouts": progress["recent"],
            "trend": progress["trends"],
            "recovery_recommendation": recovery_note,
        }
        summary = MemorySummary(
            user_id=user_id,
            summary_type="weekly",
            period_start=start,
            period_end=end,
            summary_json=json.dumps(summary_payload),
            created_at=datetime.now(timezone.utc),
        )
        db.add(summary)
        await db.flush()
        return summary

    async def get_long_term_state(self, db: AsyncSession, user_id: str = "default") -> dict[str, Any]:
        result = await db.execute(
            select(MemorySummary)
            .where(MemorySummary.user_id == user_id)
            .order_by(MemorySummary.created_at.desc())
            .limit(8)
        )
        rows = result.scalars().all()
        summaries = [json.loads(r.summary_json) for r in rows]
        if not summaries:
            return {"status": "no_memory", "summary_count": 0}
        avg_consistency = sum(s.get("consistency", 0) for s in summaries) / len(summaries)
        return {
            "status": "available",
            "summary_count": len(summaries),
            "average_consistency": round(avg_consistency, 3),
            "latest": summaries[0],
        }
