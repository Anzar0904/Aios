"""Graph Integration Hooks (Phase 4.5).

Provides lightweight hooks that auto-create graph relationships whenever
domain events occur (task created, project created, document saved, etc.).
Integrates with Memory, Task, Goal, Context, and Notification services.
"""

import logging
from typing import Any, Dict, Optional

from aios.services.graph import (
    EntityType,
    GraphService,
    RelationshipType,
)
from aios.services.graph_query import GraphQueryEngine

logger = logging.getLogger(__name__)


class GraphIntegrationHooks:
    """Auto-creates graph nodes/edges when domain events fire.

    Designed for use in service implementations — call the appropriate
    on_* method whenever a domain object is created/updated/deployed.
    """

    def __init__(self, graph: GraphService) -> None:
        self._graph = graph
        self._engine = GraphQueryEngine(graph)

    # ------------------------------------------------------------------
    # Task Engine integration
    # ------------------------------------------------------------------

    def on_task_created(
        self,
        task_id: str,
        task_title: str,
        project_name: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Auto-register a new task in the knowledge graph."""
        try:
            props = {"task_id": task_id, **(properties or {})}
            self._engine.ensure_entity(EntityType.TASK, task_title, props)

            if project_name:
                self._engine.link_task_to_project(task_title, project_name)
                logger.debug("Graph: task '%s' linked to project '%s'", task_title, project_name)
            else:
                logger.debug("Graph: task '%s' registered (no project)", task_title)
        except Exception as exc:
            logger.warning("Graph hook on_task_created failed: %s", exc)

    # ------------------------------------------------------------------
    # Project Engine integration
    # ------------------------------------------------------------------

    def on_project_created(
        self,
        project_name: str,
        repository_name: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Auto-register a new project in the knowledge graph."""
        try:
            self._engine.ensure_entity(EntityType.PROJECT, project_name, properties)
            if repository_name:
                self._engine.link_repository_to_project(repository_name, project_name)
            logger.debug("Graph: project '%s' registered", project_name)
        except Exception as exc:
            logger.warning("Graph hook on_project_created failed: %s", exc)

    # ------------------------------------------------------------------
    # Document / Knowledge Hub integration
    # ------------------------------------------------------------------

    def on_document_saved(
        self,
        document_name: str,
        project_name: Optional[str] = None,
        notion_page_id: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Auto-register a saved document and optionally link to a project."""
        try:
            props = {**(properties or {})}
            if notion_page_id:
                props["notion_page_id"] = notion_page_id

            doc = self._engine.ensure_entity(EntityType.DOCUMENT, document_name, props)

            if project_name:
                self._engine.link_document_to_project(document_name, project_name)

            if notion_page_id:
                page = self._engine.ensure_entity(
                    EntityType.NOTION_PAGE, f"Notion:{notion_page_id}", {"page_id": notion_page_id}
                )
                self._engine.ensure_relationship(
                    doc.entity_id, page.entity_id, RelationshipType.REFERENCES
                )

            logger.debug("Graph: document '%s' saved", document_name)
        except Exception as exc:
            logger.warning("Graph hook on_document_saved failed: %s", exc)

    # ------------------------------------------------------------------
    # Workflow / n8n integration
    # ------------------------------------------------------------------

    def on_workflow_deployed(
        self,
        workflow_name: str,
        project_name: Optional[str] = None,
        model_name: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Auto-register a deployed workflow."""
        try:
            self._engine.ensure_entity(EntityType.WORKFLOW, workflow_name, properties)

            if project_name:
                self._engine.link_workflow_to_project(workflow_name, project_name)

            if model_name:
                self._engine.link_model_to_workflow(model_name, workflow_name)

            logger.debug("Graph: workflow '%s' deployed", workflow_name)
        except Exception as exc:
            logger.warning("Graph hook on_workflow_deployed failed: %s", exc)

    # ------------------------------------------------------------------
    # Decision Engine integration
    # ------------------------------------------------------------------

    def on_decision_recorded(
        self,
        decision_title: str,
        project_name: Optional[str] = None,
        rationale: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Auto-register a recorded decision."""
        try:
            props = {**(properties or {})}
            if rationale:
                props["rationale"] = rationale

            self._engine.ensure_entity(EntityType.DECISION, decision_title, props)

            if project_name:
                self._engine.link_decision_to_project(decision_title, project_name)

            logger.debug("Graph: decision '%s' recorded", decision_title)
        except Exception as exc:
            logger.warning("Graph hook on_decision_recorded failed: %s", exc)

    # ------------------------------------------------------------------
    # Memory Service integration
    # ------------------------------------------------------------------

    def on_memory_stored(
        self,
        memory_title: str,
        memory_category: str,
        project_name: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Reflect a stored memory into the graph as a Document node."""
        try:
            props = {"memory_category": memory_category, **(properties or {})}
            doc = self._engine.ensure_entity(EntityType.DOCUMENT, memory_title, props)

            if project_name:
                project = self._engine.ensure_entity(EntityType.PROJECT, project_name)
                self._engine.ensure_relationship(
                    project.entity_id, doc.entity_id, RelationshipType.CONTAINS
                )

            logger.debug("Graph: memory '%s' reflected", memory_title)
        except Exception as exc:
            logger.warning("Graph hook on_memory_stored failed: %s", exc)

    # ------------------------------------------------------------------
    # Research integration
    # ------------------------------------------------------------------

    def on_research_completed(
        self,
        research_title: str,
        project_name: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Register completed research in the graph."""
        try:
            research = self._engine.ensure_entity(EntityType.RESEARCH, research_title, properties)

            if project_name:
                project = self._engine.ensure_entity(EntityType.PROJECT, project_name)
                self._engine.ensure_relationship(
                    research.entity_id, project.entity_id, RelationshipType.SUPPORTS
                )

            logger.debug("Graph: research '%s' registered", research_title)
        except Exception as exc:
            logger.warning("Graph hook on_research_completed failed: %s", exc)
