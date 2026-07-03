import logging
import time
import uuid
from typing import Any, Dict, List, Optional

from aios.services.context import ContextLoadedEvent
from aios.services.event_bus import EventBusService
from aios.services.memory import (
    Memory,
    MemoryMetadata,
    MemoryService,
    MemoryType,
)
from aios.services.memory_storage import MemoryStorage
from aios.services.memory_storage_impl import LocalJSONMemoryStorage
from aios.services.session import SessionEndedEvent, SessionStartedEvent

logger = logging.getLogger(__name__)


class LocalMemoryService(MemoryService):
    """Concrete implementation of MemoryService utilizing a configurable local storage backend."""

    def __init__(self, event_bus: EventBusService, storage: Optional[MemoryStorage] = None) -> None:
        self._event_bus = event_bus
        self._workspace_id: Optional[str] = None
        self._session_id: Optional[str] = None

        if storage is None:
            self._storage: MemoryStorage = LocalJSONMemoryStorage()
        else:
            self._storage = storage

        self._memories: Dict[str, Memory] = {}

    def initialize(self) -> None:
        logger.info("Initializing LocalMemoryService")
        self._event_bus.subscribe(ContextLoadedEvent, self._on_context_loaded)
        self._event_bus.subscribe(SessionStartedEvent, self._on_session_started)
        self._event_bus.subscribe(SessionEndedEvent, self._on_session_ended)

    def _on_context_loaded(self, event: ContextLoadedEvent) -> None:
        self._workspace_id = event.context.project_root
        logger.info(f"MemoryService context loaded for workspace: {self._workspace_id}")

    def _on_session_started(self, event: SessionStartedEvent) -> None:
        self._session_id = event.session_id
        workspace_id = event.session.workspace_id
        self._workspace_id = workspace_id

        loaded = self.load_workspace_memory(workspace_id)
        print(f"[MemoryService] Restored {len(loaded)} memories for workspace: {workspace_id}")

    def _on_session_ended(self, event: SessionEndedEvent) -> None:
        self.commit()
        print(f"[MemoryService] Committed memories for workspace: {self._workspace_id}")
        self._session_id = None

    def add_memory(
        self,
        content: str,
        memory_type: MemoryType,
        tags: List[str] = None,
        importance: int = 1,
        metadata_additional: Dict[str, Any] = None,
    ) -> Memory:
        if metadata_additional is None:
            metadata_additional = {}
        if tags is None:
            tags = []
        if self._workspace_id is None:
            raise RuntimeError("Cannot add memory: no active workspace context")

        session_id = self._session_id if self._session_id else "system"
        memory_id = str(uuid.uuid4())

        metadata = MemoryMetadata(
            workspace_id=self._workspace_id,
            session_id=session_id,
            tags=tags,
            importance=importance,
            additional=metadata_additional,
        )

        now = time.time()
        memory = Memory(
            memory_id=memory_id,
            content=content,
            memory_type=memory_type,
            metadata=metadata,
            created_at=now,
            updated_at=now,
        )

        self._memories[memory_id] = memory
        self._storage.save_memory(memory)
        return memory

    def update_memory(
        self,
        memory_id: str,
        content: Optional[str] = None,
        tags: Optional[List[str]] = None,
        importance: Optional[int] = None,
        metadata_additional: Optional[Dict[str, Any]] = None,
    ) -> Memory:
        memory = self.get_memory(memory_id)
        if memory is None:
            raise KeyError(f"Memory with ID {memory_id} not found")

        if content is not None:
            memory.content = content
        if tags is not None:
            memory.metadata.tags = tags
        if importance is not None:
            memory.metadata.importance = importance
        if metadata_additional is not None:
            memory.metadata.additional.update(metadata_additional)

        memory.updated_at = time.time()
        self._storage.save_memory(memory)
        return memory

    def delete_memory(self, memory_id: str) -> None:
        if memory_id in self._memories:
            del self._memories[memory_id]
        self._storage.delete_memory(memory_id)

    def search_memory(
        self,
        query: str,
        memory_type: Optional[MemoryType] = None,
        tags: Optional[List[str]] = None,
    ) -> List[Memory]:
        results = []
        for memory in self._memories.values():
            if query.lower() not in memory.content.lower():
                continue
            if memory_type is not None and memory.memory_type != memory_type:
                continue
            if tags is not None:
                if not all(tag in memory.metadata.tags for tag in tags):
                    continue
            results.append(memory)
        return results

    def get_memory(self, memory_id: str) -> Optional[Memory]:
        if memory_id in self._memories:
            return self._memories[memory_id]
        return self._storage.get_memory(memory_id)

    def load_workspace_memory(self, workspace_id: str) -> List[Memory]:
        all_memories = self._storage.load_all_memories()
        workspace_memories = [m for m in all_memories if m.metadata.workspace_id == workspace_id]
        self._memories = {m.memory_id: m for m in workspace_memories}
        return workspace_memories

    def commit(self) -> None:
        self._storage.commit()

    # Existing backward-compatibility interface methods
    def restore_memory(self, context: dict) -> None:
        workspace_id = context.get("project_root") or context.get("working_directory")
        if workspace_id:
            self._workspace_id = workspace_id
            self.load_workspace_memory(workspace_id)

    def observe_event(self, event: dict) -> None:
        pass

    def commit_memory(self) -> None:
        self.commit()

    def prune_memory(self) -> None:
        pass
