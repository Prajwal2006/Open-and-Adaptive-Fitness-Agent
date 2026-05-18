from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Any


class FitnessEventType(str, Enum):
    WORKOUT_COMPLETED = "WORKOUT_COMPLETED"
    MISSED_WORKOUT = "MISSED_WORKOUT"
    PLATEAU_DETECTED = "PLATEAU_DETECTED"
    RECOVERY_POOR = "RECOVERY_POOR"
    CONSISTENCY_DROPPING = "CONSISTENCY_DROPPING"
    BODY_METRICS_UPDATED = "BODY_METRICS_UPDATED"
    DELOAD_RECOMMENDED = "DELOAD_RECOMMENDED"
    SCHEDULE_SHIFTED = "SCHEDULE_SHIFTED"
    TRAINING_READINESS_LOW = "TRAINING_READINESS_LOW"


class FitnessEvent(BaseModel):
    event_type: FitnessEventType
    payload: dict
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    processed: bool = False
