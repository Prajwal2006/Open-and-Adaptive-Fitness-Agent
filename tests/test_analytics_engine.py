import pytest
from app.core.analytics_engine.engine import AnalyticsEngine


@pytest.fixture
def analytics():
    return AnalyticsEngine()


async def test_consistency_no_workouts(analytics, db_session):
    score = await analytics.calculate_consistency(db_session)
    assert score == 0.0


async def test_progress_summary_is_compact(analytics, db_session):
    summary = await analytics.get_progress_summary(db_session)
    assert "total_workouts" in summary
    assert "consistency" in summary
    assert "recent" in summary
    assert "trends" in summary


async def test_recent_workouts_empty(analytics, db_session):
    recent = await analytics.summarize_recent_workouts(db_session)
    assert recent == []


async def test_detect_training_trends_no_data(analytics, db_session):
    trends = await analytics.detect_training_trends(db_session)
    assert trends["trend"] == "insufficient_data"
