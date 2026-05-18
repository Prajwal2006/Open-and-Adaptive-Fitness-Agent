from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.orm_models import ScheduleState, ReadinessSnapshot
from app.config.settings import settings
from datetime import datetime, date
from typing import Optional


class FitnessState(BaseModel):
    current_split_position: int = 0
    fatigue_state: float = 0.0
    recovery_state: float = 1.0
    progression_state: dict = {}
    consistency_score: float = 0.0
    adaptive_adjustment: int = 0
    training_readiness: float = 1.0
    plateau_state: dict = {}


class StateEngine:
    def __init__(self):
        self.state = FitnessState()

    async def load_state(self, db: AsyncSession) -> None:
        result = await db.execute(select(ScheduleState).limit(1))
        row = result.scalar_one_or_none()
        if row:
            self.state.current_split_position = row.current_position
            self.state.adaptive_adjustment = row.shift_offset

        result2 = await db.execute(
            select(ReadinessSnapshot).order_by(ReadinessSnapshot.created_at.desc()).limit(1)
        )
        snap = result2.scalar_one_or_none()
        if snap:
            self.state.fatigue_state = snap.fatigue_level
            self.state.recovery_state = snap.recovery_score
            self.state.training_readiness = snap.readiness_score

    async def persist_state(self, db: AsyncSession) -> None:
        result = await db.execute(select(ScheduleState).limit(1))
        row = result.scalar_one_or_none()
        if row is None:
            row = ScheduleState(
                current_position=self.state.current_split_position,
                shift_offset=self.state.adaptive_adjustment,
                updated_at=datetime.utcnow(),
            )
            db.add(row)
        else:
            row.current_position = self.state.current_split_position
            row.shift_offset = self.state.adaptive_adjustment
            row.updated_at = datetime.utcnow()
        await db.flush()

    def update_fatigue(self, workout_completed: bool) -> None:
        if workout_completed:
            self.state.fatigue_state = min(1.0, self.state.fatigue_state + 0.2)
            self.state.recovery_state = max(0.0, self.state.recovery_state - 0.15)
        else:
            self.state.fatigue_state = max(0.0, self.state.fatigue_state * settings.RECOVERY_FATIGUE_DECAY)
            self.state.recovery_state = min(1.0, self.state.recovery_state + 0.1)
        self.state.training_readiness = self.calculate_readiness()

    def calculate_readiness(self) -> float:
        readiness = 1.0 - (self.state.fatigue_state * 0.6) + (self.state.recovery_state * 0.4)
        return max(0.0, min(1.0, readiness))

    def get_compact_summary(self) -> dict:
        return {
            "split_pos": self.state.current_split_position,
            "fatigue": round(self.state.fatigue_state, 2),
            "recovery": round(self.state.recovery_state, 2),
            "readiness": round(self.state.training_readiness, 2),
            "consistency": round(self.state.consistency_score, 2),
            "plateau": bool(self.state.plateau_state),
        }
