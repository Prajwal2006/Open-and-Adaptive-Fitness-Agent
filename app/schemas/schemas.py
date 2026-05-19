from pydantic import BaseModel, ConfigDict
from datetime import datetime, date
from typing import Optional, List, Any


class WorkoutSessionCreate(BaseModel):
    date: date
    split_type: str
    completed: bool = False
    duration_minutes: Optional[int] = None
    notes: Optional[str] = None


class WorkoutSessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    date: date
    split_type: str
    completed: bool
    duration_minutes: Optional[int]
    notes: Optional[str]
    created_at: datetime


class ExerciseLogCreate(BaseModel):
    session_id: int
    exercise_name: str
    sets_completed: int
    reps_completed: int
    weight_kg: float
    rpe: Optional[float] = None


class ExerciseLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    session_id: int
    exercise_name: str
    sets_completed: int
    reps_completed: int
    weight_kg: float
    rpe: Optional[float]
    created_at: datetime


class BodyMetricsCreate(BaseModel):
    date: date
    weight_kg: Optional[float] = None
    body_fat_pct: Optional[float] = None
    notes: Optional[str] = None


class BodyMetricsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    date: date
    weight_kg: Optional[float]
    body_fat_pct: Optional[float]
    notes: Optional[str]
    created_at: datetime


class ProgressSummaryResponse(BaseModel):
    consistency_score: float
    total_workouts: int
    recent_workouts: List[dict]
    trends: dict
    split_position: int


class TrainingStateResponse(BaseModel):
    fatigue_level: float
    recovery_score: float
    readiness_score: float
    consistency_score: float
    plateau_detected: bool
    recommendations_count: int


class RecommendationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    rec_type: str
    message: str
    priority: int
    is_read: bool
    created_at: datetime


class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: str
    notif_type: str
    title: str
    message: str
    severity: str
    priority: int
    status: str
    is_read: bool
    sent: bool
    created_at: datetime


class NotificationLifecycleRequest(BaseModel):
    status: str


class NotificationReadResponse(BaseModel):
    id: int
    is_read: bool
    status: str


class MemoryPreferenceRequest(BaseModel):
    key: str
    value: Any


class AgentResponse(BaseModel):
    type: str
    status: str
    payload: dict
    orchestrator_safe: bool = True


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str


class TodayWorkoutResponse(BaseModel):
    date: date
    split_type: str
    position: int
    is_rest_day: bool
    next_workout: Optional[str]


class LogWorkoutRequest(BaseModel):
    split_type: str
    duration_minutes: Optional[int] = None
    notes: Optional[str] = None
    exercises: Optional[List[ExerciseLogCreate]] = None


class LogWorkoutResponse(BaseModel):
    session_id: int
    split_type: str
    date: date
    message: str
    next_workout: Optional[str]
