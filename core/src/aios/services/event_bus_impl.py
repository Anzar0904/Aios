import logging
from typing import Callable, Dict, List, Type, TypeVar

from aios.services.event_bus import Event, EventBusService

logger = logging.getLogger(__name__)
E = TypeVar("E", bound=Event)


class LocalEventBus(EventBusService):
    """
    A lightweight, synchronous, in-memory event bus.
    Enforces strong event typing, registration, and isolated handler execution.
    """

    def __init__(self) -> None:
        self._registered_types: set[Type[Event]] = set()
        self._subscribers: Dict[Type[Event], List[Callable[[Event], None]]] = {}

    def initialize(self) -> None:
        logger.info("Initializing LocalEventBus")

    def on_ready(self) -> None:
        logger.info("LocalEventBus is ready")

    def teardown(self) -> None:
        logger.info("Tearing down LocalEventBus")
        self._subscribers.clear()
        self._registered_types.clear()

    def register_event_type(self, event_type: Type[Event]) -> None:
        """Registers a strongly typed event class with the bus."""
        if not issubclass(event_type, Event):
            raise TypeError(f"Type {event_type.__name__} must inherit from Event")
        self._registered_types.add(event_type)

    def subscribe(self, event_type: Type[E], handler: Callable[[E], None]) -> None:
        """Subscribes an isolated handler to a specific Event type."""
        if event_type not in self._registered_types:
            raise ValueError(f"Event type {event_type.__name__} is not registered with this bus")
        if not callable(handler):
            raise TypeError("Event handler must be callable")

        if event_type not in self._subscribers:
            self._subscribers[event_type] = []

        # Cast handler to generic Callable[[Event], None] for internal storage
        generic_handler = handler  # type: ignore
        if generic_handler not in self._subscribers[event_type]:
            self._subscribers[event_type].append(generic_handler)

    def unsubscribe(self, event_type: Type[E], handler: Callable[[E], None]) -> None:
        """Unsubscribes a handler from a specific Event type."""
        if event_type not in self._subscribers:
            return

        generic_handler = handler  # type: ignore
        if generic_handler in self._subscribers[event_type]:
            self._subscribers[event_type].remove(generic_handler)

    def publish(self, event: Event) -> None:
        """Publishes an event synchronously to all registered subscribers."""
        event_type = type(event)
        if event_type not in self._registered_types:
            raise ValueError(f"Event type {event_type.__name__} is not registered with this bus")

        handlers = self._subscribers.get(event_type, [])
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                # Log event dispatch failures to prevent cascading errors
                h_name = handler.__name__ if hasattr(handler, "__name__") else str(handler)
                logger.error(
                    f"Error in handler {h_name} while dispatching event {event_type.__name__}: {e}",
                    exc_info=True,
                )
