import pytest
from app.core.progression_engine.engine import ProgressionEngine


@pytest.fixture
def progression():
    return ProgressionEngine()


async def test_suggest_next_weight_no_history(progression, db_session):
    weight = await progression.suggest_next_weight("Unknown Exercise", db_session)
    assert weight == ProgressionEngine.DEFAULT_WEIGHT_KG


async def test_detect_plateau_no_history(progression, db_session):
    result = await progression.detect_plateau("Bench Press", db_session)
    assert result is False


async def test_volume_calculation_no_history(progression, db_session):
    result = await progression.calculate_volume_progression("Squat", db_session)
    assert result["trend"] == "no_data"
    assert result["avg_volume"] == 0.0


async def test_deload_recommendation_initial(progression, db_session):
    result = await progression.recommend_deload(db_session)
    assert result is False


async def test_exercise_history_empty(progression, db_session):
    history = await progression.get_exercise_history("Deadlift", db_session)
    assert history == []
