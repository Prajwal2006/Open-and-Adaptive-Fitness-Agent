# OpenFitnessAgent

> **A proactive autonomous fitness intelligence backend for AI orchestrators.**

OpenFitnessAgent is an open-source, async-first REST API server that acts as the "fitness brain" behind any AI orchestrator or chatbot. It tracks workouts, manages recovery and fatigue, detects training plateaus, fires event-driven notifications, and surfaces personalised recommendations — all without requiring manual queries from the orchestrator.

Built with **FastAPI**, **SQLAlchemy 2.x (async)**, **aiosqlite**, and **APScheduler**, it exposes a clean HTTP surface that tools like [OpenClaw](https://github.com/openclaw), LangChain, CrewAI, and OpenAI Agents SDK can call as structured tools.

---

## Table of Contents

1. [Features](#features)
2. [Architecture](#architecture)
3. [Prerequisites](#prerequisites)
4. [Installation](#installation)
5. [Configuration](#configuration)
6. [Running the Server](#running-the-server)
7. [API Reference](#api-reference)
8. [Integrating with OpenClaw](#integrating-with-openclaw)
9. [Other Integrations](#other-integrations)
10. [Running Tests](#running-tests)
11. [Project Structure](#project-structure)
12. [Contributing](#contributing)
13. [License](#license)

---

## Features

- 📅 **Adaptive Workout Scheduling** — Push/Pull/Legs split with automatic rest-day detection and miss detection
- 📈 **Progression Tracking** — Per-exercise weight/volume progression with plateau detection
- 🔋 **Recovery & Fatigue Engine** — Exponential-decay fatigue model with readiness scoring
- 📊 **Analytics Engine** — Consistency metrics, trend detection, and progress summaries
- 💡 **Recommendation Engine** — Proactive workout & recovery suggestions generated on a schedule
- 🔔 **Notification Engine** — Push-style payloads prepared for orchestrator consumption
- ⚡ **Event-Driven Architecture** — Internal dispatcher handles `WORKOUT_COMPLETED`, `MISSED_WORKOUT`, `PLATEAU_DETECTED`, `RECOVERY_POOR`
- 🤖 **Orchestration Bridge** — Single unified API surface for AI orchestrator integration
- 🗄️ **Persistent State** — SQLite via async SQLAlchemy; Alembic-ready for migrations

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                  AI Orchestrator                    │
│         (OpenClaw / LangChain / CrewAI / …)         │
└───────────────────┬─────────────────────────────────┘
                    │  HTTP tool calls
┌───────────────────▼─────────────────────────────────┐
│              FastAPI REST Server                    │
│  /health  /today-workout  /log-workout  /progress   │
│  /recommendations  /notifications  /body-metrics    │
└───────┬──────────────────────────────────┬──────────┘
        │                                  │
┌───────▼──────────┐          ┌────────────▼──────────┐
│  Core Engines    │          │  Event Engine          │
│  ─ Scheduler     │          │  dispatcher + handlers │
│  ─ Progression   │          └────────────┬──────────┘
│  ─ Recovery      │                       │
│  ─ Analytics     │          ┌────────────▼──────────┐
│  ─ Recommender   │          │  APScheduler Jobs      │
│  ─ State         │          │  (hourly / 6h / 24h)   │
│  ─ Notification  │          └───────────────────────┘
└───────┬──────────┘
        │
┌───────▼──────────────────────────────────────────────┐
│           SQLite (async aiosqlite)                   │
└──────────────────────────────────────────────────────┘
```

### Core Engines

| Engine | Responsibility |
|--------|---------------|
| `StateEngine` | In-memory + persisted fitness state (fatigue, recovery, readiness) |
| `SchedulerEngine` | Adaptive workout split scheduling with miss detection |
| `ProgressionEngine` | Weight/volume progression tracking and plateau detection |
| `RecoveryEngine` | Fatigue load calculation and readiness scoring |
| `AnalyticsEngine` | Consistency metrics, trend detection, progress summaries |
| `RecommendationEngine` | Proactive recommendation generation |
| `EventEngine` | Event-driven dispatcher + handlers |
| `NotificationEngine` | Push-style notification preparation |
| `OrchestrationBridge` | Unified API surface for AI orchestrator integration |

---

## Prerequisites

- Python **3.11** or **3.12**
- `pip` (comes with Python)
- *(Optional)* a virtual environment manager such as `venv` or `conda`

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/Prajwal2006/Open-and-Adaptive-Fitness-Agent.git
cd Open-and-Adaptive-Fitness-Agent
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate          # macOS / Linux
# .venv\Scripts\activate           # Windows PowerShell
```

### 3. Install dependencies

```bash
# runtime dependencies only
pip install -r requirements.txt

# OR install with dev/test extras
pip install -e ".[dev]"
```

---

## Configuration

All settings are loaded via **Pydantic Settings** and can be overridden with environment variables prefixed with `OFA_`, or by placing a `.env` file in the project root.

| Variable | Default | Description |
|----------|---------|-------------|
| `OFA_DATABASE_URL` | `sqlite+aiosqlite:///./data/openfitnessagent.db` | SQLAlchemy async database URL |
| `OFA_APP_NAME` | `OpenFitnessAgent` | Application name shown in OpenAPI docs |
| `OFA_APP_VERSION` | `0.1.0` | Application version |
| `OFA_DEBUG` | `false` | Enable debug mode |
| `OFA_DEFAULT_SPLIT` | `["Push","Pull","Legs","Rest","Push","Pull","Legs"]` | Weekly workout split template |
| `OFA_PLATEAU_THRESHOLD` | `3` | Consecutive sessions without progress before plateau fires |
| `OFA_DELOAD_THRESHOLD` | `6` | Consecutive sessions before a deload is recommended |
| `OFA_PROGRESSION_INCREMENT_KG` | `2.5` | Weight increment per progression step (kg) |
| `OFA_CONSISTENCY_WINDOW_DAYS` | `30` | Rolling window for consistency scoring |
| `OFA_RECOVERY_FATIGUE_DECAY` | `0.85` | Exponential decay factor for fatigue calculation |

Example `.env` file:

```env
OFA_DEBUG=true
OFA_PROGRESSION_INCREMENT_KG=5.0
OFA_DEFAULT_SPLIT=["Push","Pull","Legs","Rest","Push","Pull","Rest"]
```

---

## Running the Server

### Using the provided script

```bash
bash scripts/start.sh
```

### Manually with Uvicorn

```bash
mkdir -p data
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Once started, the interactive API docs are available at:

- **Swagger UI** → http://localhost:8000/docs
- **ReDoc** → http://localhost:8000/redoc

---

## API Reference

All endpoints are relative to `http://localhost:8000`.

### Health

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Liveness check — returns `{"status":"healthy"}` |

### Workout

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/today-workout` | Returns today's planned split type and rest-day status |
| `POST` | `/log-workout` | Log a completed workout session (with optional exercise logs) |
| `POST` | `/log-exercise` | Append an individual exercise log to an existing session |
| `GET` | `/training-state` | Current fatigue, recovery, readiness, and consistency scores |

**`POST /log-workout` — request body example:**

```json
{
  "split_type": "Push",
  "duration_minutes": 60,
  "notes": "Felt strong today",
  "exercises": [
    {
      "exercise_name": "Bench Press",
      "sets_completed": 4,
      "reps_completed": 8,
      "weight_kg": 80.0,
      "rpe": 7
    }
  ]
}
```

### Progress

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/progress-summary` | Consistency score, total workouts, trends, and split position |

### Recommendations

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/recommendations` | List of proactive recommendations ordered by priority |

### Notifications

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/notifications` | Unread push-style notification payloads |

### Metrics

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/body-metrics` | Log body-weight and body-fat percentage |

---

## Integrating with OpenClaw

[OpenClaw](https://github.com/openclaw) is an open-source AI orchestration framework that lets agents call external HTTP endpoints as **tools**. OpenFitnessAgent exposes a REST API that maps directly to the OpenClaw tool definition format.

### Step 1 — Start the OpenFitnessAgent server

```bash
bash scripts/start.sh
# Server is now listening on http://localhost:8000
```

Verify it is healthy:

```bash
curl http://localhost:8000/health
# {"status":"healthy","service":"OpenFitnessAgent","version":"0.1.0"}
```

### Step 2 — Install and configure OpenClaw

Follow the [OpenClaw installation guide](https://github.com/openclaw) for your environment, then create (or open) your OpenClaw agent configuration file (e.g. `agent_config.yaml`).

### Step 3 — Define OpenFitnessAgent as an OpenClaw tool set

Add the following tool definitions to your OpenClaw configuration. Each tool maps a name the LLM can call to a specific OpenFitnessAgent endpoint:

```yaml
tools:
  - name: get_today_workout
    description: >
      Returns today's planned workout split type, whether it is a rest day,
      and the next scheduled split.
    type: http
    method: GET
    url: http://localhost:8000/today-workout

  - name: log_workout
    description: >
      Log a completed workout session. Provide split_type, duration_minutes,
      optional notes, and an optional list of exercises with sets, reps,
      weight_kg, and RPE.
    type: http
    method: POST
    url: http://localhost:8000/log-workout
    body_schema:
      type: object
      properties:
        split_type:
          type: string
          description: "e.g. Push, Pull, Legs"
        duration_minutes:
          type: integer
        notes:
          type: string
        exercises:
          type: array
          items:
            type: object
            properties:
              exercise_name: { type: string }
              sets_completed: { type: integer }
              reps_completed: { type: integer }
              weight_kg: { type: number }
              rpe: { type: integer, description: "Rate of Perceived Exertion 1-10" }

  - name: get_training_state
    description: >
      Returns the user's current fatigue level, recovery score, readiness
      score, consistency score, and recommendation count.
    type: http
    method: GET
    url: http://localhost:8000/training-state

  - name: get_progress_summary
    description: >
      Returns a full progress summary including consistency score, total
      workouts completed, recent workout history, and performance trends.
    type: http
    method: GET
    url: http://localhost:8000/progress-summary

  - name: get_recommendations
    description: >
      Returns a prioritised list of proactive workout and recovery
      recommendations generated by the agent.
    type: http
    method: GET
    url: http://localhost:8000/recommendations

  - name: get_notifications
    description: >
      Returns unread push notifications (missed workouts, plateau alerts,
      recovery warnings) that the agent has queued.
    type: http
    method: GET
    url: http://localhost:8000/notifications

  - name: log_body_metrics
    description: >
      Log body-weight and optional body-fat percentage for a given date.
    type: http
    method: POST
    url: http://localhost:8000/body-metrics
    body_schema:
      type: object
      properties:
        date:
          type: string
          format: date
          description: "ISO 8601 date, e.g. 2025-05-18"
        weight_kg:
          type: number
        body_fat_pct:
          type: number
        notes:
          type: string
```

### Step 4 — Wire the tools into your OpenClaw agent

```yaml
agent:
  name: FitnessCoach
  model: gpt-4o          # or any model supported by OpenClaw
  system_prompt: >
    You are a proactive fitness coach. Use the available tools to check
    the user's training state, recommend workouts, log sessions, and
    surface recovery alerts. Always check get_today_workout before
    suggesting any activity.
  tools:
    - get_today_workout
    - log_workout
    - get_training_state
    - get_progress_summary
    - get_recommendations
    - get_notifications
    - log_body_metrics
```

### Step 5 — Run the OpenClaw agent

```bash
openclaw run --config agent_config.yaml
```

The LLM can now call any of the fitness tools during a conversation. Example interaction:

```
User:  How is my training going and what should I do today?

Agent: [calls get_today_workout]   → "Push day"
       [calls get_training_state]  → readiness 0.82, fatigue 0.18
       [calls get_recommendations] → "Increase bench press by 2.5 kg"

       Your readiness score is 82 % — you're well recovered! Today is a
       Push day. Your bench press is due for a progression: try adding
       2.5 kg to your working sets.
```

### Using the OpenClaw adapter in Python

OpenFitnessAgent ships an `OpenClawAdapter` stub under `app/integrations/openclaw/adapter.py` that you can extend once OpenClaw publishes a stable Python SDK:

```python
from app.integrations.openclaw.adapter import OpenClawAdapter

adapter = OpenClawAdapter()

# Check availability (returns False until the SDK is wired in)
if adapter.is_available():
    adapter.connect()
    adapter.send_event({"type": "workout_completed", "split": "Push"})
    tools = adapter.get_tools()
```

> **Note:** The Python-side adapter is a forward-compatible stub. The recommended integration path today is the HTTP tool definitions described in Steps 3–5 above.

---

## Other Integrations

OpenFitnessAgent provides adapter stubs for the following orchestration frameworks. All follow the same HTTP-tool pattern described for OpenClaw.

### LangChain

```python
# app/integrations/langchain/adapter.py
from app.integrations.langchain.adapter import LangChainAdapter

adapter = LangChainAdapter()
# get_tools() will return LangChain-compatible tool objects once implemented
tools = adapter.get_tools()
```

Alternatively, use LangChain's built-in `requests` tool to call OpenFitnessAgent endpoints directly until the native adapter is complete.

### CrewAI

```python
# app/integrations/crewai/adapter.py
from app.integrations.crewai.adapter import CrewAIAdapter

adapter = CrewAIAdapter()
# create_crew() / get_agent() will return CrewAI objects once implemented
```

### OpenAI Agents SDK

```python
# app/integrations/openai_agents/adapter.py
from app.integrations.openai_agents.adapter import OpenAIAgentsAdapter

adapter = OpenAIAgentsAdapter()
# get_tools() will return OpenAI function-tool definitions once implemented
tools = adapter.get_tools()
```

For immediate use with the OpenAI Agents SDK, define the endpoints as function tools manually:

```python
import httpx
from agents import function_tool

BASE = "http://localhost:8000"

@function_tool
def get_today_workout() -> dict:
    """Returns today's planned workout split."""
    return httpx.get(f"{BASE}/today-workout").json()

@function_tool
def get_training_state() -> dict:
    """Returns current fatigue, recovery, and readiness scores."""
    return httpx.get(f"{BASE}/training-state").json()
```

---

## Running Tests

```bash
# Install dev dependencies if not already installed
pip install -e ".[dev]"

# Run the full test suite
python3 -m pytest tests/ -v
```

Tests use `pytest-asyncio` with `asyncio_mode = "auto"` (configured in `pyproject.toml`).

---

## Project Structure

```
Open-and-Adaptive-Fitness-Agent/
├── app/
│   ├── api/
│   │   ├── dependencies.py          # DB session dependency
│   │   └── routes/                  # FastAPI routers
│   │       ├── health.py
│   │       ├── workout.py
│   │       ├── progress.py
│   │       ├── recommendations.py
│   │       ├── notifications.py
│   │       └── metrics.py
│   ├── config/
│   │   └── settings.py              # Pydantic settings (env-configurable)
│   ├── core/
│   │   ├── analytics_engine/
│   │   ├── event_engine/            # Dispatcher + event handlers
│   │   ├── notification_engine/
│   │   ├── orchestration_bridge/    # Unified bridge for AI orchestrators
│   │   ├── progression_engine/
│   │   ├── recommendation_engine/
│   │   ├── recovery_engine/
│   │   ├── scheduler_engine/
│   │   └── state_engine/
│   ├── integrations/
│   │   ├── crewai/
│   │   ├── langchain/
│   │   ├── openclaw/
│   │   └── openai_agents/
│   ├── models/                      # SQLAlchemy ORM models
│   ├── persistence/                 # Database init + repositories
│   ├── schemas/                     # Pydantic request/response schemas
│   └── main.py                      # FastAPI app + APScheduler setup
├── data/                            # SQLite database (auto-created)
├── docs/
│   └── architecture.md
├── scripts/
│   └── start.sh
├── tests/                           # pytest test suite
├── pyproject.toml
├── requirements.txt
└── README.md
```

---

## Contributing

Contributions are welcome! To get started:

1. Fork the repository and create a feature branch.
2. Install dev dependencies: `pip install -e ".[dev]"`
3. Make your changes and add tests where appropriate.
4. Run the test suite: `python3 -m pytest tests/ -v`
5. Open a pull request against `main` with a clear description.

Please keep commits focused and follow the existing code style.

---

## License

This project is licensed under the **MIT License**. See [LICENSE](LICENSE) for details.

