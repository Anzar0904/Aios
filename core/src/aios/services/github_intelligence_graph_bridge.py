"""Phase 9: GitHub Intelligence — Knowledge Graph Bridge.

Bridges git repositories, branches, commits, pull requests, and issues into the Universal Knowledge Graph
using CONTAINS, REFERENCES, and MERGES edges.
"""

from __future__ import annotations

import logging

from aios.services.github_intelligence import (
    GitBranch,
    GitIssue,
    GitPullRequest,
    GitRepository,
)
from aios.services.graph import EntityType, RelationshipType
from aios.services.graph_query import GraphQueryEngine

logger = logging.getLogger(__name__)


class GitHubIntelligenceGraphBridge:
    """Synchronizes GitHub repository intelligence elements and activity logs to the Knowledge Graph."""

    def __init__(self, graph_engine: GraphQueryEngine) -> None:
        self._engine = graph_engine

    def sync_repository(self, repo: GitRepository) -> str:
        """Create or update a REPOSITORY node in the graph."""
        try:
            props = {
                "owner": repo.owner,
                "language": repo.language,
                "health_score": repo.health_score,
            }
            entity = self._engine.ensure_entity(EntityType.REPOSITORY, repo.name, props)
            return entity.entity_id
        except Exception as exc:
            logger.warning("Failed to sync repository to graph: %s", exc)
            return ""

    def sync_branch(self, branch: GitBranch, repo_name: str) -> str:
        """Create or update a BRANCH node and establish CONTAINS relationship from Repo."""
        try:
            props = {
                "author": branch.author,
                "status": branch.status,
            }
            entity = self._engine.ensure_entity(
                EntityType.BRANCH, f"{repo_name} @ {branch.name}", props
            )

            repo_entity = self._engine.ensure_entity(EntityType.REPOSITORY, repo_name)
            self._engine.ensure_relationship(
                repo_entity.entity_id, entity.entity_id, RelationshipType.CONTAINS
            )
            return entity.entity_id
        except Exception as exc:
            logger.warning("Failed to sync branch to graph: %s", exc)
            return ""

    def sync_pull_request(self, pr: GitPullRequest, repo_name: str) -> str:
        """Create or update a PULL_REQUEST node and link it via REFERENCES."""
        try:
            props = {
                "pr_number": pr.pr_number,
                "author": pr.author,
                "status": pr.status,
                "risk_score": pr.risk_score,
            }
            entity = self._engine.ensure_entity(
                EntityType.PULL_REQUEST, f"PR #{pr.pr_number}: {pr.title}", props
            )

            repo_entity = self._engine.ensure_entity(EntityType.REPOSITORY, repo_name)
            self._engine.ensure_relationship(
                repo_entity.entity_id, entity.entity_id, RelationshipType.REFERENCES
            )
            return entity.entity_id
        except Exception as exc:
            logger.warning("Failed to sync PR to graph: %s", exc)
            return ""

    def sync_issue(self, issue: GitIssue, repo_name: str) -> str:
        """Create or update an ISSUE node in the graph."""
        try:
            props = {
                "priority": issue.priority,
                "status": issue.status,
            }
            entity = self._engine.ensure_entity(EntityType.ISSUE, f"Issue: {issue.title}", props)

            repo_entity = self._engine.ensure_entity(EntityType.REPOSITORY, repo_name)
            self._engine.ensure_relationship(
                repo_entity.entity_id, entity.entity_id, RelationshipType.REFERENCES
            )
            return entity.entity_id
        except Exception as exc:
            logger.warning("Failed to sync issue to graph: %s", exc)
            return ""
