"""Phase 10: Research Intelligence — Knowledge Graph Bridge.

Bridges research projects, ingested academic papers, findings, and experiments
into the Universal Knowledge Graph using SUPPORTS, CITES, and DERIVED_FROM edges.
"""

from __future__ import annotations

import logging

from aios.services.graph import EntityType, RelationshipType
from aios.services.graph_query import GraphQueryEngine
from aios.services.research import IngestedPaper, ResearchProject

logger = logging.getLogger(__name__)


class ResearchGraphBridge:
    """Synchronizes research projects and ingested papers to the Knowledge Graph."""

    def __init__(self, graph_engine: GraphQueryEngine) -> None:
        self._engine = graph_engine

    def sync_research_project(self, project: ResearchProject) -> str:
        """Create or update a RESEARCH node in the graph."""
        try:
            props = {
                "category": project.category,
                "status": project.status,
            }
            entity = self._engine.ensure_entity(EntityType.RESEARCH, project.title, props)
            return entity.entity_id
        except Exception as exc:
            logger.warning("Failed to sync research project to graph: %s", exc)
            return ""

    def sync_ingested_paper(self, paper: IngestedPaper, research_name: str) -> str:
        """Create or update a PAPER node and link it via CITES to the project."""
        try:
            props = {
                "summary": paper.summary,
            }
            entity = self._engine.ensure_entity(EntityType.PAPER, paper.title, props)

            res_entity = self._engine.ensure_entity(EntityType.RESEARCH, research_name)
            self._engine.ensure_relationship(
                entity.entity_id, res_entity.entity_id, RelationshipType.CITES
            )
            return entity.entity_id
        except Exception as exc:
            logger.warning("Failed to sync paper to graph: %s", exc)
            return ""
