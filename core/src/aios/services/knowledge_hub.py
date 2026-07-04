import abc
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from aios.services.base import ServiceLifecycle


class KnowledgeOperation(Enum):
    CREATE = "create"
    UPDATE = "update"
    READ = "read"
    DELETE = "delete"
    SYNC = "sync"


class KnowledgeSyncPolicy(Enum):
    PERIODIC = "periodic"
    ON_DEMAND = "on_demand"
    MANUAL = "manual"


@dataclass
class KnowledgeMetadata:
    unique_id: str
    timestamp: float
    source_subsystem: str
    category: str  # e.g., "Daily Review", "Career", "Project", "GitHub", "Research", "Mission"
    tags: List[str] = field(default_factory=list)
    version: int = 1
    content_hash: str = ""
    last_modified: float = 0.0
    provider_page_id: Optional[str] = None
    provider_db_id: Optional[str] = None
    sync_status: str = "pending"  # "pending", "synced", "failed"
    additional: Dict[str, Any] = field(default_factory=dict)


@dataclass
class KnowledgeReference:
    reference_id: str
    reference_type: str  # e.g. "notion_page", "memory_id"
    provider: str  # e.g. "notion"
    url: Optional[str] = None


@dataclass
class KnowledgeDocument:
    document_id: str
    title: str
    content: str  # markdown or plain text
    metadata: KnowledgeMetadata
    references: List[KnowledgeReference] = field(default_factory=list)


@dataclass
class KnowledgePage:
    page_id: str
    title: str
    properties: Dict[str, Any] = field(default_factory=dict)
    content: str = ""  # markdown representation
    url: Optional[str] = None


@dataclass
class KnowledgeSyncResult:
    document_id: str
    provider: str
    status: str  # "success", "skipped", "failed"
    provider_page_id: Optional[str] = None
    timestamp: float = 0.0
    error_message: Optional[str] = None


class KnowledgeProvider(abc.ABC):
    @abc.abstractmethod
    def get_name(self) -> str:
        """Returns the provider name (e.g. 'notion')."""
        pass

    @abc.abstractmethod
    def authenticate(self) -> bool:
        """Verifies authentication credentials with the external system."""
        pass

    @abc.abstractmethod
    def discover_databases(self) -> List[Dict[str, Any]]:
        """Discovers accessible databases."""
        pass

    @abc.abstractmethod
    def discover_pages(self) -> List[KnowledgePage]:
        """Discovers accessible root pages."""
        pass

    @abc.abstractmethod
    def search(self, query: str) -> List[KnowledgePage]:
        """Searches the provider for matching pages."""
        pass

    @abc.abstractmethod
    def read_page(self, page_id: str) -> Optional[KnowledgePage]:
        """Reads a specific page from the provider."""
        pass

    @abc.abstractmethod
    def create_page(
        self,
        parent_id: str,
        title: str,
        content: str,
        properties: Optional[Dict[str, Any]] = None,
    ) -> Optional[KnowledgePage]:
        """Creates a page under a parent page or inside a database."""
        pass

    @abc.abstractmethod
    def update_page(
        self,
        page_id: str,
        title: Optional[str] = None,
        content: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None,
    ) -> Optional[KnowledgePage]:
        """Updates an existing page's title, content, or properties."""
        pass


class KnowledgeHubService(ServiceLifecycle, abc.ABC):
    @abc.abstractmethod
    def register_provider(self, provider: KnowledgeProvider) -> None:
        """Registers a knowledge sync provider."""
        pass

    @abc.abstractmethod
    def get_provider(self, name: str) -> Optional[KnowledgeProvider]:
        """Retrieves a registered provider by name."""
        pass

    @abc.abstractmethod
    def sync_document(self, doc: KnowledgeDocument, provider_name: str) -> KnowledgeSyncResult:
        """Synchronizes a KnowledgeDocument with an external provider."""
        pass

    @abc.abstractmethod
    def get_sync_status(self, document_id: str) -> Optional[KnowledgeMetadata]:
        """Gets the sync metadata for a specific document."""
        pass
