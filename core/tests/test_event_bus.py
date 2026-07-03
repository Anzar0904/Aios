import logging
from dataclasses import dataclass

import pytest
from aios.services.event_bus import Event
from aios.services.event_bus_impl import LocalEventBus


@dataclass(frozen=True, kw_only=True)
class DummyEvent(Event):
    payload: str


@dataclass(frozen=True, kw_only=True)
class AnotherDummyEvent(Event):
    value: int


def test_event_bus_registration():
    bus = LocalEventBus()

    # Event types must inherit from Event class
    with pytest.raises(TypeError):
        bus.register_event_type(int)  # type: ignore

    bus.register_event_type(DummyEvent)
    assert DummyEvent in bus._registered_types


def test_event_bus_subscription():
    bus = LocalEventBus()
    bus.register_event_type(DummyEvent)

    events_received = []

    def handler(event: DummyEvent) -> None:
        events_received.append(event)

    # Valid subscription
    bus.subscribe(DummyEvent, handler)

    # Publishing unregistered event raises ValueError
    with pytest.raises(ValueError):
        bus.publish(AnotherDummyEvent(value=42))

    # Subscribing to unregistered event raises ValueError
    with pytest.raises(ValueError):
        bus.subscribe(AnotherDummyEvent, lambda x: None)

    # Publish dummy event
    event = DummyEvent(payload="test")
    bus.publish(event)

    assert len(events_received) == 1
    assert events_received[0] == event


def test_event_bus_unsubscription():
    bus = LocalEventBus()
    bus.register_event_type(DummyEvent)

    events_received = []

    def handler(event: DummyEvent) -> None:
        events_received.append(event)

    bus.subscribe(DummyEvent, handler)
    bus.publish(DummyEvent(payload="first"))

    bus.unsubscribe(DummyEvent, handler)
    bus.publish(DummyEvent(payload="second"))

    assert len(events_received) == 1
    assert events_received[0].payload == "first"


def test_event_bus_multiple_subscribers():
    bus = LocalEventBus()
    bus.register_event_type(DummyEvent)

    results = []

    def handler_one(event: DummyEvent) -> None:
        results.append(f"one:{event.payload}")

    def handler_two(event: DummyEvent) -> None:
        results.append(f"two:{event.payload}")

    bus.subscribe(DummyEvent, handler_one)
    bus.subscribe(DummyEvent, handler_two)

    bus.publish(DummyEvent(payload="hello"))

    assert "one:hello" in results
    assert "two:hello" in results
    assert len(results) == 2


def test_event_bus_handler_isolation(caplog):
    bus = LocalEventBus()
    bus.register_event_type(DummyEvent)

    results = []

    def failing_handler(event: DummyEvent) -> None:
        raise RuntimeError("Handler exploded")

    def successful_handler(event: DummyEvent) -> None:
        results.append(event.payload)

    bus.subscribe(DummyEvent, failing_handler)
    bus.subscribe(DummyEvent, successful_handler)

    # Verify publishing does not raise an exception even when a handler fails
    caplog.clear()
    with caplog.at_level(logging.ERROR):
        bus.publish(DummyEvent(payload="safely-isolated"))

    # Verify the successful handler was still executed
    assert results == ["safely-isolated"]

    # Verify error was logged
    assert len(caplog.records) == 1
    assert "Handler exploded" in caplog.text
