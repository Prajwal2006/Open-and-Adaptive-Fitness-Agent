# OpenFitnessAgent Architecture

## Overview
OpenFitnessAgent is a proactive autonomous fitness intelligence backend designed for integration with AI orchestrators (LangChain, CrewAI, OpenAI Agents, OpenClaw).

## Core Engines

| Engine | Responsibility |
|--------|---------------|
| StateEngine | Manages in-memory + persisted fitness state (fatigue, recovery, readiness) |
| SchedulerEngine | Adaptive workout split scheduling with miss detection |
| ProgressionEngine | Weight/volume progression tracking and plateau detection |
| RecoveryEngine | Fatigue load calculation and readiness scoring |
| AnalyticsEngine | Consistency metrics, trend detection, progress summaries |
| RecommendationEngine | Proactive recommendation generation |
| EventEngine | Event-driven architecture (dispatcher + handlers) |
| NotificationEngine | Push-style notification preparation |
| OrchestrationBridge | Unified API surface for AI orchestrator integration |

## Data Layer
- SQLAlchemy 2.x async ORM with aiosqlite
- Alembic for migrations
- Repositories pattern for data access

## API
FastAPI with async endpoints, APScheduler for background jobs.
