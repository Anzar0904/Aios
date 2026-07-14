"""Phase 7: n8n Automation Intelligence — Graph Integration.

Bridges the Workflow Registry Service with the Phase 4.5 Universal Knowledge Graph.
Registers workflow nodes, deployment versions, webhooks, and connects them
to Projects and CRM Client entities via BELONGS_TO, SERVES, and DEPLOYED_BY links.
"""

from __future__ import annotations

import logging

from aios.services.graph import EntityType, RelationshipType
from aios.services.graph_query import GraphQueryEngine
from aios.services.workflows import Deployment, Workflow, WorkflowExecution

logger = logging.getLogger(__name__)


class WorkflowsGraphBridge:
    """Synchronizes Workflow items and events into the Universal Knowledge Graph."""

    def __init__(self, graph_engine: GraphQueryEngine) -> None:
        self._engine = graph_engine

    def sync_workflow(self, workflow: Workflow) -> str:
        """Create or update a WORKFLOW node in the graph."""
        try:
            props = {
                "version": workflow.version,
                "webhook_url": workflow.webhook_url,
                "status": workflow.status.value,
                "health_score": workflow.health_score,
                "nodes_count": len(workflow.nodes),
            }
            entity = self._engine.ensure_entity(
                EntityType.WORKFLOW, workflow.name, props
            )

            # Link to project if available
            if workflow.project_id:
                # Link to project node via BELONGS_TO
                self._engine.ensure_relationship(
                    entity.entity_id, workflow.project_id, RelationshipType.BELONGS_TO
                )

            return entity.entity_id
        except Exception as exc:
            logger.warning("Failed to sync workflow to graph: %s", exc)
            return ""

    def sync_deployment(self, deployment: Deployment) -> str:
        """Create or update a DEPLOYMENT node in the graph."""
        try:
            props = {
                "version": deployment.version,
                "status": deployment.status.value,
                "nodes_count": deployment.nodes_count,
                "changelog": deployment.changelog,
            }
            entity = self._engine.ensure_entity(
                EntityType.DEPLOYMENT, f"Deployment v{deployment.version} — {deployment.workflow_id[:8]}", props
            )

            # Link deployment to workflow via DEPLOYED_BY or USES
            wf_node = self._engine.ensure_entity(EntityType.WORKFLOW, deployment.workflow_id)
            self._engine.ensure_relationship(
                entity.entity_id, wf_node.entity_id, RelationshipType.BELONGS_TO
            )
            return entity.entity_id
        except Exception as exc:
            logger.warning("Failed to sync deployment to graph: %s", exc)
            return ""

    def sync_webhook(self, name: str, url: str, workflow_name: str) -> None:
        """Register a Webhook node serving a Workflow."""
        try:
            props = {"url": url}
            entity = self._engine.ensure_entity(EntityType.WEBHOOK, name, props)
            wf = self._engine.ensure_entity(EntityType.WORKFLOW, workflow_name)
            self._engine.ensure_relationship(
                entity.entity_id, wf.entity_id, RelationshipType.SERVES
            )
        except Exception as exc:
            logger.warning("Failed to sync webhook in graph: %s", exc)

    def link_execution_to_workflow(self, execution: WorkflowExecution, workflow_name: str) -> None:
        """Register Execution and link to Workflow."""
        try:
            props = {
                "status": execution.status.value,
                "latency_ms": execution.latency_ms,
                "failed_node": execution.failed_node,
            }
            entity = self._engine.ensure_entity(
                EntityType.EXECUTION, f"Exec {execution.execution_id[:8]}", props
            )
            wf = self._engine.ensure_entity(EntityType.WORKFLOW, workflow_name)
            self._engine.ensure_relationship(
                wf.entity_id, entity.entity_id, RelationshipType.EXECUTES
            )
        except Exception as exc:
            logger.warning("Failed to link execution in graph: %s", exc)
