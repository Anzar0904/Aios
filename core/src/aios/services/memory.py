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


class MemoryCategory(Enum):
    CONVERSATION = "Conversation"
    DAILY_REVIEW = "Daily Review"
    CAREER = "Career"
    PROJECT = "Project"
    GITHUB = "GitHub"
    RESEARCH = "Research"
    MISSION = "Mission"
    LEARNING = "Learning"
    WORKFLOW = "Workflow"
    PERSONAL = "Personal"


class MemoryImportance(Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class RetrievalStrategy(Enum):
    MISSION = "mission"
    PROJECT = "project"
    COMPANY = "company"
    TECHNOLOGY = "technology"
    CONVERSATION = "conversation"
    CAREER = "career"
    LEARNING = "learning"
    DATE = "date"
    TAGS = "tags"
    MIXED = "mixed"


@dataclass
class MemoryReference:
    reference_id: str
    reference_type: str  # e.g., "mission", "project", "file", "commit"
    description: Optional[str] = None


@dataclass
class MemoryMetadata:
    workspace_id: str
    session_id: str
    tags: List[str] = field(default_factory=list)
    importance: int = 1
    additional: Dict[str, Any] = field(default_factory=dict)

    # Extended Memory Intelligence fields
    unique_id: str = ""
    timestamp: float = 0.0
    source_subsystem: str = ""
    category: Optional[MemoryCategory] = None
    importance_score: Optional[MemoryImportance] = None
    related_mission: Optional[str] = None
    related_project: Optional[str] = None
    related_company: Optional[str] = None
    related_technologies: List[str] = field(default_factory=list)
    related_skills: List[str] = field(default_factory=list)
    related_files: List[str] = field(default_factory=list)
    references: List[MemoryReference] = field(default_factory=list)


@dataclass
class Memory:
    memory_id: str
    content: str
    memory_type: MemoryType
    metadata: MemoryMetadata
    created_at: float
    updated_at: float


@dataclass
class RetrievalContext:
    objective: str
    active_mission: Optional[str] = None
    active_project: Optional[str] = None
    strategy: RetrievalStrategy = RetrievalStrategy.MIXED
    max_results: int = 5
    limit_bytes: int = 4000
    additional_filters: Dict[str, Any] = field(default_factory=dict)


class MemoryFilter(abc.ABC):
    @abc.abstractmethod
    def filter_memories(self, memories: List[Memory], context: RetrievalContext) -> List[Memory]:
        """Filters memories by relevance, recency, importance, and size limits."""
        pass


class MemorySelector(abc.ABC):
    @abc.abstractmethod
    def select_memories(self, memories: List[Memory], context: RetrievalContext) -> List[Memory]:
        """Orders and trims memories to the smallest useful set to avoid prompt inflation."""
        pass


class MemoryRetriever(abc.ABC):
    @abc.abstractmethod
    def retrieve(self, context: RetrievalContext) -> List[Memory]:
        """Retrieves and filters memories matching a user objective or strategy."""
        pass


class MemoryClassifier(abc.ABC):
    @abc.abstractmethod
    def classify_memory(
        self, content: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Automatically classifies memory content, extracting category, importance, tags,
        related projects, missions, companies, technologies, skills, and files.
        """
        pass


class MemoryIndexer(abc.ABC):
    @abc.abstractmethod
    def index_memory(self, memory: Memory) -> None:
        """Indexes a memory for lookup."""
        pass

    @abc.abstractmethod
    def deindex_memory(self, memory_id: str) -> None:
        """Removes a memory from the index."""
        pass

    @abc.abstractmethod
    def lookup(
        self,
        category: Optional[MemoryCategory] = None,
        tags: Optional[List[str]] = None,
        mission: Optional[str] = None,
        project: Optional[str] = None,
        company: Optional[str] = None,
        technology: Optional[str] = None,
        start_date: Optional[float] = None,
        end_date: Optional[float] = None,
    ) -> List[Memory]:
        """Retrieves memories matching index constraints."""
        pass


class MemoryService(ServiceLifecycle, abc.ABC):
    """Interface for loading, updating, committing, and organizing knowledge across sessions."""

    @property
    @abc.abstractmethod
    def classifier(self) -> MemoryClassifier:
        pass

    @property
    @abc.abstractmethod
    def indexer(self) -> MemoryIndexer:
        pass

    @property
    @abc.abstractmethod
    def retriever(self) -> MemoryRetriever:
        pass

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
