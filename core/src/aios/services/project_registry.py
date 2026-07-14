"""Phase 5: Project Intelligence — Project Registry, Memory & Context.

Defines the canonical data models for projects, profiles, and project context,
plus the abstract service interfaces for the full project intelligence layer.
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
# Enumerations
# ---------------------------------------------------------------------------


class ProjectType(Enum):
    SOFTWARE = "software"
    AGENCY = "agency"
    RESEARCH = "research"
    COLLEGE = "college"
    HACKATHON = "hackathon"
    PORTFOLIO = "portfolio"
    AUTOMATION = "automation"
    OTHER = "other"


class ProjectStatus(Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"
    PLANNING = "planning"


class ProjectPriority(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


# ---------------------------------------------------------------------------
# Integration Config sub-dataclasses
# ---------------------------------------------------------------------------


@dataclass
class GitHubProjectConfig:
    enabled: bool = False
    repo: str = ""
    branch: str = "main"
    auto_sync: bool = True


@dataclass
class NotionProjectConfig:
    enabled: bool = False
    workspace_id: str = ""
    database_id: str = ""
    auto_sync: bool = True


@dataclass
class N8nProjectConfig:
    enabled: bool = False
    workflow_ids: List[str] = field(default_factory=list)
    auto_monitor: bool = True


@dataclass
class MemoryProjectConfig:
    enabled: bool = True
    namespace: str = ""  # Defaults to project_id
    retention_days: int = 365


@dataclass
class KnowledgeGraphProjectConfig:
    enabled: bool = True
    entity_id: str = ""  # Populated after graph node creation


# ---------------------------------------------------------------------------
# Core Project Models
# ---------------------------------------------------------------------------


@dataclass
class ProjectProfile:
    """Full configuration profile for a project."""

    project_id: str
    name: str
    description: str
    project_type: ProjectType
    status: ProjectStatus
    priority: ProjectPriority
    owner: str
    preferred_models: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    github: GitHubProjectConfig = field(default_factory=GitHubProjectConfig)
    notion: NotionProjectConfig = field(default_factory=NotionProjectConfig)
    n8n: N8nProjectConfig = field(default_factory=N8nProjectConfig)
    memory: MemoryProjectConfig = field(default_factory=MemoryProjectConfig)
    knowledge_graph: KnowledgeGraphProjectConfig = field(
        default_factory=KnowledgeGraphProjectConfig
    )
    created_at: float = field(default_factory=time.time)
    last_active: float = field(default_factory=time.time)
    workspace_path: str = ""
    current_sprint: str = ""
    current_phase: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "project_id": self.project_id,
            "name": self.name,
            "description": self.description,
            "project_type": self.project_type.value,
            "status": self.status.value,
            "priority": self.priority.value,
            "owner": self.owner,
            "preferred_models": self.preferred_models,
            "tags": self.tags,
            "github": {
                "enabled": self.github.enabled,
                "repo": self.github.repo,
                "branch": self.github.branch,
                "auto_sync": self.github.auto_sync,
            },
            "notion": {
                "enabled": self.notion.enabled,
                "workspace_id": self.notion.workspace_id,
                "database_id": self.notion.database_id,
                "auto_sync": self.notion.auto_sync,
            },
            "n8n": {
                "enabled": self.n8n.enabled,
                "workflow_ids": self.n8n.workflow_ids,
                "auto_monitor": self.n8n.auto_monitor,
            },
            "memory": {
                "enabled": self.memory.enabled,
                "namespace": self.memory.namespace,
                "retention_days": self.memory.retention_days,
            },
            "knowledge_graph": {
                "enabled": self.knowledge_graph.enabled,
                "entity_id": self.knowledge_graph.entity_id,
            },
            "created_at": self.created_at,
            "last_active": self.last_active,
            "workspace_path": self.workspace_path,
            "current_sprint": self.current_sprint,
            "current_phase": self.current_phase,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProjectProfile":
        github_data = data.get("github", {})
        notion_data = data.get("notion", {})
        n8n_data = data.get("n8n", {})
        memory_data = data.get("memory", {})
        kg_data = data.get("knowledge_graph", {})

        return cls(
            project_id=data["project_id"],
            name=data["name"],
            description=data.get("description", ""),
            project_type=ProjectType(data.get("project_type", "software")),
            status=ProjectStatus(data.get("status", "active")),
            priority=ProjectPriority(data.get("priority", "medium")),
            owner=data.get("owner", ""),
            preferred_models=data.get("preferred_models", []),
            tags=data.get("tags", []),
            github=GitHubProjectConfig(
                enabled=github_data.get("enabled", False),
                repo=github_data.get("repo", ""),
                branch=github_data.get("branch", "main"),
                auto_sync=github_data.get("auto_sync", True),
            ),
            notion=NotionProjectConfig(
                enabled=notion_data.get("enabled", False),
                workspace_id=notion_data.get("workspace_id", ""),
                database_id=notion_data.get("database_id", ""),
                auto_sync=notion_data.get("auto_sync", True),
            ),
            n8n=N8nProjectConfig(
                enabled=n8n_data.get("enabled", False),
                workflow_ids=n8n_data.get("workflow_ids", []),
                auto_monitor=n8n_data.get("auto_monitor", True),
            ),
            memory=MemoryProjectConfig(
                enabled=memory_data.get("enabled", True),
                namespace=memory_data.get("namespace", ""),
                retention_days=memory_data.get("retention_days", 365),
            ),
            knowledge_graph=KnowledgeGraphProjectConfig(
                enabled=kg_data.get("enabled", True),
                entity_id=kg_data.get("entity_id", ""),
            ),
            created_at=data.get("created_at", time.time()),
            last_active=data.get("last_active", time.time()),
            workspace_path=data.get("workspace_path", ""),
            current_sprint=data.get("current_sprint", ""),
            current_phase=data.get("current_phase", ""),
            metadata=data.get("metadata", {}),
        )


@dataclass
class ProjectRuntimeContext:
    """Isolated runtime context for a project."""

    project_id: str
    project_name: str
    current_sprint: str = ""
    current_phase: str = ""
    active_branch: str = "main"
    active_models: List[str] = field(default_factory=list)
    open_tasks: List[Dict[str, Any]] = field(default_factory=list)
    goals: List[Dict[str, Any]] = field(default_factory=list)
    documents: List[str] = field(default_factory=list)
    recent_activity: List[Dict[str, Any]] = field(default_factory=list)
    decisions: List[Dict[str, Any]] = field(default_factory=list)
    github_status: Dict[str, Any] = field(default_factory=dict)
    notion_status: Dict[str, Any] = field(default_factory=dict)
    workflow_status: Dict[str, Any] = field(default_factory=dict)
    graph_entity_id: str = ""
    last_switched: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "project_id": self.project_id,
            "project_name": self.project_name,
            "current_sprint": self.current_sprint,
            "current_phase": self.current_phase,
            "active_branch": self.active_branch,
            "active_models": self.active_models,
            "open_tasks": self.open_tasks,
            "goals": self.goals,
            "documents": self.documents,
            "recent_activity": self.recent_activity,
            "decisions": self.decisions,
            "github_status": self.github_status,
            "notion_status": self.notion_status,
            "workflow_status": self.workflow_status,
            "graph_entity_id": self.graph_entity_id,
            "last_switched": self.last_switched,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProjectRuntimeContext":
        return cls(
            project_id=data["project_id"],
            project_name=data["project_name"],
            current_sprint=data.get("current_sprint", ""),
            current_phase=data.get("current_phase", ""),
            active_branch=data.get("active_branch", "main"),
            active_models=data.get("active_models", []),
            open_tasks=data.get("open_tasks", []),
            goals=data.get("goals", []),
            documents=data.get("documents", []),
            recent_activity=data.get("recent_activity", []),
            decisions=data.get("decisions", []),
            github_status=data.get("github_status", {}),
            notion_status=data.get("notion_status", {}),
            workflow_status=data.get("workflow_status", {}),
            graph_entity_id=data.get("graph_entity_id", ""),
            last_switched=data.get("last_switched", time.time()),
        )


@dataclass
class ProjectMemoryEntry:
    """A single memory entry scoped to a project."""

    entry_id: str
    project_id: str
    category: (
        str  # conversations|decisions|architecture|research|meetings|tasks|milestones|benchmarks
    )
    title: str
    content: str
    tags: List[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "entry_id": self.entry_id,
            "project_id": self.project_id,
            "category": self.category,
            "title": self.title,
            "content": self.content,
            "tags": self.tags,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProjectMemoryEntry":
        return cls(
            entry_id=data["entry_id"],
            project_id=data["project_id"],
            category=data.get("category", "notes"),
            title=data["title"],
            content=data.get("content", ""),
            tags=data.get("tags", []),
            created_at=data.get("created_at", time.time()),
            updated_at=data.get("updated_at", time.time()),
        )


@dataclass
class CrossProjectQuery:
    """Result of a cross-project intelligence query."""

    query_type: str
    results: List[Dict[str, Any]] = field(default_factory=list)
    project_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Factory helpers
# ---------------------------------------------------------------------------


def new_project_id() -> str:
    return str(uuid.uuid4())


def new_entry_id() -> str:
    return str(uuid.uuid4())


# ---------------------------------------------------------------------------
# Abstract Service Interfaces
# ---------------------------------------------------------------------------


class ProjectRegistryService(ServiceLifecycle, abc.ABC):
    """Stores and retrieves project profiles."""

    @abc.abstractmethod
    def register_project(self, profile: ProjectProfile) -> ProjectProfile:
        """Add or update a project profile."""

    @abc.abstractmethod
    def get_project(self, project_id: str) -> Optional[ProjectProfile]:
        """Retrieve a project profile by ID."""

    @abc.abstractmethod
    def find_project(self, name: str) -> Optional[ProjectProfile]:
        """Find a project by name (case-insensitive)."""

    @abc.abstractmethod
    def list_projects(
        self,
        project_type: Optional[ProjectType] = None,
        status: Optional[ProjectStatus] = None,
    ) -> List[ProjectProfile]:
        """List all registered projects, optionally filtered."""

    @abc.abstractmethod
    def update_project(self, project_id: str, updates: Dict[str, Any]) -> Optional[ProjectProfile]:
        """Update mutable fields on a project profile."""

    @abc.abstractmethod
    def delete_project(self, project_id: str) -> bool:
        """Remove a project from the registry."""

    @abc.abstractmethod
    def set_active_project(self, project_id: str) -> bool:
        """Mark a project as the currently active project."""

    @abc.abstractmethod
    def get_active_project(self) -> Optional[ProjectProfile]:
        """Return the currently active project profile."""

    @abc.abstractmethod
    def detect_project_from_workspace(self, workspace_path: str) -> Optional[ProjectProfile]:
        """Auto-detect project from a directory path."""

    @abc.abstractmethod
    def query_by_integration(self, integration: str) -> List[ProjectProfile]:
        """Return all projects using a specific integration (e.g. 'supabase', 'ollama')."""

    @abc.abstractmethod
    def find_related_projects(self, project_id: str) -> List[ProjectProfile]:
        """Find projects related by shared tags, models, or integrations."""

    @abc.abstractmethod
    def get_projects_needing_attention(self) -> List[ProjectProfile]:
        """Return paused/planning projects that haven't been active recently."""


class ProjectMemoryService(ServiceLifecycle, abc.ABC):
    """Per-project memory storage."""

    @abc.abstractmethod
    def store(self, entry: ProjectMemoryEntry) -> ProjectMemoryEntry:
        """Persist a memory entry for a project."""

    @abc.abstractmethod
    def retrieve(
        self,
        project_id: str,
        category: Optional[str] = None,
        limit: int = 50,
    ) -> List[ProjectMemoryEntry]:
        """Retrieve memory entries for a project."""

    @abc.abstractmethod
    def search(self, project_id: str, query: str, limit: int = 20) -> List[ProjectMemoryEntry]:
        """Search memory entries by content or title."""

    @abc.abstractmethod
    def delete_entry(self, entry_id: str) -> bool:
        """Remove a specific memory entry."""

    @abc.abstractmethod
    def get_recent(self, project_id: str, limit: int = 10) -> List[ProjectMemoryEntry]:
        """Retrieve the most recently updated entries for a project."""


class ProjectContextService(ServiceLifecycle, abc.ABC):
    """Per-project context management and context switching."""

    @abc.abstractmethod
    def get_context(self, project_id: str) -> Optional[ProjectRuntimeContext]:
        """Return the current context for a project."""

    @abc.abstractmethod
    def update_context(self, project_id: str, updates: Dict[str, Any]) -> ProjectRuntimeContext:
        """Update context fields for a project."""

    @abc.abstractmethod
    def switch_to(self, project_id: str) -> ProjectRuntimeContext:
        """Switch the active context to a different project."""

    @abc.abstractmethod
    def get_active_context(self) -> Optional[ProjectRuntimeContext]:
        """Return the currently active project context."""

    @abc.abstractmethod
    def get_dashboard_data(self, project_id: str) -> Dict[str, Any]:
        """Assemble dashboard data for a project."""
