import abc
from typing import List, Optional

from aios.services.memory import Memory


class MemoryStorage(abc.ABC):
    """Interface for memory storage engines."""

    @abc.abstractmethod
    def save_memory(self, memory: Memory) -> None:
        """Saves or updates a memory in the storage backend."""
        pass

    @abc.abstractmethod
    def get_memory(self, memory_id: str) -> Optional[Memory]:
        """Retrieves a memory from the storage backend."""
        pass

    @abc.abstractmethod
    def delete_memory(self, memory_id: str) -> None:
        """Deletes a memory from the storage backend."""
        pass

    @abc.abstractmethod
    def load_all_memories(self) -> List[Memory]:
        """Loads and returns all memories from the storage backend."""
        pass

    @abc.abstractmethod
    def commit(self) -> None:
        """Persists any pending changes to the storage backend."""
        pass
