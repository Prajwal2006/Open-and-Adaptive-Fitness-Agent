import pytest
from app.core.recovery_engine.engine import RecoveryEngine


@pytest.fixture
def recovery():
    return RecoveryEngine()


async def test_readiness_score_empty_db(recovery, db_session):
    score = await recovery.calculate_readiness_score(db_session)
    assert 0.0 <= score <= 1.0


async def test_fatigue_load_empty_db(recovery, db_session):
    load = await recovery.calculate_fatigue_load(db_session)
    assert load == 0.0


async def test_recovery_warnings_empty_db(recovery, db_session):
    warnings = await recovery.get_recovery_warnings(db_session)
    assert isinstance(warnings, list)


async def test_recovery_recommendation(recovery, db_session):
    rec = await recovery.get_recovery_recommendation(db_session)
    assert isinstance(rec, str)
    assert len(rec) > 0


async def test_update_readiness_snapshot(recovery, db_session):
    await recovery.update_readiness_snapshot(db_session)
    from sqlalchemy import select
    from app.models.orm_models import ReadinessSnapshot
    result = await db_session.execute(select(ReadinessSnapshot))
    snaps = result.scalars().all()
    assert len(snaps) == 1
