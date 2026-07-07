"""
bootstrap_modules/events.py

Constructs and wires the Event Bus.
"""

from __future__ import annotations

from aios.services.agent import AgentCompletedEvent, AgentFailedEvent, AgentStartedEvent
from aios.services.context import ContextChangedEvent, ContextLoadedEvent
from aios.services.event_bus import EventBusService, KernelStartedEvent
from aios.services.event_bus_impl import LocalEventBus
from aios.services.session import SessionEndedEvent, SessionStartedEvent
from aios.services.tool import ToolCompletedEvent, ToolFailedEvent, ToolStartedEvent


def bootstrap_events(registry) -> LocalEventBus:  # noqa: ANN001
    """Constructs, registers, and returns the Event Bus."""
    event_bus = LocalEventBus()

    # Eagerly register all system-wide event types to ensure subscription safety
    event_bus.register_event_type(KernelStartedEvent)
    event_bus.register_event_type(ContextLoadedEvent)
    event_bus.register_event_type(ContextChangedEvent)
    event_bus.register_event_type(SessionStartedEvent)
    event_bus.register_event_type(SessionEndedEvent)
    event_bus.register_event_type(AgentStartedEvent)
    event_bus.register_event_type(AgentCompletedEvent)
    event_bus.register_event_type(AgentFailedEvent)
    event_bus.register_event_type(ToolStartedEvent)
    event_bus.register_event_type(ToolCompletedEvent)
    event_bus.register_event_type(ToolFailedEvent)

    registry.register(EventBusService, event_bus)
    return event_bus
