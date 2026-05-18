import pytest
from app.core.state_engine.engine import StateEngine


@pytest.fixture
def state_engine():
    return StateEngine()


def test_state_engine_init(state_engine):
    assert state_engine.state.fatigue_state == 0.0
    assert state_engine.state.recovery_state == 1.0
    assert state_engine.state.training_readiness == 1.0


def test_update_fatigue_workout_done(state_engine):
    state_engine.update_fatigue(workout_completed=True)
    assert state_engine.state.fatigue_state > 0.0
    assert state_engine.state.recovery_state < 1.0


def test_update_fatigue_rest(state_engine):
    state_engine.state.fatigue_state = 0.5
    state_engine.update_fatigue(workout_completed=False)
    assert state_engine.state.fatigue_state < 0.5


def test_calculate_readiness(state_engine):
    state_engine.state.fatigue_state = 0.0
    state_engine.state.recovery_state = 1.0
    readiness = state_engine.calculate_readiness()
    assert 0.0 <= readiness <= 1.0


def test_compact_summary(state_engine):
    summary = state_engine.get_compact_summary()
    assert "fatigue" in summary
    assert "recovery" in summary
    assert "readiness" in summary
    assert "split_pos" in summary


async def test_load_state(state_engine, db_session):
    await state_engine.load_state(db_session)
    assert state_engine.state is not None


async def test_persist_state(state_engine, db_session):
    await state_engine.persist_state(db_session)
    await state_engine.load_state(db_session)
    assert state_engine.state.current_split_position == 0
