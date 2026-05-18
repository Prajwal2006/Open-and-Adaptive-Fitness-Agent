import pytest
from app.core.event_engine.events import FitnessEvent, FitnessEventType
from app.core.event_engine.dispatcher import EventDispatcher


@pytest.fixture
def dispatcher_instance():
    return EventDispatcher()


async def test_dispatch_calls_handler(dispatcher_instance, db_session):
    called = []

    async def handler(event, db):
        called.append(event.event_type)

    dispatcher_instance.subscribe(FitnessEventType.WORKOUT_COMPLETED, handler)
    event = FitnessEvent(event_type=FitnessEventType.WORKOUT_COMPLETED, payload={})
    await dispatcher_instance.dispatch(event, db_session)
    assert FitnessEventType.WORKOUT_COMPLETED in called


async def test_subscriber_registration(dispatcher_instance):
    async def handler(event, db):
        pass

    dispatcher_instance.subscribe(FitnessEventType.MISSED_WORKOUT, handler)
    assert FitnessEventType.MISSED_WORKOUT in dispatcher_instance._subscribers
    assert len(dispatcher_instance._subscribers[FitnessEventType.MISSED_WORKOUT]) == 1


async def test_dispatch_marks_processed(dispatcher_instance, db_session):
    event = FitnessEvent(event_type=FitnessEventType.PLATEAU_DETECTED, payload={"exercise_name": "Squat"})
    await dispatcher_instance.dispatch(event, db_session)
    assert event.processed is True


async def test_dispatch_and_store(dispatcher_instance, db_session):
    event = FitnessEvent(event_type=FitnessEventType.RECOVERY_POOR, payload={})
    await dispatcher_instance.dispatch_and_store(event, db_session)
    from sqlalchemy import select
    from app.models.orm_models import EventHistory
    result = await db_session.execute(select(EventHistory))
    history = result.scalars().all()
    assert len(history) == 1
