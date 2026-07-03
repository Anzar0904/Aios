import abc
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from aios.services.base import ServiceLifecycle


class MemoryType(Enum):
    PROJECT = "project"
    WORKSPACE = "workspace"
    USER_PREFERENCE = "user_preference"
    DECISION = "decision"
    NOTE = "note"
    TASK = "task"
    LEARNING = "learning"


@dataclass
class MemoryMetadata:
    workspace_id: str
    session_id: str
    tags: List[str] = field(default_factory=list)
    importance: int = 1
    additional: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Memory:
    memory_id: str
    content: str
    memory_type: MemoryType
    metadata: MemoryMetadata
    created_at: float
    updated_at: float


class MemoryService(ServiceLifecycle, abc.ABC):
    """Interface for loading, updating, committing, and organizing knowledge across sessions."""

    @abc.abstractmethod
    def add_memory(
        self,
        content: str,
        memory_type: MemoryType,
        tags: List[str] = None,
        importance: int = 1,
        metadata_additional: Dict[str, Any] = None,
    ) -> Memory:
        """Creates and stores a new Memory."""
        pass

    @abc.abstractmethod
    def update_memory(
        self,
        memory_id: str,
        content: Optional[str] = None,
        tags: Optional[List[str]] = None,
        importance: Optional[int] = None,
        metadata_additional: Optional[Dict[str, Any]] = None,
    ) -> Memory:
        """Updates an existing Memory."""
        pass

    @abc.abstractmethod
    def delete_memory(self, memory_id: str) -> None:
        """Deletes a Memory from the system."""
        pass

    @abc.abstractmethod
    def search_memory(
        self,
        query: str,
        memory_type: Optional[MemoryType] = None,
        tags: Optional[List[str]] = None,
    ) -> List[Memory]:
        """Searches memories by substring content match, type, and/or tags."""
        pass

    @abc.abstractmethod
    def get_memory(self, memory_id: str) -> Optional[Memory]:
        """Retrieves a specific memory by ID."""
        pass

    @abc.abstractmethod
    def load_workspace_memory(self, workspace_id: str) -> List[Memory]:
        """Loads and returns memories associated with the given workspace ID."""
        pass

    @abc.abstractmethod
    def commit(self) -> None:
        """Persists the current memories state to the storage backend."""
        pass

    # Existing backward-compatibility interface methods
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
