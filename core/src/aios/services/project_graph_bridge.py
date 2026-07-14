"""Phase 5: Project Intelligence — Graph Integration for Projects.

Bridges the Project Registry with the Universal Knowledge Graph (Phase 4.5).
Automatically creates graph entities for projects, links tasks, documents,
workflows, and decisions to the correct project graph node.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from aios.services.graph import EntityType
from aios.services.graph_query import GraphQueryEngine
from aios.services.project_registry import ProjectProfile

logger = logging.getLogger(__name__)


class ProjectGraphBridge:
    """Bridges project registry events into the Knowledge Graph."""

    def __init__(self, graph_engine: GraphQueryEngine) -> None:
        self._engine = graph_engine

    # ── Project lifecycle ─────────────────────────────────────────────────────

    def register_project_in_graph(self, profile: ProjectProfile) -> str:
        """Ensure the project has a graph entity; return its entity_id."""
        try:
            props = {
                "project_type": profile.project_type.value,
                "status": profile.status.value,
                "priority": profile.priority.value,
                "owner": profile.owner,
                "preferred_models": profile.preferred_models,
                "tags": profile.tags,
                "github_repo": profile.github.repo,
                "current_sprint": profile.current_sprint,
                "current_phase": profile.current_phase,
            }
            entity = self._engine.ensure_entity(EntityType.PROJECT, profile.name, props)
            return entity.entity_id
        except Exception as exc:
            logger.warning("Failed to register project in graph: %s", exc)
            return ""

    def link_repository_to_project(self, repo_name: str, project_name: str) -> None:
        """Create a BELONGS_TO edge from repository to project."""
        try:
            self._engine.link_repository_to_project(repo_name, project_name)
        except Exception as exc:
            logger.warning("Failed to link repo to project in graph: %s", exc)

    def link_task_to_project(self, task_name: str, project_name: str) -> None:
        try:
            self._engine.link_task_to_project(task_name, project_name)
        except Exception as exc:
            logger.warning("Failed to link task in graph: %s", exc)

    def link_document_to_project(self, doc_name: str, project_name: str) -> None:
        try:
            self._engine.link_document_to_project(doc_name, project_name)
        except Exception as exc:
            logger.warning("Failed to link document in graph: %s", exc)

    def link_decision_to_project(self, decision_name: str, project_name: str) -> None:
        try:
            self._engine.link_decision_to_project(decision_name, project_name)
        except Exception as exc:
            logger.warning("Failed to link decision in graph: %s", exc)

    def link_workflow_to_project(self, workflow_name: str, project_name: str) -> None:
        try:
            self._engine.link_workflow_to_project(workflow_name, project_name)
        except Exception as exc:
            logger.warning("Failed to link workflow in graph: %s", exc)

    # ── Cross-project queries ─────────────────────────────────────────────────

    def get_project_graph_summary(self, project_name: str) -> Dict[str, Any]:
        """Return graph summary (subgraph) for a project."""
        try:
            return self._engine.get_project_overview(project_name)
        except Exception as exc:
            logger.warning("Failed to get project graph summary: %s", exc)
            return {"error": str(exc)}

    def find_shared_resources(
        self,
        project_names: List[str],
    ) -> Dict[str, Any]:
        """Identify graph nodes referenced by multiple projects."""
        try:
            shared: Dict[str, List[str]] = {}
            for pname in project_names:
                result = self._engine.get_project_overview(pname)
                if "error" in result:
                    continue
                sub = result.get("subgraph", {})
                for etype, entities in sub.items():
                    if isinstance(entities, list):
                        for e in entities:
                            eid = e.get("entity_id", "")
                            if eid:
                                shared.setdefault(eid, [])
                                if pname not in shared[eid]:
                                    shared[eid].append(pname)

            # Return only nodes shared by 2+ projects
            return {
                "shared_nodes": [
                    {"entity_id": eid, "projects": projs}
                    for eid, projs in shared.items()
                    if len(projs) >= 2
                ]
            }
        except Exception as exc:
            logger.warning("Failed to find shared resources: %s", exc)
            return {"shared_nodes": []}


class ProjectModelRouter:
    """Routes model selection to project-preferred models."""

    # Default fallbacks when no project is active or project has no models
    _GLOBAL_DEFAULTS = ["deepseek-r1", "qwen2.5-coder", "gemma3:4b"]

    def __init__(self, registry: Any) -> None:
        self._registry = registry

    def get_preferred_models(self, project_name: Optional[str] = None) -> List[str]:
        """Return the preferred model list for a project (or global defaults)."""
        try:
            if project_name:
                profile = self._registry.find_project(project_name)
                if profile and profile.preferred_models:
                    return profile.preferred_models
            # Fall back to active project
            active = self._registry.get_active_project()
            if active and active.preferred_models:
                return active.preferred_models
        except Exception as exc:
            logger.warning("ModelRouter: failed to resolve project models: %s", exc)
        return self._GLOBAL_DEFAULTS

    def get_primary_model(self, project_name: Optional[str] = None) -> str:
        """Return the single best model for the current project."""
        models = self.get_preferred_models(project_name)
        return models[0] if models else "deepseek-r1"

    def get_model_profile(self, project_name: Optional[str] = None) -> Dict[str, Any]:
        """Return the full model profile for a project."""
        try:
            if project_name:
                profile = self._registry.find_project(project_name)
                if profile:
                    return {
                        "project": profile.name,
                        "preferred_models": profile.preferred_models,
                        "primary_model": profile.preferred_models[0]
                        if profile.preferred_models
                        else "deepseek-r1",
                        "project_type": profile.project_type.value,
                    }
        except Exception:
            pass
        return {
            "project": "global",
            "preferred_models": self._GLOBAL_DEFAULTS,
            "primary_model": self._GLOBAL_DEFAULTS[0],
            "project_type": "unknown",
        }
