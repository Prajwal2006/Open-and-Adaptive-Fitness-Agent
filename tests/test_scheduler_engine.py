import pytest
from app.core.scheduler_engine.engine import SchedulerEngine


@pytest.fixture
def scheduler():
    return SchedulerEngine()


async def test_get_today_workout(scheduler, db_session):
    result = await scheduler.get_today_workout(db_session)
    assert "split_type" in result
    assert "date" in result
    assert "is_rest_day" in result


async def test_get_split_position_default(scheduler, db_session):
    pos = await scheduler.get_split_position(db_session)
    assert 0 <= pos < len(scheduler.split)


async def test_mark_workout_complete_advances_position(scheduler, db_session):
    pos_before = await scheduler.get_split_position(db_session)
    await scheduler.mark_workout_complete(db_session, session_id=1)
    pos_after = await scheduler.get_split_position(db_session)
    assert pos_after == (pos_before + 1) % len(scheduler.split)


async def test_shift_schedule_forward(scheduler, db_session):
    await scheduler.shift_schedule_forward(db_session, days=1)
    from sqlalchemy import select
    from app.models.orm_models import ScheduleState
    result = await db_session.execute(select(ScheduleState).limit(1))
    state = result.scalar_one_or_none()
    assert state is not None
    assert state.shift_offset == 1


async def test_get_next_workout(scheduler, db_session):
    result = await scheduler.get_next_workout(db_session)
    assert "split_type" in result
    assert "date" in result
