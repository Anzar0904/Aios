"""Phase 8: Documentation Intelligence — Knowledge Graph Bridge.

Bridges documentation records and technical decision logs into the Universal Knowledge Graph
using DOCUMENTS, DESCRIBES, and GENERATED_FROM edges.
"""

from __future__ import annotations

import logging

from aios.services.documentation import DecisionRecord, DocumentRecord
from aios.services.graph import EntityType, RelationshipType
from aios.services.graph_query import GraphQueryEngine

logger = logging.getLogger(__name__)


class DocumentationGraphBridge:
    """Synchronizes generated documents and technical decision logs to the Knowledge Graph."""

    def __init__(self, graph_engine: GraphQueryEngine) -> None:
        self._engine = graph_engine

    def sync_document(self, doc: DocumentRecord) -> str:
        """Create or update a DOCUMENT node and establish DOCUMENTS link to the project."""
        try:
            props = {
                "doc_type": doc.doc_type.value,
                "version": doc.version,
                "status": doc.status.value,
            }
            entity = self._engine.ensure_entity(EntityType.DOCUMENT, doc.title, props)

            if doc.project_id:
                # Link to project
                proj_entity = self._engine.ensure_entity(
                    EntityType.PROJECT, doc.project_id.capitalize()
                )
                self._engine.ensure_relationship(
                    entity.entity_id, proj_entity.entity_id, RelationshipType.DOCUMENTS
                )
            return entity.entity_id
        except Exception as exc:
            logger.warning("Failed to sync document to graph: %s", exc)
            return ""

    def sync_decision(self, dec: DecisionRecord) -> str:
        """Create or update a DECISION node and link it via RELATED_TO."""
        try:
            props = {
                "category": dec.category,
                "status": dec.status,
                "owner": dec.owner,
            }
            entity = self._engine.ensure_entity(EntityType.DECISION, dec.title, props)
            return entity.entity_id
        except Exception as exc:
            logger.warning("Failed to sync decision to graph: %s", exc)
            return ""
