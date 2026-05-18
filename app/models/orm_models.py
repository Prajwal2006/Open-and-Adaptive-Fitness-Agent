from datetime import datetime, date
from sqlalchemy import Integer, String, Float, Boolean, DateTime, Date, ForeignKey, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from typing import Optional


class Base(DeclarativeBase):
    pass


class WorkoutSession(Base):
    __tablename__ = "workout_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    split_type: Mapped[str] = mapped_column(String(50), nullable=False)
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    duration_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    exercise_logs: Mapped[list["ExerciseLog"]] = relationship("ExerciseLog", back_populates="session")


class ExerciseLog(Base):
    __tablename__ = "exercise_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(Integer, ForeignKey("workout_sessions.id"), nullable=False)
    exercise_name: Mapped[str] = mapped_column(String(200), nullable=False)
    sets_completed: Mapped[int] = mapped_column(Integer, nullable=False)
    reps_completed: Mapped[int] = mapped_column(Integer, nullable=False)
    weight_kg: Mapped[float] = mapped_column(Float, nullable=False)
    rpe: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    session: Mapped["WorkoutSession"] = relationship("WorkoutSession", back_populates="exercise_logs")


class BodyMetrics(Base):
    __tablename__ = "body_metrics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    weight_kg: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    body_fat_pct: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ProgressionHistory(Base):
    __tablename__ = "progression_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    exercise_name: Mapped[str] = mapped_column(String(200), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    weight_kg: Mapped[float] = mapped_column(Float, nullable=False)
    volume: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ScheduleState(Base):
    __tablename__ = "schedule_state"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    current_position: Mapped[int] = mapped_column(Integer, default=0)
    last_completed_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    consecutive_misses: Mapped[int] = mapped_column(Integer, default=0)
    shift_offset: Mapped[int] = mapped_column(Integer, default=0)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class EventHistory(Base):
    __tablename__ = "event_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    payload_json: Mapped[str] = mapped_column(Text, nullable=False)
    processed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Recommendation(Base):
    __tablename__ = "recommendations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    rec_type: Mapped[str] = mapped_column(String(100), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[int] = mapped_column(Integer, default=1)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class NotificationPayload(Base):
    __tablename__ = "notification_payloads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    notif_type: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    sent: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ReadinessSnapshot(Base):
    __tablename__ = "readiness_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    readiness_score: Mapped[float] = mapped_column(Float, nullable=False)
    fatigue_level: Mapped[float] = mapped_column(Float, nullable=False)
    recovery_score: Mapped[float] = mapped_column(Float, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
