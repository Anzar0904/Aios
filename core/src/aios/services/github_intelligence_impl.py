"""Phase 9: GitHub Intelligence — Service Implementations.

Provides database implementations for Repository registries, branches, commit histories,
PR risk score calculations, issues priorities, workflow builds, and repository health calculations.
"""

from __future__ import annotations

import json
import logging
import os
import sqlite3
from contextlib import contextmanager
from threading import Lock
from typing import Generator, List, Optional

from aios.services.github_intelligence import (
    GitActionWorkflow,
    GitBranch,
    GitCommit,
    GitHubIntelligenceService,
    GitIssue,
    GitPullRequest,
    GitRelease,
    GitRepository,
    new_id,
)

logger = logging.getLogger(__name__)

_DEFAULT_DB = os.path.join(os.path.expanduser("~"), ".aios_github_intel.db")


class GitHubIntelligenceServiceImpl(GitHubIntelligenceService):
    """SQLite-backed GitHub Intelligence Engine managing repositories analytics and health indices."""

    def __init__(self, db_path: Optional[str] = None) -> None:
        self._db_path = db_path or os.getenv("AIOS_GITHUB_DB", _DEFAULT_DB)
        self._lock = Lock()
        self._conn: Optional[sqlite3.Connection] = None

    def initialize(self) -> None:
        self._conn = sqlite3.connect(self._db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._bootstrap_schema()
        self._seed_default_repositories()
        logger.info("GitHub Intelligence Service initialized at: %s", self._db_path)

    def start(self) -> None:
        pass

    def shutdown(self) -> None:
        if self._conn:
            self._conn.close()
            self._conn = None

    def _bootstrap_schema(self) -> None:
        assert self._conn is not None
        with self._conn:
            self._conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS repositories (
                    repository_id   TEXT PRIMARY KEY,
                    name            TEXT NOT NULL UNIQUE,
                    owner           TEXT NOT NULL,
                    description     TEXT NOT NULL DEFAULT '',
                    visibility      TEXT NOT NULL DEFAULT 'public',
                    default_branch  TEXT NOT NULL DEFAULT 'main',
                    language        TEXT NOT NULL DEFAULT 'python',
                    stars           INTEGER NOT NULL DEFAULT 0,
                    forks           INTEGER NOT NULL DEFAULT 0,
                    open_issues     INTEGER NOT NULL DEFAULT 0,
                    open_prs        INTEGER NOT NULL DEFAULT 0,
                    created_at      REAL NOT NULL,
                    updated_at      REAL NOT NULL,
                    health_score    INTEGER NOT NULL DEFAULT 100
                );

                CREATE TABLE IF NOT EXISTS branches (
                    branch_id       TEXT PRIMARY KEY,
                    repository_id   TEXT NOT NULL,
                    name            TEXT NOT NULL,
                    parent_branch   TEXT NOT NULL DEFAULT 'main',
                    commit_sha      TEXT NOT NULL DEFAULT '',
                    author          TEXT NOT NULL DEFAULT '',
                    status          TEXT NOT NULL DEFAULT 'active',
                    merge_state     TEXT NOT NULL DEFAULT 'clean',
                    health_score    INTEGER NOT NULL DEFAULT 100,
                    UNIQUE(repository_id, name)
                );

                CREATE TABLE IF NOT EXISTS commits (
                    commit_sha      TEXT PRIMARY KEY,
                    repository_id   TEXT NOT NULL,
                    author          TEXT NOT NULL,
                    message         TEXT NOT NULL,
                    files_changed   INTEGER NOT NULL DEFAULT 0,
                    lines_added     INTEGER NOT NULL DEFAULT 0,
                    lines_removed   INTEGER NOT NULL DEFAULT 0,
                    timestamp       REAL NOT NULL
                );

                CREATE TABLE IF NOT EXISTS pull_requests (
                    pr_id           TEXT PRIMARY KEY,
                    pr_number       INTEGER NOT NULL,
                    repository_id   TEXT NOT NULL,
                    title           TEXT NOT NULL,
                    author          TEXT NOT NULL,
                    status          TEXT NOT NULL DEFAULT 'open',
                    files_changed   INTEGER NOT NULL DEFAULT 0,
                    risk_score      INTEGER NOT NULL DEFAULT 10,
                    review_state    TEXT NOT NULL DEFAULT 'pending',
                    created_at      REAL NOT NULL,
                    UNIQUE(repository_id, pr_number)
                );

                CREATE TABLE IF NOT EXISTS issues (
                    issue_id        TEXT PRIMARY KEY,
                    repository_id   TEXT NOT NULL,
                    title           TEXT NOT NULL,
                    priority        INTEGER NOT NULL DEFAULT 1,
                    status          TEXT NOT NULL DEFAULT 'open',
                    assignee        TEXT NOT NULL DEFAULT '',
                    labels          TEXT NOT NULL DEFAULT '[]',
                    created_at      REAL NOT NULL
                );

                CREATE TABLE IF NOT EXISTS action_workflows (
                    workflow_id     TEXT PRIMARY KEY,
                    repository_id   TEXT NOT NULL,
                    name            TEXT NOT NULL,
                    status          TEXT NOT NULL DEFAULT 'success',
                    duration_secs   INTEGER NOT NULL DEFAULT 0,
                    timestamp       REAL NOT NULL
                );

                CREATE TABLE IF NOT EXISTS releases (
                    release_id      TEXT PRIMARY KEY,
                    repository_id   TEXT NOT NULL,
                    version         TEXT NOT NULL UNIQUE,
                    title           TEXT NOT NULL,
                    features        TEXT NOT NULL DEFAULT '[]',
                    fixes           TEXT NOT NULL DEFAULT '[]',
                    timestamp       REAL NOT NULL
                );
                """
            )

    def _seed_default_repositories(self) -> None:
        """Seed default active repositories."""
        assert self._conn is not None
        with self._lock:
            count = self._conn.execute("SELECT count(*) FROM repositories").fetchone()[0]
        if count > 0:
            return

        rid = new_id()
        repo = GitRepository(
            repository_id=rid,
            name="Anzar0904/Aios",
            owner="Anzar0904",
            description="The core Operating System engine of AI OS.",
            visibility="public",
            language="python",
            stars=142,
            forks=28,
            open_issues=2,
            open_prs=1,
        )
        self.register_repository(repo)

        # Seed child branches
        self.record_branch(
            GitBranch(
                branch_id=new_id(),
                repository_id=rid,
                name="main",
                author="Anzar0904",
                status="active",
            )
        )
        self.record_branch(
            GitBranch(
                branch_id=new_id(),
                repository_id=rid,
                name="feat/docs-intel",
                parent_branch="main",
                author="Anzar0904",
                status="active",
            )
        )

        # Seed sample issues and PRs
        self.record_issue(
            GitIssue(
                issue_id=new_id(),
                repository_id=rid,
                title="Documentation Sync latency issue",
                priority=3,
                status="open",
                assignee="Anzar0904",
                labels=["bug", "docs"],
            )
        )
        self.record_pull_request(
            GitPullRequest(
                pr_id=new_id(),
                pr_number=14,
                repository_id=rid,
                title="feat: Phase 8 Documentation Intelligence",
                author="Anzar0904",
                status="open",
                files_changed=15,
                risk_score=20,
            )
        )

    @contextmanager
    def _tx(self) -> Generator[sqlite3.Connection, None, None]:
        assert self._conn is not None
        with self._lock:
            with self._conn:
                yield self._conn

    # ── Repository Config CRUD ───────────────────────────────────────────────

    def register_repository(self, repo: GitRepository) -> GitRepository:
        with self._tx() as conn:
            conn.execute(
                """
                INSERT INTO repositories (
                    repository_id, name, owner, description, visibility, default_branch,
                    language, stars, forks, open_issues, open_prs, created_at, updated_at, health_score
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(repository_id) DO UPDATE SET
                    name=excluded.name, description=excluded.description, visibility=excluded.visibility,
                    stars=excluded.stars, forks=excluded.forks, open_issues=excluded.open_issues,
                    open_prs=excluded.open_prs, updated_at=excluded.updated_at, health_score=excluded.health_score
                """,
                (
                    repo.repository_id,
                    repo.name,
                    repo.owner,
                    repo.description,
                    repo.visibility,
                    repo.default_branch,
                    repo.language,
                    repo.stars,
                    repo.forks,
                    repo.open_issues,
                    repo.open_prs,
                    repo.created_at,
                    repo.updated_at,
                    repo.health_score,
                ),
            )
        return repo

    def get_repository(self, repository_id: str) -> Optional[GitRepository]:
        assert self._conn is not None
        with self._lock:
            row = self._conn.execute(
                "SELECT * FROM repositories WHERE repository_id = ?", (repository_id,)
            ).fetchone()
        return GitRepository.from_dict(dict(row)) if row else None

    def get_repository_by_name(self, name: str) -> Optional[GitRepository]:
        assert self._conn is not None
        with self._lock:
            row = self._conn.execute(
                "SELECT * FROM repositories WHERE name = ?", (name,)
            ).fetchone()
        return GitRepository.from_dict(dict(row)) if row else None

    def list_repositories(self) -> List[GitRepository]:
        assert self._conn is not None
        with self._lock:
            rows = self._conn.execute("SELECT * FROM repositories").fetchall()
        return [GitRepository.from_dict(dict(r)) for r in rows]

    # ── Pull Requests & Issues ───────────────────────────────────────────────

    def record_pull_request(self, pr: GitPullRequest) -> GitPullRequest:
        with self._tx() as conn:
            conn.execute(
                """
                INSERT INTO pull_requests (pr_id, pr_number, repository_id, title, author, status, files_changed, risk_score, review_state, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(repository_id, pr_number) DO UPDATE SET
                    title=excluded.title, status=excluded.status, files_changed=excluded.files_changed,
                    risk_score=excluded.risk_score, review_state=excluded.review_state
                """,
                (
                    pr.pr_id,
                    pr.pr_number,
                    pr.repository_id,
                    pr.title,
                    pr.author,
                    pr.status,
                    pr.files_changed,
                    pr.risk_score,
                    pr.review_state,
                    pr.created_at,
                ),
            )
        return pr

    def list_pull_requests(self, repository_id: str) -> List[GitPullRequest]:
        assert self._conn is not None
        with self._lock:
            rows = self._conn.execute(
                "SELECT * FROM pull_requests WHERE repository_id = ?", (repository_id,)
            ).fetchall()
        return [GitPullRequest.from_dict(dict(r)) for r in rows]

    def record_issue(self, issue: GitIssue) -> GitIssue:
        with self._tx() as conn:
            conn.execute(
                """
                INSERT INTO issues (issue_id, repository_id, title, priority, status, assignee, labels, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(issue_id) DO UPDATE SET
                    title=excluded.title, priority=excluded.priority, status=excluded.status,
                    assignee=excluded.assignee, labels=excluded.labels
                """,
                (
                    issue.issue_id,
                    issue.repository_id,
                    issue.title,
                    issue.priority,
                    issue.status,
                    issue.assignee,
                    json.dumps(issue.labels),
                    issue.created_at,
                ),
            )
        return issue

    def list_issues(self, repository_id: str) -> List[GitIssue]:
        assert self._conn is not None
        with self._lock:
            rows = self._conn.execute(
                "SELECT * FROM issues WHERE repository_id = ?", (repository_id,)
            ).fetchall()
        return [GitIssue.from_dict(dict(r)) for r in rows]

    # ── Commits & Branches ────────────────────────────────────────────────────

    def record_commit(self, commit: GitCommit) -> GitCommit:
        with self._tx() as conn:
            conn.execute(
                """
                INSERT INTO commits (commit_sha, repository_id, author, message, files_changed, lines_added, lines_removed, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(commit_sha) DO NOTHING
                """,
                (
                    commit.commit_sha,
                    commit.repository_id,
                    commit.author,
                    commit.message,
                    commit.files_changed,
                    commit.lines_added,
                    commit.lines_removed,
                    commit.timestamp,
                ),
            )
        return commit

    def list_commits(self, repository_id: str) -> List[GitCommit]:
        assert self._conn is not None
        with self._lock:
            rows = self._conn.execute(
                "SELECT * FROM commits WHERE repository_id = ? ORDER BY timestamp DESC",
                (repository_id,),
            ).fetchall()
        return [GitCommit.from_dict(dict(r)) for r in rows]

    def record_branch(self, branch: GitBranch) -> GitBranch:
        with self._tx() as conn:
            conn.execute(
                """
                INSERT INTO branches (branch_id, repository_id, name, parent_branch, commit_sha, author, status, merge_state, health_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(repository_id, name) DO UPDATE SET
                    commit_sha=excluded.commit_sha, status=excluded.status, merge_state=excluded.merge_state,
                    health_score=excluded.health_score
                """,
                (
                    branch.branch_id,
                    branch.repository_id,
                    branch.name,
                    branch.parent_branch,
                    branch.commit_sha,
                    branch.author,
                    branch.status,
                    branch.merge_state,
                    branch.health_score,
                ),
            )
        return branch

    def list_branches(self, repository_id: str) -> List[GitBranch]:
        assert self._conn is not None
        with self._lock:
            rows = self._conn.execute(
                "SELECT * FROM branches WHERE repository_id = ?", (repository_id,)
            ).fetchall()
        return [GitBranch.from_dict(dict(r)) for r in rows]

    # ── Actions Workflows & Releases ──────────────────────────────────────────

    def record_workflow_run(self, run: GitActionWorkflow) -> GitActionWorkflow:
        with self._tx() as conn:
            conn.execute(
                """
                INSERT INTO action_workflows (workflow_id, repository_id, name, status, duration_secs, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(workflow_id) DO UPDATE SET
                    status=excluded.status, duration_secs=excluded.duration_secs
                """,
                (
                    run.workflow_id,
                    run.repository_id,
                    run.name,
                    run.status,
                    run.duration_secs,
                    run.timestamp,
                ),
            )
        return run

    def list_workflow_runs(self, repository_id: str) -> List[GitActionWorkflow]:
        assert self._conn is not None
        with self._lock:
            rows = self._conn.execute(
                "SELECT * FROM action_workflows WHERE repository_id = ? ORDER BY timestamp DESC",
                (repository_id,),
            ).fetchall()
        return [GitActionWorkflow.from_dict(dict(r)) for r in rows]

    def record_release(self, release: GitRelease) -> GitRelease:
        with self._tx() as conn:
            conn.execute(
                """
                INSERT INTO releases (release_id, repository_id, version, title, features, fixes, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(version) DO UPDATE SET
                    title=excluded.title, features=excluded.features, fixes=excluded.fixes
                """,
                (
                    release.release_id,
                    release.repository_id,
                    release.version,
                    release.title,
                    json.dumps(release.features),
                    json.dumps(release.fixes),
                    release.timestamp,
                ),
            )
        return release

    def list_releases(self, repository_id: str) -> List[GitRelease]:
        assert self._conn is not None
        with self._lock:
            rows = self._conn.execute(
                "SELECT * FROM releases WHERE repository_id = ? ORDER BY timestamp DESC",
                (repository_id,),
            ).fetchall()
        return [GitRelease.from_dict(dict(r)) for r in rows]

    # ── Repository Health Calculations ────────────────────────────────────────

    def calculate_repository_health(self, repository_id: str) -> int:
        """Calculate overall health from open issues, CI failures, and PR counts."""
        repo = self.get_repository(repository_id)
        if not repo:
            return 100

        score = 100

        # 1. Open Issues penalty (5 points each)
        issues = self.list_issues(repository_id)
        open_issues = sum(1 for i in issues if i.status == "open")
        score -= open_issues * 5

        # 2. CI failures penalty (15 points each failed workflow run)
        runs = self.list_workflow_runs(repository_id)
        failed_runs = sum(1 for r in runs if r.status == "failed")
        score -= failed_runs * 15

        # 3. PR risk score penalty (PR risk deduct)
        prs = self.list_pull_requests(repository_id)
        open_prs = [p for p in prs if p.status == "open"]
        if open_prs:
            avg_risk = sum(p.risk_score for p in open_prs) / len(open_prs)
            score -= int(avg_risk * 0.5)

        # Bound health score between 0 and 100
        final_score = max(0, min(100, score))

        # Save health back to repository
        repo.health_score = final_score
        self.register_repository(repo)

        return final_score
