"""Universal Knowledge Graph — Interface & Data Models (Phase 4.5).

Provides the domain types and abstract service contract for the SQLite-backed
graph engine that connects Entities, Relationships, and Events across the AI OS.
"""

import abc
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from aios.services.base import ServiceLifecycle

# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------


class EntityType(Enum):
    PROJECT = "project"
    TASK = "task"
    DOCUMENT = "document"
    REPOSITORY = "repository"
    WORKFLOW = "workflow"
    MODEL = "model"
    DECISION = "decision"
    CLIENT = "client"
    RESEARCH = "research"
    NOTION_PAGE = "notion_page"
    # Phase 6 CRM Entities
    PERSON = "person"
    COMPANY = "company"
    LEAD = "lead"
    MEETING = "meeting"
    PROPOSAL = "proposal"
    CONTRACT = "contract"
    # Phase 7 Automation Entities
    DEPLOYMENT = "deployment"
    WEBHOOK = "webhook"
    EXECUTION = "execution"
    CREDENTIAL = "credential"
    WORKFLOW_TEMPLATE = "workflow_template"
    # Phase 7.5 Integration Entities
    INTEGRATION = "integration"
    CONNECTOR = "connector"
    EVENT_SOURCE = "event_source"
    # Phase 8 Documentation Entities
    SECTION = "section"
    RELEASE = "release"
    REPORT = "report"


class RelationshipType(Enum):
    BELONGS_TO = "BELONGS_TO"
    USES = "USES"
    CREATED_BY = "CREATED_BY"
    DEPENDS_ON = "DEPENDS_ON"
    SUPPORTS = "SUPPORTS"
    REFERENCES = "REFERENCES"
    CONTAINS = "CONTAINS"
    RELATED_TO = "RELATED_TO"
    # Phase 6 CRM Relationships
    WORKS_FOR = "WORKS_FOR"
    OWNS = "OWNS"
    ATTENDED = "ATTENDED"
    CREATED = "CREATED"
    SENT_TO = "SENT_TO"
    CONVERTED_TO = "CONVERTED_TO"
    MANAGES = "MANAGES"
    # Phase 7 Automation Relationships
    SERVES = "SERVES"
    DEPLOYED_BY = "DEPLOYED_BY"
    EXECUTES = "EXECUTES"
    CALLS = "CALLS"
    # Phase 7.5 Integration Relationships
    CONNECTED_TO = "CONNECTED_TO"
    EMITS = "EMITS"
    AUTHENTICATES = "AUTHENTICATES"
    SYNCS = "SYNCS"
    # Phase 8 Documentation Relationships
    DOCUMENTS = "DOCUMENTS"
    DESCRIBES = "DESCRIBES"
    GENERATED_FROM = "GENERATED_FROM"


class GraphEventType(Enum):
    ENTITY_CREATED = "entity_created"
    ENTITY_UPDATED = "entity_updated"
    ENTITY_DELETED = "entity_deleted"
    RELATIONSHIP_CREATED = "relationship_created"
    RELATIONSHIP_DELETED = "relationship_deleted"
    GRAPH_QUERIED = "graph_queried"


# ---------------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------------


@dataclass
class GraphEntity:
    """A node in the knowledge graph."""

    entity_id: str
    entity_type: EntityType
    name: str
    properties: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "entity_id": self.entity_id,
            "entity_type": self.entity_type.value,
            "name": self.name,
            "properties": self.properties,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GraphEntity":
        return cls(
            entity_id=data["entity_id"],
            entity_type=EntityType(data["entity_type"]),
            name=data["name"],
            properties=data.get("properties", {}),
            created_at=data.get("created_at", time.time()),
            updated_at=data.get("updated_at", time.time()),
        )


@dataclass
class GraphRelationship:
    """A directed edge between two entities in the knowledge graph."""

    relationship_id: str
    source_id: str
    target_id: str
    relationship_type: RelationshipType
    properties: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "relationship_id": self.relationship_id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relationship_type": self.relationship_type.value,
            "properties": self.properties,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GraphRelationship":
        return cls(
            relationship_id=data["relationship_id"],
            source_id=data["source_id"],
            target_id=data["target_id"],
            relationship_type=RelationshipType(data["relationship_type"]),
            properties=data.get("properties", {}),
            created_at=data.get("created_at", time.time()),
        )


@dataclass
class GraphEvent:
    """An immutable event recorded in the knowledge graph audit log."""

    event_id: str
    event_type: GraphEventType
    entity_id: Optional[str]
    relationship_id: Optional[str]
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "entity_id": self.entity_id,
            "relationship_id": self.relationship_id,
            "payload": self.payload,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GraphEvent":
        return cls(
            event_id=data["event_id"],
            event_type=GraphEventType(data["event_type"]),
            entity_id=data.get("entity_id"),
            relationship_id=data.get("relationship_id"),
            payload=data.get("payload", {}),
            timestamp=data.get("timestamp", time.time()),
        )


@dataclass
class GraphQueryResult:
    """Result container for graph query operations."""

    entities: List[GraphEntity] = field(default_factory=list)
    relationships: List[GraphRelationship] = field(default_factory=list)
    events: List[GraphEvent] = field(default_factory=list)
    total_count: int = 0
    query_time_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GraphStats:
    """Aggregate statistics for the knowledge graph."""

    total_entities: int = 0
    total_relationships: int = 0
    total_events: int = 0
    entity_counts: Dict[str, int] = field(default_factory=dict)
    relationship_counts: Dict[str, int] = field(default_factory=dict)
    generated_at: float = field(default_factory=time.time)


# ---------------------------------------------------------------------------
# Helper factory
# ---------------------------------------------------------------------------


def new_entity(
    entity_type: EntityType,
    name: str,
    properties: Optional[Dict[str, Any]] = None,
) -> GraphEntity:
    """Create a new GraphEntity with a generated UUID."""
    return GraphEntity(
        entity_id=str(uuid.uuid4()),
        entity_type=entity_type,
        name=name,
        properties=properties or {},
    )


def new_relationship(
    source_id: str,
    target_id: str,
    relationship_type: RelationshipType,
    properties: Optional[Dict[str, Any]] = None,
) -> GraphRelationship:
    """Create a new GraphRelationship with a generated UUID."""
    return GraphRelationship(
        relationship_id=str(uuid.uuid4()),
        source_id=source_id,
        target_id=target_id,
        relationship_type=relationship_type,
        properties=properties or {},
    )


def new_event(
    event_type: GraphEventType,
    entity_id: Optional[str] = None,
    relationship_id: Optional[str] = None,
    payload: Optional[Dict[str, Any]] = None,
) -> GraphEvent:
    """Create a new GraphEvent with a generated UUID."""
    return GraphEvent(
        event_id=str(uuid.uuid4()),
        event_type=event_type,
        entity_id=entity_id,
        relationship_id=relationship_id,
        payload=payload or {},
    )


# ---------------------------------------------------------------------------
# Abstract Service Interface
# ---------------------------------------------------------------------------


class GraphService(ServiceLifecycle, abc.ABC):
    """Abstract interface for the Universal Knowledge Graph engine."""

    # ---- Entity operations ------------------------------------------------

    @abc.abstractmethod
    def create_entity(self, entity: GraphEntity) -> GraphEntity:
        """Persist a new entity node to the graph."""

    @abc.abstractmethod
    def get_entity(self, entity_id: str) -> Optional[GraphEntity]:
        """Retrieve an entity by its ID."""

    @abc.abstractmethod
    def find_entities(
        self,
        entity_type: Optional[EntityType] = None,
        name_contains: Optional[str] = None,
        limit: int = 50,
    ) -> List[GraphEntity]:
        """Search entities by type and/or name substring."""

    @abc.abstractmethod
    def update_entity(self, entity_id: str, updates: Dict[str, Any]) -> Optional[GraphEntity]:
        """Update entity properties."""

    @abc.abstractmethod
    def delete_entity(self, entity_id: str) -> bool:
        """Remove an entity and all its relationships from the graph."""

    # ---- Relationship operations -------------------------------------------

    @abc.abstractmethod
    def create_relationship(self, relationship: GraphRelationship) -> GraphRelationship:
        """Persist a directed relationship between two entities."""

    @abc.abstractmethod
    def get_relationship(self, relationship_id: str) -> Optional[GraphRelationship]:
        """Retrieve a relationship by its ID."""

    @abc.abstractmethod
    def find_relationships(
        self,
        source_id: Optional[str] = None,
        target_id: Optional[str] = None,
        relationship_type: Optional[RelationshipType] = None,
        limit: int = 50,
    ) -> List[GraphRelationship]:
        """Query relationships with optional source/target/type filters."""

    @abc.abstractmethod
    def delete_relationship(self, relationship_id: str) -> bool:
        """Remove a specific relationship from the graph."""

    # ---- Event operations -------------------------------------------------

    @abc.abstractmethod
    def record_event(self, event: GraphEvent) -> GraphEvent:
        """Append an immutable audit event to the graph log."""

    @abc.abstractmethod
    def get_events(
        self,
        entity_id: Optional[str] = None,
        event_type: Optional[GraphEventType] = None,
        limit: int = 100,
    ) -> List[GraphEvent]:
        """Retrieve events filtered by entity or type."""

    # ---- Query operations -------------------------------------------------

    @abc.abstractmethod
    def get_neighbors(
        self,
        entity_id: str,
        relationship_type: Optional[RelationshipType] = None,
        direction: str = "both",
    ) -> GraphQueryResult:
        """Return entities connected to the given entity.

        Args:
            entity_id: The focal entity.
            relationship_type: Optional filter on the edge label.
            direction: "outbound" | "inbound" | "both".
        """

    @abc.abstractmethod
    def find_path(self, source_id: str, target_id: str, max_depth: int = 5) -> GraphQueryResult:
        """Find a shortest path between two entities via BFS."""

    @abc.abstractmethod
    def search(self, query: str, limit: int = 20) -> GraphQueryResult:
        """Full-text search across entity names and properties."""

    @abc.abstractmethod
    def get_project_subgraph(self, project_entity_id: str) -> GraphQueryResult:
        """Return the full subgraph rooted at a project entity."""

    # ---- Stats & health ---------------------------------------------------

    @abc.abstractmethod
    def get_stats(self) -> GraphStats:
        """Return aggregate statistics for the graph."""

    @abc.abstractmethod
    def health_check(self) -> bool:
        """Verify the graph engine is operational."""
