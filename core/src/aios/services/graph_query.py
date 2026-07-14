"""Graph Query Engine (Phase 4.5) — higher-level analytical queries.

Wraps GraphService with semantic, domain-aware query capabilities that power
the CLI and integration hooks.
"""

from typing import Any, Dict, Optional

from aios.services.graph import (
    EntityType,
    GraphEntity,
    GraphRelationship,
    GraphService,
    RelationshipType,
    new_entity,
    new_relationship,
)


class GraphQueryEngine:
    """High-level query operations built on top of GraphService."""

    def __init__(self, graph: GraphService) -> None:
        self._graph = graph

    # ------------------------------------------------------------------
    # Convenience factory helpers
    # ------------------------------------------------------------------

    def ensure_entity(
        self,
        entity_type: EntityType,
        name: str,
        properties: Optional[Dict[str, Any]] = None,
    ) -> GraphEntity:
        """Return an existing entity matching type+name, or create it."""
        results = self._graph.find_entities(entity_type=entity_type, name_contains=name)
        for e in results:
            if e.name.lower() == name.lower():
                return e
        entity = new_entity(entity_type, name, properties)
        return self._graph.create_entity(entity)

    def ensure_relationship(
        self,
        source_id: str,
        target_id: str,
        rel_type: RelationshipType,
        properties: Optional[Dict[str, Any]] = None,
    ) -> GraphRelationship:
        """Return an existing relationship, or create it."""
        existing = self._graph.find_relationships(
            source_id=source_id,
            target_id=target_id,
            relationship_type=rel_type,
        )
        if existing:
            return existing[0]
        rel = new_relationship(source_id, target_id, rel_type, properties)
        return self._graph.create_relationship(rel)

    # ------------------------------------------------------------------
    # Domain-specific auto-link helpers
    # ------------------------------------------------------------------

    def link_task_to_project(self, task_name: str, project_name: str) -> Dict[str, Any]:
        """Create task entity and link it to a project via BELONGS_TO."""
        project = self.ensure_entity(EntityType.PROJECT, project_name)
        task = self.ensure_entity(EntityType.TASK, task_name)
        rel = self.ensure_relationship(
            task.entity_id, project.entity_id, RelationshipType.BELONGS_TO
        )
        return {"task": task.to_dict(), "project": project.to_dict(), "relationship": rel.to_dict()}

    def link_document_to_project(self, doc_name: str, project_name: str) -> Dict[str, Any]:
        """Create document entity and link it to a project via CONTAINS."""
        project = self.ensure_entity(EntityType.PROJECT, project_name)
        doc = self.ensure_entity(EntityType.DOCUMENT, doc_name)
        rel = self.ensure_relationship(project.entity_id, doc.entity_id, RelationshipType.CONTAINS)
        return {
            "document": doc.to_dict(),
            "project": project.to_dict(),
            "relationship": rel.to_dict(),
        }

    def link_workflow_to_project(self, workflow_name: str, project_name: str) -> Dict[str, Any]:
        """Create workflow entity and link to project via SUPPORTS."""
        project = self.ensure_entity(EntityType.PROJECT, project_name)
        wf = self.ensure_entity(EntityType.WORKFLOW, workflow_name)
        rel = self.ensure_relationship(wf.entity_id, project.entity_id, RelationshipType.SUPPORTS)
        return {
            "workflow": wf.to_dict(),
            "project": project.to_dict(),
            "relationship": rel.to_dict(),
        }

    def link_decision_to_project(self, decision_name: str, project_name: str) -> Dict[str, Any]:
        """Record a decision entity and link to project via REFERENCES."""
        project = self.ensure_entity(EntityType.PROJECT, project_name)
        decision = self.ensure_entity(EntityType.DECISION, decision_name)
        rel = self.ensure_relationship(
            decision.entity_id, project.entity_id, RelationshipType.REFERENCES
        )
        return {
            "decision": decision.to_dict(),
            "project": project.to_dict(),
            "relationship": rel.to_dict(),
        }

    def link_repository_to_project(self, repo_name: str, project_name: str) -> Dict[str, Any]:
        """Link a repository to a project via BELONGS_TO."""
        project = self.ensure_entity(EntityType.PROJECT, project_name)
        repo = self.ensure_entity(EntityType.REPOSITORY, repo_name)
        rel = self.ensure_relationship(
            repo.entity_id, project.entity_id, RelationshipType.BELONGS_TO
        )
        return {
            "repository": repo.to_dict(),
            "project": project.to_dict(),
            "relationship": rel.to_dict(),
        }

    def link_model_to_workflow(self, model_name: str, workflow_name: str) -> Dict[str, Any]:
        """Link an AI model to a workflow via USES."""
        workflow = self.ensure_entity(EntityType.WORKFLOW, workflow_name)
        model = self.ensure_entity(EntityType.MODEL, model_name)
        rel = self.ensure_relationship(workflow.entity_id, model.entity_id, RelationshipType.USES)
        return {
            "model": model.to_dict(),
            "workflow": workflow.to_dict(),
            "relationship": rel.to_dict(),
        }

    # ------------------------------------------------------------------
    # Analytical queries
    # ------------------------------------------------------------------

    def get_entity_summary(self, entity_id: str) -> Dict[str, Any]:
        """Comprehensive summary: entity + neighbors + recent events."""
        entity = self._graph.get_entity(entity_id)
        if not entity:
            return {"error": f"Entity {entity_id} not found"}

        neighbors = self._graph.get_neighbors(entity_id)
        events = self._graph.get_events(entity_id=entity_id, limit=10)

        return {
            "entity": entity.to_dict(),
            "neighbors": {
                "count": len(neighbors.entities),
                "entities": [e.to_dict() for e in neighbors.entities],
                "relationships": [r.to_dict() for r in neighbors.relationships],
            },
            "recent_events": [e.to_dict() for e in events],
        }

    def get_project_overview(self, project_name: str) -> Dict[str, Any]:
        """Complete project graph overview including tasks, docs, workflows."""
        projects = self._graph.find_entities(
            entity_type=EntityType.PROJECT, name_contains=project_name
        )
        if not projects:
            return {"error": f"No project matching '{project_name}'"}

        project = projects[0]
        subgraph = self._graph.get_project_subgraph(project.entity_id)

        # Group by entity type
        by_type: Dict[str, list] = {}
        for e in subgraph.entities:
            key = e.entity_type.value
            by_type.setdefault(key, []).append(e.to_dict())

        return {
            "project": project.to_dict(),
            "subgraph": {
                "total_nodes": subgraph.total_count,
                "by_type": by_type,
                "relationships": [r.to_dict() for r in subgraph.relationships],
                "query_time_ms": subgraph.query_time_ms,
            },
        }

    def search_graph(self, query: str, limit: int = 20) -> Dict[str, Any]:
        """Search the graph and return structured results."""
        result = self._graph.search(query, limit=limit)
        return {
            "query": query,
            "total": result.total_count,
            "entities": [e.to_dict() for e in result.entities],
            "query_time_ms": result.query_time_ms,
        }

    def get_relations(
        self,
        entity_name: str,
        entity_type: Optional[EntityType] = None,
        direction: str = "both",
    ) -> Dict[str, Any]:
        """Return relationship summary for a named entity."""
        entities = self._graph.find_entities(entity_type=entity_type, name_contains=entity_name)
        if not entities:
            return {"error": f"No entity matching '{entity_name}'"}

        entity = entities[0]
        neighbors = self._graph.get_neighbors(entity.entity_id, direction=direction)

        return {
            "entity": entity.to_dict(),
            "direction": direction,
            "relationship_count": len(neighbors.relationships),
            "relationships": [r.to_dict() for r in neighbors.relationships],
            "neighbors": [e.to_dict() for e in neighbors.entities],
            "query_time_ms": neighbors.query_time_ms,
        }

    def get_stats_summary(self) -> Dict[str, Any]:
        """Return human-readable graph statistics."""
        stats = self._graph.get_stats()
        return {
            "total_entities": stats.total_entities,
            "total_relationships": stats.total_relationships,
            "total_events": stats.total_events,
            "entities_by_type": stats.entity_counts,
            "relationships_by_type": stats.relationship_counts,
            "generated_at": stats.generated_at,
        }

    def find_path(self, source_name: str, target_name: str) -> Dict[str, Any]:
        """Find shortest path between two named entities."""
        sources = self._graph.find_entities(name_contains=source_name)
        targets = self._graph.find_entities(name_contains=target_name)

        if not sources:
            return {"error": f"Source entity '{source_name}' not found"}
        if not targets:
            return {"error": f"Target entity '{target_name}' not found"}

        result = self._graph.find_path(sources[0].entity_id, targets[0].entity_id)

        if not result.entities:
            return {
                "source": sources[0].name,
                "target": targets[0].name,
                "path_found": False,
                "message": "No path found between these entities",
            }

        return {
            "source": sources[0].name,
            "target": targets[0].name,
            "path_found": True,
            "path_length": len(result.relationships),
            "entities": [e.to_dict() for e in result.entities],
            "relationships": [r.to_dict() for r in result.relationships],
            "query_time_ms": result.query_time_ms,
        }
