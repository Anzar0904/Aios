"""Phase 5: Project Intelligence — SQLite-backed Implementation.

Implements ProjectRegistryService, ProjectMemoryService, and ProjectContextService
using a single SQLite database for zero-dependency, CI-compatible operation.
"""

from __future__ import annotations

import json
import logging
import os
import sqlite3
import time
from contextlib import contextmanager
from threading import Lock
from typing import Any, Dict, Generator, List, Optional

from aios.services.project_registry import (
    GitHubProjectConfig,
    N8nProjectConfig,
    NotionProjectConfig,
    ProjectContextService,
    ProjectMemoryEntry,
    ProjectMemoryService,
    ProjectPriority,
    ProjectProfile,
    ProjectRegistryService,
    ProjectRuntimeContext,
    ProjectStatus,
    ProjectType,
    new_project_id,
)

logger = logging.getLogger(__name__)

_DEFAULT_DB = os.path.join(os.path.expanduser("~"), ".aios_projects.db")

# ── Canonical project catalogue ──────────────────────────────────────────────
BUILTIN_PROJECTS: List[Dict[str, Any]] = [
    {
        "name": "AI OS",
        "description": "Personal AI Operating System — core intelligence and workflow engine",
        "project_type": "software",
        "priority": "critical",
        "preferred_models": ["deepseek-coder-v2", "qwen2.5-coder", "deepseek-r1"],
        "tags": ["os", "ai", "core"],
        "github": {"enabled": True, "repo": "Anzar0904/Aios", "branch": "main"},
        "notion": {"enabled": True},
        "n8n": {"enabled": True},
        "current_phase": "Phase 5: Project Intelligence",
        "current_sprint": "Sprint 32",
    },
    {
        "name": "Agency",
        "description": "AI-powered freelance agency management and client operations",
        "project_type": "agency",
        "priority": "high",
        "preferred_models": ["qwen3.5", "gemma3:12b"],
        "tags": ["agency", "crm", "clients"],
        "github": {"enabled": False},
        "notion": {"enabled": True},
        "n8n": {"enabled": True},
    },
    {
        "name": "CampusConnect",
        "description": "University social and academic networking platform",
        "project_type": "software",
        "priority": "high",
        "preferred_models": ["deepseek-coder-v2", "qwen2.5-coder"],
        "tags": ["campus", "social", "university"],
        "github": {"enabled": True, "repo": "Anzar0904/CampusConnect"},
        "notion": {"enabled": True},
    },
    {
        "name": "College",
        "description": "Academic coursework, assignments, and exam preparation",
        "project_type": "college",
        "priority": "high",
        "preferred_models": ["deepseek-r1", "qwen3.5"],
        "tags": ["college", "academic", "education"],
        "notion": {"enabled": True},
    },
    {
        "name": "Research",
        "description": "AI/ML research experiments, benchmarks, and paper implementations",
        "project_type": "research",
        "priority": "medium",
        "preferred_models": ["deepseek-r1", "qwen3.5"],
        "tags": ["research", "ai", "ml", "benchmarks"],
        "notion": {"enabled": True},
    },
    {
        "name": "Hackathons",
        "description": "Active hackathon participation and rapid prototype development",
        "project_type": "hackathon",
        "priority": "high",
        "preferred_models": ["deepseek-coder-v2", "qwen2.5-coder"],
        "tags": ["hackathon", "prototype", "competition"],
        "github": {"enabled": True},
    },
    {
        "name": "Portfolio",
        "description": "Personal portfolio website and project showcase",
        "project_type": "portfolio",
        "priority": "medium",
        "preferred_models": ["deepseek-coder-v2"],
        "tags": ["portfolio", "web", "personal"],
        "github": {"enabled": True},
    },
]

# Workspace path keywords → project name mapping for auto-detection
_WORKSPACE_HINTS: Dict[str, str] = {
    "aios": "AI OS",
    "agency": "Agency",
    "campusconnect": "CampusConnect",
    "college": "College",
    "research": "Research",
    "hackathon": "Hackathons",
    "portfolio": "Portfolio",
}


class ProjectRegistryImpl(ProjectRegistryService):
    """SQLite-backed project registry."""

    def __init__(self, db_path: Optional[str] = None) -> None:
        self._db_path = db_path or os.getenv("AIOS_PROJECTS_DB", _DEFAULT_DB)
        self._lock = Lock()
        self._conn: Optional[sqlite3.Connection] = None

    # ── Lifecycle ────────────────────────────────────────────────────────────

    def initialize(self) -> None:
        self._conn = sqlite3.connect(self._db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._bootstrap_schema()
        self._seed_builtin_projects()
        logger.info("ProjectRegistry initialized — db: %s", self._db_path)

    def start(self) -> None:
        pass

    def shutdown(self) -> None:
        if self._conn:
            self._conn.close()
            self._conn = None

    def ready(self) -> bool:
        return self._conn is not None

    # ── Schema ───────────────────────────────────────────────────────────────

    def _bootstrap_schema(self) -> None:
        assert self._conn is not None
        with self._conn:
            self._conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS projects (
                    project_id    TEXT PRIMARY KEY,
                    name          TEXT NOT NULL UNIQUE,
                    data          TEXT NOT NULL DEFAULT '{}'
                );

                CREATE INDEX IF NOT EXISTS idx_projects_name ON projects(name COLLATE NOCASE);

                CREATE TABLE IF NOT EXISTS project_state (
                    key   TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );
                """
            )

    def _seed_builtin_projects(self) -> None:
        """Idempotently seed canonical projects on first run."""
        for spec in BUILTIN_PROJECTS:
            existing = self.find_project(spec["name"])
            if existing:
                continue
            pid = new_project_id()
            profile = ProjectProfile(
                project_id=pid,
                name=spec["name"],
                description=spec.get("description", ""),
                project_type=ProjectType(spec.get("project_type", "software")),
                status=ProjectStatus.ACTIVE,
                priority=ProjectPriority(spec.get("priority", "medium")),
                owner="Anzar Akhtar",
                preferred_models=spec.get("preferred_models", []),
                tags=spec.get("tags", []),
                github=GitHubProjectConfig(
                    enabled=spec.get("github", {}).get("enabled", False),
                    repo=spec.get("github", {}).get("repo", ""),
                    branch=spec.get("github", {}).get("branch", "main"),
                ),
                notion=NotionProjectConfig(
                    enabled=spec.get("notion", {}).get("enabled", False),
                ),
                n8n=N8nProjectConfig(
                    enabled=spec.get("n8n", {}).get("enabled", False),
                ),
                current_phase=spec.get("current_phase", ""),
                current_sprint=spec.get("current_sprint", ""),
            )
            self.register_project(profile)

    # ── Connection helper ─────────────────────────────────────────────────────

    @contextmanager
    def _tx(self) -> Generator[sqlite3.Connection, None, None]:
        assert self._conn is not None, "ProjectRegistry not initialized"
        with self._lock:
            with self._conn:
                yield self._conn

    # ── CRUD ─────────────────────────────────────────────────────────────────

    def register_project(self, profile: ProjectProfile) -> ProjectProfile:
        with self._tx() as conn:
            conn.execute(
                """
                INSERT INTO projects (project_id, name, data)
                VALUES (?, ?, ?)
                ON CONFLICT(project_id) DO UPDATE SET name=excluded.name, data=excluded.data
                """,
                (profile.project_id, profile.name, json.dumps(profile.to_dict())),
            )
        return profile

    def get_project(self, project_id: str) -> Optional[ProjectProfile]:
        assert self._conn is not None
        with self._lock:
            row = self._conn.execute(
                "SELECT data FROM projects WHERE project_id = ?", (project_id,)
            ).fetchone()
        return ProjectProfile.from_dict(json.loads(row["data"])) if row else None

    def find_project(self, name: str) -> Optional[ProjectProfile]:
        assert self._conn is not None
        with self._lock:
            row = self._conn.execute(
                "SELECT data FROM projects WHERE name = ? COLLATE NOCASE", (name,)
            ).fetchone()
        return ProjectProfile.from_dict(json.loads(row["data"])) if row else None

    def list_projects(
        self,
        project_type: Optional[ProjectType] = None,
        status: Optional[ProjectStatus] = None,
    ) -> List[ProjectProfile]:
        assert self._conn is not None
        with self._lock:
            rows = self._conn.execute("SELECT data FROM projects").fetchall()
        profiles = [ProjectProfile.from_dict(json.loads(r["data"])) for r in rows]
        if project_type:
            profiles = [p for p in profiles if p.project_type == project_type]
        if status:
            profiles = [p for p in profiles if p.status == status]
        return sorted(profiles, key=lambda p: p.last_active, reverse=True)

    def update_project(self, project_id: str, updates: Dict[str, Any]) -> Optional[ProjectProfile]:
        profile = self.get_project(project_id)
        if not profile:
            return None
        d = profile.to_dict()
        d.update(updates)
        d["last_active"] = time.time()
        updated = ProjectProfile.from_dict(d)
        self.register_project(updated)
        return updated

    def delete_project(self, project_id: str) -> bool:
        if not self.get_project(project_id):
            return False
        with self._tx() as conn:
            conn.execute("DELETE FROM projects WHERE project_id = ?", (project_id,))
        return True

    def set_active_project(self, project_id: str) -> bool:
        if not self.get_project(project_id):
            return False
        with self._tx() as conn:
            conn.execute(
                "INSERT INTO project_state (key, value) VALUES ('active_project', ?) "
                "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                (project_id,),
            )
        return True

    def get_active_project(self) -> Optional[ProjectProfile]:
        assert self._conn is not None
        with self._lock:
            row = self._conn.execute(
                "SELECT value FROM project_state WHERE key = 'active_project'"
            ).fetchone()
        if not row:
            # Default to AI OS
            return self.find_project("AI OS")
        return self.get_project(row["value"])

    def detect_project_from_workspace(self, workspace_path: str) -> Optional[ProjectProfile]:
        path_lower = workspace_path.lower()
        for hint, project_name in _WORKSPACE_HINTS.items():
            if hint in path_lower:
                return self.find_project(project_name)
        return None

    def query_by_integration(self, integration: str) -> List[ProjectProfile]:
        """Return projects that use a given integration."""
        integration_lower = integration.lower()
        results = []
        for p in self.list_projects():
            tags_str = " ".join(p.tags).lower()
            metadata_str = json.dumps(p.metadata).lower()
            models_str = " ".join(p.preferred_models).lower()
            if (
                integration_lower in tags_str
                or integration_lower in metadata_str
                or integration_lower in models_str
                or (integration_lower == "github" and p.github.enabled)
                or (integration_lower == "notion" and p.notion.enabled)
                or (integration_lower == "n8n" and p.n8n.enabled)
            ):
                results.append(p)
        return results

    def find_related_projects(self, project_id: str) -> List[ProjectProfile]:
        """Find projects sharing tags or preferred models."""
        source = self.get_project(project_id)
        if not source:
            return []
        source_tags = set(source.tags)
        source_models = set(source.preferred_models)
        results = []
        for p in self.list_projects():
            if p.project_id == project_id:
                continue
            shared_tags = source_tags & set(p.tags)
            shared_models = source_models & set(p.preferred_models)
            if shared_tags or shared_models:
                results.append(p)
        return results

    def get_projects_needing_attention(self) -> List[ProjectProfile]:
        """Return projects that haven't been active in 7+ days or are in planning/paused state."""
        threshold = time.time() - (7 * 24 * 3600)
        results = []
        for p in self.list_projects():
            if p.status in (ProjectStatus.PAUSED, ProjectStatus.PLANNING):
                results.append(p)
            elif p.last_active < threshold and p.status == ProjectStatus.ACTIVE:
                results.append(p)
        return results


class ProjectMemoryImpl(ProjectMemoryService):
    """SQLite-backed per-project memory store."""

    def __init__(self, db_path: Optional[str] = None) -> None:
        self._db_path = db_path or os.getenv("AIOS_PROJECTS_DB", _DEFAULT_DB)
        self._lock = Lock()
        self._conn: Optional[sqlite3.Connection] = None

    def initialize(self) -> None:
        self._conn = sqlite3.connect(self._db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._bootstrap_schema()

    def start(self) -> None:
        pass

    def shutdown(self) -> None:
        if self._conn:
            self._conn.close()
            self._conn = None

    def ready(self) -> bool:
        return self._conn is not None

    def _bootstrap_schema(self) -> None:
        assert self._conn is not None
        with self._conn:
            self._conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS project_memory (
                    entry_id    TEXT PRIMARY KEY,
                    project_id  TEXT NOT NULL,
                    category    TEXT NOT NULL,
                    title       TEXT NOT NULL,
                    content     TEXT NOT NULL DEFAULT '',
                    tags        TEXT NOT NULL DEFAULT '[]',
                    created_at  REAL NOT NULL,
                    updated_at  REAL NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_pmem_project ON project_memory(project_id);
                CREATE INDEX IF NOT EXISTS idx_pmem_category ON project_memory(category);
                """
            )

    @contextmanager
    def _tx(self) -> Generator[sqlite3.Connection, None, None]:
        assert self._conn is not None
        with self._lock:
            with self._conn:
                yield self._conn

    @staticmethod
    def _row_to_entry(row: sqlite3.Row) -> ProjectMemoryEntry:
        return ProjectMemoryEntry(
            entry_id=row["entry_id"],
            project_id=row["project_id"],
            category=row["category"],
            title=row["title"],
            content=row["content"],
            tags=json.loads(row["tags"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def store(self, entry: ProjectMemoryEntry) -> ProjectMemoryEntry:
        with self._tx() as conn:
            conn.execute(
                """
                INSERT INTO project_memory
                    (entry_id, project_id, category, title, content, tags, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(entry_id) DO UPDATE SET
                    title=excluded.title,
                    content=excluded.content,
                    tags=excluded.tags,
                    updated_at=excluded.updated_at
                """,
                (
                    entry.entry_id,
                    entry.project_id,
                    entry.category,
                    entry.title,
                    entry.content,
                    json.dumps(entry.tags),
                    entry.created_at,
                    entry.updated_at,
                ),
            )
        return entry

    def retrieve(
        self,
        project_id: str,
        category: Optional[str] = None,
        limit: int = 50,
    ) -> List[ProjectMemoryEntry]:
        assert self._conn is not None
        query = "SELECT * FROM project_memory WHERE project_id = ?"
        params: list = [project_id]
        if category:
            query += " AND category = ?"
            params.append(category)
        query += " ORDER BY updated_at DESC LIMIT ?"
        params.append(limit)
        with self._lock:
            rows = self._conn.execute(query, params).fetchall()
        return [self._row_to_entry(r) for r in rows]

    def search(self, project_id: str, query: str, limit: int = 20) -> List[ProjectMemoryEntry]:
        assert self._conn is not None
        with self._lock:
            rows = self._conn.execute(
                """
                SELECT * FROM project_memory
                WHERE project_id = ? AND (title LIKE ? OR content LIKE ?)
                ORDER BY updated_at DESC LIMIT ?
                """,
                (project_id, f"%{query}%", f"%{query}%", limit),
            ).fetchall()
        return [self._row_to_entry(r) for r in rows]

    def delete_entry(self, entry_id: str) -> bool:
        assert self._conn is not None
        with self._lock:
            row = self._conn.execute(
                "SELECT entry_id FROM project_memory WHERE entry_id = ?", (entry_id,)
            ).fetchone()
        if not row:
            return False
        with self._tx() as conn:
            conn.execute("DELETE FROM project_memory WHERE entry_id = ?", (entry_id,))
        return True

    def get_recent(self, project_id: str, limit: int = 10) -> List[ProjectMemoryEntry]:
        return self.retrieve(project_id, limit=limit)


class ProjectContextImpl(ProjectContextService):
    """SQLite-backed project context and context-switching service."""

    def __init__(
        self,
        registry: ProjectRegistryImpl,
        db_path: Optional[str] = None,
    ) -> None:
        self._registry = registry
        self._db_path = db_path or os.getenv("AIOS_PROJECTS_DB", _DEFAULT_DB)
        self._lock = Lock()
        self._conn: Optional[sqlite3.Connection] = None

    def initialize(self) -> None:
        self._conn = sqlite3.connect(self._db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._bootstrap_schema()

    def start(self) -> None:
        pass

    def shutdown(self) -> None:
        if self._conn:
            self._conn.close()
            self._conn = None

    def ready(self) -> bool:
        return self._conn is not None

    def _bootstrap_schema(self) -> None:
        assert self._conn is not None
        with self._conn:
            self._conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS project_contexts (
                    project_id  TEXT PRIMARY KEY,
                    data        TEXT NOT NULL DEFAULT '{}'
                );

                CREATE TABLE IF NOT EXISTS project_context_state (
                    key   TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );
                """
            )

    @contextmanager
    def _tx(self) -> Generator[sqlite3.Connection, None, None]:
        assert self._conn is not None
        with self._lock:
            with self._conn:
                yield self._conn

    def _build_context_from_profile(self, profile: ProjectProfile) -> ProjectRuntimeContext:
        """Assemble a default runtime context from a project profile."""
        return ProjectRuntimeContext(
            project_id=profile.project_id,
            project_name=profile.name,
            current_sprint=profile.current_sprint,
            current_phase=profile.current_phase,
            active_branch=profile.github.branch if profile.github.enabled else "main",
            active_models=list(profile.preferred_models),
            github_status={"enabled": profile.github.enabled, "repo": profile.github.repo},
            notion_status={"enabled": profile.notion.enabled},
            workflow_status={"enabled": profile.n8n.enabled},
            graph_entity_id=profile.knowledge_graph.entity_id,
        )

    def get_context(self, project_id: str) -> Optional[ProjectRuntimeContext]:
        assert self._conn is not None
        with self._lock:
            row = self._conn.execute(
                "SELECT data FROM project_contexts WHERE project_id = ?", (project_id,)
            ).fetchone()
        if row:
            return ProjectRuntimeContext.from_dict(json.loads(row["data"]))
        # Build fresh from profile
        profile = self._registry.get_project(project_id)
        if profile:
            ctx = self._build_context_from_profile(profile)
            self._persist_context(ctx)
            return ctx
        return None

    def _persist_context(self, ctx: ProjectRuntimeContext) -> None:
        with self._tx() as conn:
            conn.execute(
                """
                INSERT INTO project_contexts (project_id, data)
                VALUES (?, ?)
                ON CONFLICT(project_id) DO UPDATE SET data=excluded.data
                """,
                (ctx.project_id, json.dumps(ctx.to_dict())),
            )

    def update_context(self, project_id: str, updates: Dict[str, Any]) -> ProjectRuntimeContext:
        ctx = self.get_context(project_id)
        if not ctx:
            profile = self._registry.get_project(project_id)
            if profile:
                ctx = self._build_context_from_profile(profile)
            else:
                ctx = ProjectRuntimeContext(project_id=project_id, project_name=project_id)
        d = ctx.to_dict()
        d.update(updates)
        updated = ProjectRuntimeContext.from_dict(d)
        self._persist_context(updated)
        return updated

    def switch_to(self, project_id: str) -> ProjectRuntimeContext:
        """Load full project context and set it as active."""
        ctx = self.get_context(project_id)
        if not ctx:
            profile = self._registry.get_project(project_id)
            if not profile:
                raise ValueError(f"Project '{project_id}' not found in registry")
            ctx = self._build_context_from_profile(profile)

        ctx.last_switched = time.time()
        self._persist_context(ctx)
        self._registry.set_active_project(project_id)
        self._registry.update_project(project_id, {"last_active": time.time()})

        with self._tx() as conn:
            conn.execute(
                "INSERT INTO project_context_state (key, value) VALUES ('active_context', ?) "
                "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                (project_id,),
            )
        return ctx

    def get_active_context(self) -> Optional[ProjectRuntimeContext]:
        assert self._conn is not None
        with self._lock:
            row = self._conn.execute(
                "SELECT value FROM project_context_state WHERE key = 'active_context'"
            ).fetchone()
        if not row:
            # Default to AI OS
            profile = self._registry.find_project("AI OS")
            if profile:
                return self.get_context(profile.project_id)
            return None
        return self.get_context(row["value"])

    def get_dashboard_data(self, project_id: str) -> Dict[str, Any]:
        """Assemble full dashboard data for a project."""
        profile = self._registry.get_project(project_id)
        ctx = self.get_context(project_id)

        if not profile:
            return {"error": f"Project '{project_id}' not found"}

        ctx_dict = ctx.to_dict() if ctx else {}

        # Compute health score
        health_score = 100
        if profile.status == ProjectStatus.PAUSED:
            health_score = 60
        elif profile.status == ProjectStatus.PLANNING:
            health_score = 40

        stale_days = int((time.time() - profile.last_active) / 86400)
        if stale_days > 7:
            health_score = max(health_score - 20, 10)

        return {
            "project": profile.to_dict(),
            "context": ctx_dict,
            "health_score": health_score,
            "stale_days": stale_days,
            "integrations": {
                "github": {
                    "enabled": profile.github.enabled,
                    "repo": profile.github.repo,
                    "branch": profile.github.branch,
                    "status": ctx_dict.get("github_status", {}),
                },
                "notion": {
                    "enabled": profile.notion.enabled,
                    "status": ctx_dict.get("notion_status", {}),
                },
                "n8n": {
                    "enabled": profile.n8n.enabled,
                    "workflow_ids": profile.n8n.workflow_ids,
                    "status": ctx_dict.get("workflow_status", {}),
                },
            },
            "preferred_models": profile.preferred_models,
            "open_tasks": ctx_dict.get("open_tasks", []),
            "goals": ctx_dict.get("goals", []),
            "recent_activity": ctx_dict.get("recent_activity", []),
            "graph_entity_id": ctx_dict.get("graph_entity_id", ""),
        }
