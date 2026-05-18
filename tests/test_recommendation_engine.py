import pytest
from app.core.recommendation_engine.engine import RecommendationEngine


@pytest.fixture
def recommender():
    return RecommendationEngine()


async def test_generate_recommendations_empty_db(recommender, db_session):
    recs = await recommender.generate_recommendations(db_session)
    assert isinstance(recs, list)


async def test_save_recommendations(recommender, db_session):
    recs = [{"rec_type": "test", "message": "Test recommendation", "priority": 1}]
    await recommender.save_recommendations(recs, db_session)
    from sqlalchemy import select
    from app.models.orm_models import Recommendation
    result = await db_session.execute(select(Recommendation))
    saved = result.scalars().all()
    assert len(saved) == 1
    assert saved[0].rec_type == "test"


async def test_deload_check_no_data(recommender, db_session):
    result = await recommender.check_deload_needed(db_session)
    assert result is None


async def test_recovery_check_no_data(recommender, db_session):
    result = await recommender.check_recovery_change(db_session)
    assert result is None
