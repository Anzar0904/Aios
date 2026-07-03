import time

from aios.services.event_bus_impl import LocalEventBus
from aios.services.session import (
    SessionEndedEvent,
    SessionStartedEvent,
)
from aios.services.session_impl import LocalSessionService


def test_session_lifecycle():
    event_bus = LocalEventBus()
    event_bus.register_event_type(SessionStartedEvent)
    event_bus.register_event_type(SessionEndedEvent)

    started_events = []
    ended_events = []

    event_bus.subscribe(SessionStartedEvent, lambda e: started_events.append(e))
    event_bus.subscribe(SessionEndedEvent, lambda e: ended_events.append(e))

    service = LocalSessionService(event_bus)

    # Initially, no active session
    assert service.get_current_session() is None
    assert service.get_active_session_id() is None

    # Start a session
    workspace = "/Users/anzarakhtar/project"
    session = service.start_session(workspace)

    assert session.session_id is not None
    assert session.workspace_id == workspace
    assert session.start_time <= time.time()
    assert session.end_time is None
    assert session.runtime_state == "active"

    assert service.get_current_session() == session
    assert service.get_active_session_id() == session.session_id

    # Started event must be published
    assert len(started_events) == 1
    assert started_events[0].session_id == session.session_id
    assert started_events[0].session == session
    assert len(ended_events) == 0

    # End the session
    service.end_session()

    assert service.get_current_session() is None
    assert service.get_active_session_id() is None
    assert session.end_time is not None
    assert session.end_time >= session.start_time
    assert session.runtime_state == "ended"

    # Ended event must be published
    assert len(started_events) == 1
    assert len(ended_events) == 1
    assert ended_events[0].session_id == session.session_id
    assert ended_events[0].session == session


def test_session_auto_end_previous():
    event_bus = LocalEventBus()
    event_bus.register_event_type(SessionStartedEvent)
    event_bus.register_event_type(SessionEndedEvent)

    started_events = []
    ended_events = []

    event_bus.subscribe(SessionStartedEvent, lambda e: started_events.append(e))
    event_bus.subscribe(SessionEndedEvent, lambda e: ended_events.append(e))

    service = LocalSessionService(event_bus)

    s1 = service.start_session("/workspace/1")
    assert len(started_events) == 1
    assert len(ended_events) == 0

    # Start another session, which should auto-end the previous one
    s2 = service.start_session("/workspace/2")

    assert len(started_events) == 2
    assert len(ended_events) == 1
    assert ended_events[0].session_id == s1.session_id
    assert s1.runtime_state == "ended"
    assert s2.runtime_state == "active"


def test_create_session_compatibility():
    event_bus = LocalEventBus()
    event_bus.register_event_type(SessionStartedEvent)
    event_bus.register_event_type(SessionEndedEvent)

    service = LocalSessionService(event_bus)

    session_id = service.create_session("/workspace/path")
    assert session_id is not None
    assert service.get_active_session_id() == session_id

    # Save session should be safe to call
    service.save_session(session_id)
