import abc

from aios.services.base import ServiceLifecycle


class MemoryService(ServiceLifecycle, abc.ABC):
    """Interface for loading, updating, committing, and pruning memory tiers."""

    @abc.abstractmethod
    def restore_memory(self, context: dict) -> None:
        """Restores memory relevant to the given context."""
        pass

    @abc.abstractmethod
    def observe_event(self, event: dict) -> None:
        """Observes an event for potential memory retention."""
        pass

    @abc.abstractmethod
    def commit_memory(self) -> None:
        """Persists the current memory state."""
        pass

    @abc.abstractmethod
    def prune_memory(self) -> None:
        """Runs the memory pruning and expiration routines."""
        pass
