import pytest
from datetime import date


async def test_health_check(test_client):
    response = await test_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "OpenFitnessAgent"


async def test_get_today_workout(test_client):
    response = await test_client.get("/today-workout")
    assert response.status_code == 200
    data = response.json()
    assert "split_type" in data
    assert "date" in data
    assert "is_rest_day" in data


async def test_log_workout(test_client):
    payload = {
        "split_type": "Push",
        "duration_minutes": 60,
        "notes": "Test workout",
    }
    response = await test_client.post("/log-workout", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert data["split_type"] == "Push"


async def test_get_progress_summary(test_client):
    response = await test_client.get("/progress-summary")
    assert response.status_code == 200
    data = response.json()
    assert "consistency_score" in data
    assert "total_workouts" in data


async def test_get_recommendations(test_client):
    response = await test_client.get("/recommendations")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


async def test_get_notifications(test_client):
    response = await test_client.get("/notifications")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


async def test_post_body_metrics(test_client):
    payload = {
        "date": date.today().isoformat(),
        "weight_kg": 80.0,
        "body_fat_pct": 15.0,
        "notes": "Morning measurement",
    }
    response = await test_client.post("/body-metrics", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["weight_kg"] == 80.0


async def test_get_training_state(test_client):
    response = await test_client.get("/training-state")
    assert response.status_code == 200
    data = response.json()
    assert "readiness_score" in data
    assert "fatigue_level" in data
