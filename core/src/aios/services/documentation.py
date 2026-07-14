"""Phase 8: Documentation Intelligence — Interfaces and Dataclasses.

Defines the Document structures, registry schemas, decision log systems,
and documentation engines interface contract.
"""

from __future__ import annotations

import abc
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from aios.services.base import ServiceLifecycle

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class DocType(Enum):
    README = "readme"
    ARCHITECTURE = "architecture"
    API_DOCS = "api_docs"
    DEV_GUIDE = "dev_guide"
    SPRINT_REPORT = "sprint_report"
    RELEASE_NOTES = "release_notes"
    PROJECT_DOCS = "project_docs"
    WORKFLOW_DOCS = "workflow_docs"
    INTEGRATION_DOCS = "integration_docs"
    RESEARCH_DOCS = "research_docs"
    AGENCY_DOCS = "agency_docs"
    MEETING_NOTES = "meeting_notes"
    TECH_DECISIONS = "tech_decisions"


class DocStatus(Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    OUTDATED = "outdated"


# ---------------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------------


@dataclass
class DocumentRecord:
    document_id: str
    title: str
    doc_type: DocType
    content: str = ""
    project_id: str = ""
    owner: str = ""
    status: DocStatus = DocStatus.DRAFT
    version: int = 1
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    related_entities: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "document_id": self.document_id,
            "title": self.title,
            "doc_type": self.doc_type.value,
            "content": self.content,
            "project_id": self.project_id,
            "owner": self.owner,
            "status": self.status.value,
            "version": self.version,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "related_entities": self.related_entities,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> DocumentRecord:
        import json as _json

        related_entities = data.get("related_entities", [])
        if isinstance(related_entities, str):
            try:
                related_entities = _json.loads(related_entities)
            except Exception:
                related_entities = []

        return cls(
            document_id=data["document_id"],
            title=data["title"],
            doc_type=DocType(data.get("doc_type", "readme")),
            content=data.get("content", ""),
            project_id=data.get("project_id", ""),
            owner=data.get("owner", ""),
            status=DocStatus(data.get("status", "draft")),
            version=data.get("version", 1),
            created_at=data.get("created_at", time.time()),
            updated_at=data.get("updated_at", time.time()),
            related_entities=related_entities,
        )


@dataclass
class DecisionRecord:
    decision_id: str
    title: str
    category: str  # architectural|technology|model|workflow|agency
    status: str  # proposed|accepted|rejected|deprecated
    context: str
    consequences: str
    owner: str = ""
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "decision_id": self.decision_id,
            "title": self.title,
            "category": self.category,
            "status": self.status,
            "context": self.context,
            "consequences": self.consequences,
            "owner": self.owner,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> DecisionRecord:
        return cls(
            decision_id=data["decision_id"],
            title=data["title"],
            category=data.get("category", "architectural"),
            status=data.get("status", "proposed"),
            context=data.get("context", ""),
            consequences=data.get("consequences", ""),
            owner=data.get("owner", ""),
            timestamp=data.get("timestamp", time.time()),
        )


# ---------------------------------------------------------------------------
# Factory Helpers
# ---------------------------------------------------------------------------


def new_id() -> str:
    return str(uuid.uuid4())


# ---------------------------------------------------------------------------
# Service Interface
# ---------------------------------------------------------------------------


class DocumentationService(ServiceLifecycle, abc.ABC):
    """Auto-generates, updates, indexes, versions, and searches project/OS documentations."""

    @abc.abstractmethod
    def register_document(self, doc: DocumentRecord) -> DocumentRecord:
        """Store or update a generated documentation page record."""

    @abc.abstractmethod
    def get_document(self, document_id: str) -> Optional[DocumentRecord]:
        """Fetch a documentation record."""

    @abc.abstractmethod
    def list_documents(self) -> List[DocumentRecord]:
        """List all documents."""

    @abc.abstractmethod
    def delete_document(self, document_id: str) -> bool:
        """Remove a document."""

    # ── Decision Logs ────────────────────────────────────────────────────────
    @abc.abstractmethod
    def record_decision(self, decision: DecisionRecord) -> DecisionRecord:
        """Store a tech or architectural decision record."""

    @abc.abstractmethod
    def list_decisions(self) -> List[DecisionRecord]:
        """List all decisions."""

    # ── Search Engine ────────────────────────────────────────────────────────
    @abc.abstractmethod
    def search_documents(self, query: str) -> List[DocumentRecord]:
        """Search registered documentations by keywords matching title or content."""

    # ── Documentation Engine Builders ────────────────────────────────────────
    @abc.abstractmethod
    def generate_readme(self, project_id: str) -> DocumentRecord:
        """Create structured README.md including overview, installation, and commands."""

    @abc.abstractmethod
    def generate_architecture_doc(self, project_id: str) -> DocumentRecord:
        """Create structured architecture doc detailing Component/Service dependencies."""

    @abc.abstractmethod
    def generate_api_doc(self, module_name: str) -> DocumentRecord:
        """Create service interfaces API documentations."""
