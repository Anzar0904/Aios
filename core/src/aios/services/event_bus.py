import abc
import time
from dataclasses import dataclass, field
from typing import Callable, Type, TypeVar

from aios.services.base import ServiceLifecycle


@dataclass(frozen=True, kw_only=True)
class Event:
    """Base class for all strongly typed events in the system."""

    timestamp: float = field(default_factory=time.time)


E = TypeVar("E", bound=Event)


class EventBusService(ServiceLifecycle, abc.ABC):
    """Interface for synchronous event registration, subscription, and publishing."""

    @abc.abstractmethod
    def register_event_type(self, event_type: Type[Event]) -> None:
        """Registers a strongly typed event class with the bus."""
        pass

    @abc.abstractmethod
    def subscribe(self, event_type: Type[E], handler: Callable[[E], None]) -> None:
        """Subscribes an isolated handler to a specific Event type."""
        pass

    @abc.abstractmethod
    def unsubscribe(self, event_type: Type[E], handler: Callable[[E], None]) -> None:
        """Unsubscribes a handler from a specific Event type."""
        pass

    @abc.abstractmethod
    def publish(self, event: Event) -> None:
        """Publishes an event synchronously to all registered subscribers."""
        pass


@dataclass(frozen=True, kw_only=True)
class KernelStartedEvent(Event):
    """Event published when the Kernel has successfully booted and transitioned to READY."""

    version: str
