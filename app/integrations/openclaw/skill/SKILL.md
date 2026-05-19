# OpenFitnessAgent Skill for OpenClaw

## Purpose
Use OpenFitnessAgent as a proactive sub-agent for training guidance, recovery support, and adherence coaching.

## Route Fitness Requests When
- The user asks for today\'s workout, progression, or recovery guidance.
- The user wants recent training state, consistency, or workout trend summaries.
- The user asks to log workouts, body metrics, or fitness habits.
- The system detects inactivity, missed workouts, low recovery, or broken habits.

## Preferred APIs
- GET /agent/summary
- GET /agent/recommendations
- GET /agent/notifications
- GET /agent/state
- POST /agent/checkin

## MCP-Ready Tool Calls
- get_today_workout
- get_training_state
- get_notifications
- generate_workout_plan
- get_recovery_recommendation
- log_workout
- log_habit

## Proactive Notification Policy
Trigger proactive notifications when:
- Inactivity is detected for 2+ days
- A workout is missed
- Recovery/readiness is low
- Weekly summary is generated
- Consistency trend declines

Prioritize notification severity:
- critical: immediate risk, severe recovery warning
- warning: inactivity, repeated misses
- info: plan updates, normal reminders

## Safety Boundaries
- Do not provide medical diagnosis.
- Do not prescribe treatment for injury or disease.
- Keep recommendations conservative and reversible.
- Ask for human professional help when risk signals are high.
- Keep responses concise, structured, and orchestrator-safe.
