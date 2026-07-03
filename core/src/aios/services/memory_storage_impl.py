import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

from aios.services.memory import Memory, MemoryMetadata, MemoryType
from aios.services.memory_storage import MemoryStorage

logger = logging.getLogger(__name__)


class LocalJSONMemoryStorage(MemoryStorage):
    """Local JSON file implementation of MemoryStorage."""

    def __init__(self, file_path: Optional[Path] = None) -> None:
        if file_path is None:
            # Default to monorepo config/memory.json
            self.file_path = Path("config/memory.json")
        else:
            self.file_path = file_path

        self._memories: Dict[str, Memory] = {}
        self._load_from_file()

    def _load_from_file(self) -> None:
        if not self.file_path.exists():
            self._memories = {}
            return

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            memories = {}
            for item in data:
                metadata_data = item.get("metadata", {})
                metadata = MemoryMetadata(
                    workspace_id=metadata_data.get("workspace_id", ""),
                    session_id=metadata_data.get("session_id", ""),
                    tags=metadata_data.get("tags", []),
                    importance=metadata_data.get("importance", 1),
                    additional=metadata_data.get("additional", {}),
                )
                memory = Memory(
                    memory_id=item.get("memory_id", ""),
                    content=item.get("content", ""),
                    memory_type=MemoryType(item.get("memory_type", "note")),
                    metadata=metadata,
                    created_at=item.get("created_at", 0.0),
                    updated_at=item.get("updated_at", 0.0),
                )
                memories[memory.memory_id] = memory
            self._memories = memories
        except Exception as e:
            logger.error(f"Failed to load memories from file: {e}")
            self._memories = {}

    def save_memory(self, memory: Memory) -> None:
        self._memories[memory.memory_id] = memory

    def get_memory(self, memory_id: str) -> Optional[Memory]:
        return self._memories.get(memory_id)

    def delete_memory(self, memory_id: str) -> None:
        if memory_id in self._memories:
            del self._memories[memory_id]

    def load_all_memories(self) -> List[Memory]:
        return list(self._memories.values())

    def commit(self) -> None:
        try:
            self.file_path.parent.mkdir(parents=True, exist_ok=True)

            data = []
            for memory in self._memories.values():
                item = {
                    "memory_id": memory.memory_id,
                    "content": memory.content,
                    "memory_type": memory.memory_type.value,
                    "created_at": memory.created_at,
                    "updated_at": memory.updated_at,
                    "metadata": {
                        "workspace_id": memory.metadata.workspace_id,
                        "session_id": memory.metadata.session_id,
                        "tags": memory.metadata.tags,
                        "importance": memory.metadata.importance,
                        "additional": memory.metadata.additional,
                    },
                }
                data.append(item)

            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to commit memories to file: {e}")
            raise RuntimeError(f"Failed to commit memory storage: {e}") from e
