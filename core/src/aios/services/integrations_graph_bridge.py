"""Phase 7.5: Universal Integration Layer — Knowledge Graph Bridge.

Bridges integration connectors, credentials records, and emitted event streams
into the Universal Knowledge Graph using CONNECTED_TO, AUTHENTICATES, EMITS, and SYNCS edges.
"""

from __future__ import annotations

import logging

from aios.services.graph import EntityType, RelationshipType
from aios.services.graph_query import GraphQueryEngine
from aios.services.integrations import ConnectorConfig, CredentialRecord, IntegrationEvent

logger = logging.getLogger(__name__)


class IntegrationsGraphBridge:
    """Synchronizes universal integrations and events into the Universal Knowledge Graph."""

    def __init__(self, graph_engine: GraphQueryEngine) -> None:
        self._engine = graph_engine

    def sync_connector(self, config: ConnectorConfig) -> str:
        """Create or update a CONNECTOR node in the graph."""
        try:
            props = {
                "provider": config.provider,
                "version": config.version,
                "status": config.status.value,
                "health_score": config.health_score,
            }
            entity = self._engine.ensure_entity(EntityType.CONNECTOR, config.name, props)

            # Link to integrations entity
            int_entity = self._engine.ensure_entity(
                EntityType.INTEGRATION, config.provider.capitalize() + " Integration"
            )
            self._engine.ensure_relationship(
                entity.entity_id, int_entity.entity_id, RelationshipType.CONNECTED_TO
            )
            return entity.entity_id
        except Exception as exc:
            logger.warning("Failed to sync connector to graph: %s", exc)
            return ""

    def sync_credential(self, record: CredentialRecord, connector_name: str) -> str:
        """Create or update a CREDENTIAL node and link it to the connector."""
        try:
            props = {
                "key_name": record.key_name,
                "last_rotated": record.last_rotated,
            }
            entity = self._engine.ensure_entity(
                EntityType.CREDENTIAL, f"Vault Key: {record.key_name}", props
            )

            conn_entity = self._engine.ensure_entity(EntityType.CONNECTOR, connector_name)
            self._engine.ensure_relationship(
                entity.entity_id, conn_entity.entity_id, RelationshipType.AUTHENTICATES
            )
            return entity.entity_id
        except Exception as exc:
            logger.warning("Failed to sync credential to graph: %s", exc)
            return ""

    def link_event_to_connector(self, event: IntegrationEvent, connector_name: str) -> None:
        """Create EVENT_SOURCE node and link it to Connector."""
        try:
            props = {
                "event_type": event.event_type,
            }
            entity = self._engine.ensure_entity(
                EntityType.EVENT_SOURCE, f"Event: {event.event_type}", props
            )

            conn_entity = self._engine.ensure_entity(EntityType.CONNECTOR, connector_name)
            self._engine.ensure_relationship(
                conn_entity.entity_id, entity.entity_id, RelationshipType.EMITS
            )
        except Exception as exc:
            logger.warning("Failed to link event in graph: %s", exc)
