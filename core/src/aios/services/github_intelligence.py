"""Phase 9: GitHub Intelligence — Interfaces and Dataclasses.

Defines the Repository registry, branches, commits, pull requests, issues,
actions workflows, and releases intelligence models.
"""

from __future__ import annotations

import abc
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from aios.services.base import ServiceLifecycle

# ---------------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------------


@dataclass
class GitRepository:
    repository_id: str
    name: str
    owner: str
    description: str = ""
    visibility: str = "public"
    default_branch: str = "main"
    language: str = "python"
    stars: int = 0
    forks: int = 0
    open_issues: int = 0
    open_prs: int = 0
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    health_score: int = 100

    def to_dict(self) -> Dict[str, Any]:
        return {
            "repository_id": self.repository_id,
            "name": self.name,
            "owner": self.owner,
            "description": self.description,
            "visibility": self.visibility,
            "default_branch": self.default_branch,
            "language": self.language,
            "stars": self.stars,
            "forks": self.forks,
            "open_issues": self.open_issues,
            "open_prs": self.open_prs,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "health_score": self.health_score,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> GitRepository:
        return cls(
            repository_id=data["repository_id"],
            name=data["name"],
            owner=data["owner"],
            description=data.get("description", ""),
            visibility=data.get("visibility", "public"),
            default_branch=data.get("default_branch", "main"),
            language=data.get("language", "python"),
            stars=data.get("stars", 0),
            forks=data.get("forks", 0),
            open_issues=data.get("open_issues", 0),
            open_prs=data.get("open_prs", 0),
            created_at=data.get("created_at", time.time()),
            updated_at=data.get("updated_at", time.time()),
            health_score=data.get("health_score", 100),
        )


@dataclass
class GitBranch:
    branch_id: str
    repository_id: str
    name: str
    parent_branch: str = "main"
    commit_sha: str = ""
    author: str = ""
    status: str = "active"
    merge_state: str = "clean"
    health_score: int = 100

    def to_dict(self) -> Dict[str, Any]:
        return {
            "branch_id": self.branch_id,
            "repository_id": self.repository_id,
            "name": self.name,
            "parent_branch": self.parent_branch,
            "commit_sha": self.commit_sha,
            "author": self.author,
            "status": self.status,
            "merge_state": self.merge_state,
            "health_score": self.health_score,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> GitBranch:
        return cls(
            branch_id=data["branch_id"],
            repository_id=data["repository_id"],
            name=data["name"],
            parent_branch=data.get("parent_branch", "main"),
            commit_sha=data.get("commit_sha", ""),
            author=data.get("author", ""),
            status=data.get("status", "active"),
            merge_state=data.get("merge_state", "clean"),
            health_score=data.get("health_score", 100),
        )


@dataclass
class GitCommit:
    commit_sha: str
    repository_id: str
    author: str
    message: str
    files_changed: int = 0
    lines_added: int = 0
    lines_removed: int = 0
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "commit_sha": self.commit_sha,
            "repository_id": self.repository_id,
            "author": self.author,
            "message": self.message,
            "files_changed": self.files_changed,
            "lines_added": self.lines_added,
            "lines_removed": self.lines_removed,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> GitCommit:
        return cls(
            commit_sha=data["commit_sha"],
            repository_id=data["repository_id"],
            author=data["author"],
            message=data["message"],
            files_changed=data.get("files_changed", 0),
            lines_added=data.get("lines_added", 0),
            lines_removed=data.get("lines_removed", 0),
            timestamp=data.get("timestamp", time.time()),
        )


@dataclass
class GitPullRequest:
    pr_id: str
    pr_number: int
    repository_id: str
    title: str
    author: str
    status: str = "open"  # open|closed|merged
    files_changed: int = 0
    risk_score: int = 10
    review_state: str = "pending"  # approved|changes_requested|pending
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pr_id": self.pr_id,
            "pr_number": self.pr_number,
            "repository_id": self.repository_id,
            "title": self.title,
            "author": self.author,
            "status": self.status,
            "files_changed": self.files_changed,
            "risk_score": self.risk_score,
            "review_state": self.review_state,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> GitPullRequest:
        return cls(
            pr_id=data["pr_id"],
            pr_number=data["pr_number"],
            repository_id=data["repository_id"],
            title=data["title"],
            author=data["author"],
            status=data.get("status", "open"),
            files_changed=data.get("files_changed", 0),
            risk_score=data.get("risk_score", 10),
            review_state=data.get("review_state", "pending"),
            created_at=data.get("created_at", time.time()),
        )


@dataclass
class GitIssue:
    issue_id: str
    repository_id: str
    title: str
    priority: int = 1  # 1-5 scale (5 highest)
    status: str = "open"  # open|closed
    assignee: str = ""
    labels: List[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "issue_id": self.issue_id,
            "repository_id": self.repository_id,
            "title": self.title,
            "priority": self.priority,
            "status": self.status,
            "assignee": self.assignee,
            "labels": self.labels,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> GitIssue:
        import json as _json

        labels = data.get("labels", [])
        if isinstance(labels, str):
            try:
                labels = _json.loads(labels)
            except Exception:
                labels = []

        return cls(
            issue_id=data["issue_id"],
            repository_id=data["repository_id"],
            title=data["title"],
            priority=data.get("priority", 1),
            status=data.get("status", "open"),
            assignee=data.get("assignee", ""),
            labels=labels,
            created_at=data.get("created_at", time.time()),
        )


@dataclass
class GitActionWorkflow:
    workflow_id: str
    repository_id: str
    name: str
    status: str = "success"  # success|failed|running
    duration_secs: int = 0
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "workflow_id": self.workflow_id,
            "repository_id": self.repository_id,
            "name": self.name,
            "status": self.status,
            "duration_secs": self.duration_secs,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> GitActionWorkflow:
        return cls(
            workflow_id=data["workflow_id"],
            repository_id=data["repository_id"],
            name=data["name"],
            status=data.get("status", "success"),
            duration_secs=data.get("duration_secs", 0),
            timestamp=data.get("timestamp", time.time()),
        )


@dataclass
class GitRelease:
    release_id: str
    repository_id: str
    version: str
    title: str
    features: List[str] = field(default_factory=list)
    fixes: List[str] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "release_id": self.release_id,
            "repository_id": self.repository_id,
            "version": self.version,
            "title": self.title,
            "features": self.features,
            "fixes": self.fixes,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> GitRelease:
        import json as _json

        features = data.get("features", [])
        if isinstance(features, str):
            try:
                features = _json.loads(features)
            except Exception:
                features = []

        fixes = data.get("fixes", [])
        if isinstance(fixes, str):
            try:
                fixes = _json.loads(fixes)
            except Exception:
                fixes = []

        return cls(
            release_id=data["release_id"],
            repository_id=data["repository_id"],
            version=data["version"],
            title=data["title"],
            features=features,
            fixes=fixes,
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


class GitHubIntelligenceService(ServiceLifecycle, abc.ABC):
    """Monitors repository codes, pull requests review metrics, action builds, and releases."""

    @abc.abstractmethod
    def register_repository(self, repo: GitRepository) -> GitRepository:
        """Register a repository profile."""

    @abc.abstractmethod
    def get_repository(self, repository_id: str) -> Optional[GitRepository]:
        """Fetch repository profile."""

    @abc.abstractmethod
    def list_repositories(self) -> List[GitRepository]:
        """List registered repositories."""

    # ── PR Analyzer & Issues ──────────────────────────────────────────────────
    @abc.abstractmethod
    def record_pull_request(self, pr: GitPullRequest) -> GitPullRequest:
        """Log pull request update."""

    @abc.abstractmethod
    def list_pull_requests(self, repository_id: str) -> List[GitPullRequest]:
        """List repository PRs."""

    @abc.abstractmethod
    def record_issue(self, issue: GitIssue) -> GitIssue:
        """Log issue choice update."""

    @abc.abstractmethod
    def list_issues(self, repository_id: str) -> List[GitIssue]:
        """List repository issues."""

    # ── Commits & Branches ────────────────────────────────────────────────────
    @abc.abstractmethod
    def record_commit(self, commit: GitCommit) -> GitCommit:
        """Log commit details."""

    @abc.abstractmethod
    def record_branch(self, branch: GitBranch) -> GitBranch:
        """Log branch choice update."""

    # ── Actions Workflows & Releases ──────────────────────────────────────────
    @abc.abstractmethod
    def record_workflow_run(self, run: GitActionWorkflow) -> GitActionWorkflow:
        """Log CI actions workflow run status."""

    @abc.abstractmethod
    def record_release(self, release: GitRelease) -> GitRelease:
        """Log release version change."""

    # ── Repository Health Calculations ────────────────────────────────────────
    @abc.abstractmethod
    def calculate_repository_health(self, repository_id: str) -> int:
        """Calculate overall repository health based on code, docs, tests, and open issues."""
