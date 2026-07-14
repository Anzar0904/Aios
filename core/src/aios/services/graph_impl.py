"""SQLite-backed implementation of the Universal Knowledge Graph (Phase 4.5).

Stores entities, relationships, and events in a local SQLite database so the
graph works in CI and on developer machines without any external services.
"""

import json
import logging
import os
import sqlite3
import time
from contextlib import contextmanager
from threading import Lock
from typing import Any, Dict, Generator, List, Optional

from aios.services.graph import (
    EntityType,
    GraphEntity,
    GraphEvent,
    GraphEventType,
    GraphQueryResult,
    GraphRelationship,
    GraphService,
    GraphStats,
    RelationshipType,
    new_event,
)

logger = logging.getLogger(__name__)

_DEFAULT_DB_PATH = os.path.join(os.path.expanduser("~"), ".aios_graph.db")


class GraphServiceImpl(GraphService):
    """SQLite-backed knowledge graph engine."""

    def __init__(self, db_path: Optional[str] = None) -> None:
        self._db_path = db_path or os.getenv("AIOS_GRAPH_DB", _DEFAULT_DB_PATH)
        self._lock = Lock()
        self._conn: Optional[sqlite3.Connection] = None

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def initialize(self) -> None:
        self._conn = sqlite3.connect(self._db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA foreign_keys=ON")
        self._bootstrap_schema()
        logger.info("GraphService initialized — db: %s", self._db_path)

    def start(self) -> None:
        pass

    def shutdown(self) -> None:
        if self._conn:
            self._conn.close()
            self._conn = None

    def ready(self) -> bool:
        return self._conn is not None

    # ------------------------------------------------------------------
    # Schema
    # ------------------------------------------------------------------

    def _bootstrap_schema(self) -> None:
        assert self._conn is not None
        with self._conn:
            self._conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS entities (
                    entity_id      TEXT PRIMARY KEY,
                    entity_type    TEXT NOT NULL,
                    name           TEXT NOT NULL,
                    properties     TEXT NOT NULL DEFAULT '{}',
                    created_at     REAL NOT NULL,
                    updated_at     REAL NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_entities_type
                    ON entities (entity_type);
                CREATE INDEX IF NOT EXISTS idx_entities_name
                    ON entities (name COLLATE NOCASE);

                CREATE TABLE IF NOT EXISTS relationships (
                    relationship_id   TEXT PRIMARY KEY,
                    source_id         TEXT NOT NULL,
                    target_id         TEXT NOT NULL,
                    relationship_type TEXT NOT NULL,
                    properties        TEXT NOT NULL DEFAULT '{}',
                    created_at        REAL NOT NULL,
                    FOREIGN KEY (source_id) REFERENCES entities(entity_id)
                        ON DELETE CASCADE,
                    FOREIGN KEY (target_id) REFERENCES entities(entity_id)
                        ON DELETE CASCADE
                );

                CREATE INDEX IF NOT EXISTS idx_rel_source
                    ON relationships (source_id);
                CREATE INDEX IF NOT EXISTS idx_rel_target
                    ON relationships (target_id);
                CREATE INDEX IF NOT EXISTS idx_rel_type
                    ON relationships (relationship_type);

                CREATE TABLE IF NOT EXISTS graph_events (
                    event_id         TEXT PRIMARY KEY,
                    event_type       TEXT NOT NULL,
                    entity_id        TEXT,
                    relationship_id  TEXT,
                    payload          TEXT NOT NULL DEFAULT '{}',
                    timestamp        REAL NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_events_entity
                    ON graph_events (entity_id);
                CREATE INDEX IF NOT EXISTS idx_events_type
                    ON graph_events (event_type);
                """
            )

    # ------------------------------------------------------------------
    # Connection helper
    # ------------------------------------------------------------------

    @contextmanager
    def _tx(self) -> Generator[sqlite3.Connection, None, None]:
        assert self._conn is not None, "GraphService not initialized"
        with self._lock:
            with self._conn:
                yield self._conn

    # ------------------------------------------------------------------
    # Entity helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _row_to_entity(row: sqlite3.Row) -> GraphEntity:
        return GraphEntity(
            entity_id=row["entity_id"],
            entity_type=EntityType(row["entity_type"]),
            name=row["name"],
            properties=json.loads(row["properties"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    @staticmethod
    def _row_to_relationship(row: sqlite3.Row) -> GraphRelationship:
        return GraphRelationship(
            relationship_id=row["relationship_id"],
            source_id=row["source_id"],
            target_id=row["target_id"],
            relationship_type=RelationshipType(row["relationship_type"]),
            properties=json.loads(row["properties"]),
            created_at=row["created_at"],
        )

    @staticmethod
    def _row_to_event(row: sqlite3.Row) -> GraphEvent:
        return GraphEvent(
            event_id=row["event_id"],
            event_type=GraphEventType(row["event_type"]),
            entity_id=row["entity_id"],
            relationship_id=row["relationship_id"],
            payload=json.loads(row["payload"]),
            timestamp=row["timestamp"],
        )

    # ------------------------------------------------------------------
    # Entity operations
    # ------------------------------------------------------------------

    def create_entity(self, entity: GraphEntity) -> GraphEntity:
        with self._tx() as conn:
            conn.execute(
                """
                INSERT INTO entities
                    (entity_id, entity_type, name, properties, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    entity.entity_id,
                    entity.entity_type.value,
                    entity.name,
                    json.dumps(entity.properties),
                    entity.created_at,
                    entity.updated_at,
                ),
            )
        evt = new_event(
            GraphEventType.ENTITY_CREATED,
            entity_id=entity.entity_id,
            payload={"entity_type": entity.entity_type.value, "name": entity.name},
        )
        self.record_event(evt)
        return entity

    def get_entity(self, entity_id: str) -> Optional[GraphEntity]:
        assert self._conn is not None
        with self._lock:
            row = self._conn.execute(
                "SELECT * FROM entities WHERE entity_id = ?", (entity_id,)
            ).fetchone()
        return self._row_to_entity(row) if row else None

    def find_entities(
        self,
        entity_type: Optional[EntityType] = None,
        name_contains: Optional[str] = None,
        limit: int = 50,
    ) -> List[GraphEntity]:
        assert self._conn is not None
        query = "SELECT * FROM entities WHERE 1=1"
        params: list = []
        if entity_type:
            query += " AND entity_type = ?"
            params.append(entity_type.value)
        if name_contains:
            query += " AND name LIKE ?"
            params.append(f"%{name_contains}%")
        query += " ORDER BY updated_at DESC LIMIT ?"
        params.append(limit)
        with self._lock:
            rows = self._conn.execute(query, params).fetchall()
        return [self._row_to_entity(r) for r in rows]

    def update_entity(self, entity_id: str, updates: Dict[str, Any]) -> Optional[GraphEntity]:
        entity = self.get_entity(entity_id)
        if not entity:
            return None
        new_props = {**entity.properties, **updates.get("properties", {})}
        new_name = updates.get("name", entity.name)
        now = time.time()
        with self._tx() as conn:
            conn.execute(
                """
                UPDATE entities
                SET name = ?, properties = ?, updated_at = ?
                WHERE entity_id = ?
                """,
                (new_name, json.dumps(new_props), now, entity_id),
            )
        evt = new_event(
            GraphEventType.ENTITY_UPDATED,
            entity_id=entity_id,
            payload=updates,
        )
        self.record_event(evt)
        return self.get_entity(entity_id)

    def delete_entity(self, entity_id: str) -> bool:
        entity = self.get_entity(entity_id)
        if not entity:
            return False
        with self._tx() as conn:
            conn.execute("DELETE FROM entities WHERE entity_id = ?", (entity_id,))
        evt = new_event(
            GraphEventType.ENTITY_DELETED,
            entity_id=entity_id,
            payload={"name": entity.name},
        )
        self.record_event(evt)
        return True

    # ------------------------------------------------------------------
    # Relationship operations
    # ------------------------------------------------------------------

    def create_relationship(self, relationship: GraphRelationship) -> GraphRelationship:
        with self._tx() as conn:
            conn.execute(
                """
                INSERT INTO relationships
                    (relationship_id, source_id, target_id,
                     relationship_type, properties, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    relationship.relationship_id,
                    relationship.source_id,
                    relationship.target_id,
                    relationship.relationship_type.value,
                    json.dumps(relationship.properties),
                    relationship.created_at,
                ),
            )
        evt = new_event(
            GraphEventType.RELATIONSHIP_CREATED,
            relationship_id=relationship.relationship_id,
            payload={
                "source_id": relationship.source_id,
                "target_id": relationship.target_id,
                "type": relationship.relationship_type.value,
            },
        )
        self.record_event(evt)
        return relationship

    def get_relationship(self, relationship_id: str) -> Optional[GraphRelationship]:
        assert self._conn is not None
        with self._lock:
            row = self._conn.execute(
                "SELECT * FROM relationships WHERE relationship_id = ?", (relationship_id,)
            ).fetchone()
        return self._row_to_relationship(row) if row else None

    def find_relationships(
        self,
        source_id: Optional[str] = None,
        target_id: Optional[str] = None,
        relationship_type: Optional[RelationshipType] = None,
        limit: int = 50,
    ) -> List[GraphRelationship]:
        assert self._conn is not None
        query = "SELECT * FROM relationships WHERE 1=1"
        params: list = []
        if source_id:
            query += " AND source_id = ?"
            params.append(source_id)
        if target_id:
            query += " AND target_id = ?"
            params.append(target_id)
        if relationship_type:
            query += " AND relationship_type = ?"
            params.append(relationship_type.value)
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        with self._lock:
            rows = self._conn.execute(query, params).fetchall()
        return [self._row_to_relationship(r) for r in rows]

    def delete_relationship(self, relationship_id: str) -> bool:
        rel = self.get_relationship(relationship_id)
        if not rel:
            return False
        with self._tx() as conn:
            conn.execute("DELETE FROM relationships WHERE relationship_id = ?", (relationship_id,))
        evt = new_event(
            GraphEventType.RELATIONSHIP_DELETED,
            relationship_id=relationship_id,
            payload={"source_id": rel.source_id, "target_id": rel.target_id},
        )
        self.record_event(evt)
        return True

    # ------------------------------------------------------------------
    # Event operations
    # ------------------------------------------------------------------

    def record_event(self, event: GraphEvent) -> GraphEvent:
        assert self._conn is not None
        with self._lock:
            with self._conn:
                self._conn.execute(
                    """
                    INSERT INTO graph_events
                        (event_id, event_type, entity_id, relationship_id,
                         payload, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        event.event_id,
                        event.event_type.value,
                        event.entity_id,
                        event.relationship_id,
                        json.dumps(event.payload),
                        event.timestamp,
                    ),
                )
        return event

    def get_events(
        self,
        entity_id: Optional[str] = None,
        event_type: Optional[GraphEventType] = None,
        limit: int = 100,
    ) -> List[GraphEvent]:
        assert self._conn is not None
        query = "SELECT * FROM graph_events WHERE 1=1"
        params: list = []
        if entity_id:
            query += " AND entity_id = ?"
            params.append(entity_id)
        if event_type:
            query += " AND event_type = ?"
            params.append(event_type.value)
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        with self._lock:
            rows = self._conn.execute(query, params).fetchall()
        return [self._row_to_event(r) for r in rows]

    # ------------------------------------------------------------------
    # Query operations
    # ------------------------------------------------------------------

    def get_neighbors(
        self,
        entity_id: str,
        relationship_type: Optional[RelationshipType] = None,
        direction: str = "both",
    ) -> GraphQueryResult:
        start = time.time()
        assert self._conn is not None

        neighbor_ids: set = set()
        rels: List[GraphRelationship] = []

        rel_filter = ""
        params_base: list = []
        if relationship_type:
            rel_filter = " AND relationship_type = ?"
            params_base.append(relationship_type.value)

        with self._lock:
            if direction in ("outbound", "both"):
                rows = self._conn.execute(
                    f"SELECT * FROM relationships WHERE source_id = ?{rel_filter}",
                    [entity_id] + params_base,
                ).fetchall()
                for r in rows:
                    rel = self._row_to_relationship(r)
                    rels.append(rel)
                    neighbor_ids.add(rel.target_id)

            if direction in ("inbound", "both"):
                rows = self._conn.execute(
                    f"SELECT * FROM relationships WHERE target_id = ?{rel_filter}",
                    [entity_id] + params_base,
                ).fetchall()
                for r in rows:
                    rel = self._row_to_relationship(r)
                    rels.append(rel)
                    neighbor_ids.add(rel.source_id)

            entities = []
            for nid in neighbor_ids:
                row = self._conn.execute(
                    "SELECT * FROM entities WHERE entity_id = ?", (nid,)
                ).fetchone()
                if row:
                    entities.append(self._row_to_entity(row))

        return GraphQueryResult(
            entities=entities,
            relationships=rels,
            total_count=len(entities),
            query_time_ms=(time.time() - start) * 1000,
        )

    def find_path(self, source_id: str, target_id: str, max_depth: int = 5) -> GraphQueryResult:
        """BFS shortest path between two entities."""
        start = time.time()
        assert self._conn is not None

        if source_id == target_id:
            entity = self.get_entity(source_id)
            entities = [entity] if entity else []
            return GraphQueryResult(
                entities=entities,
                total_count=len(entities),
                query_time_ms=(time.time() - start) * 1000,
            )

        visited: set = {source_id}
        queue: list = [(source_id, [], [])]

        for _ in range(max_depth):
            if not queue:
                break
            next_queue: list = []
            for current_id, path_entities, path_rels in queue:
                with self._lock:
                    rows = self._conn.execute(
                        """
                        SELECT * FROM relationships
                        WHERE source_id = ? OR target_id = ?
                        """,
                        (current_id, current_id),
                    ).fetchall()
                for row in rows:
                    rel = self._row_to_relationship(row)
                    neighbor_id = rel.target_id if rel.source_id == current_id else rel.source_id
                    if neighbor_id in visited:
                        continue
                    visited.add(neighbor_id)
                    new_path_rels = path_rels + [rel]
                    neighbor_entity = self.get_entity(neighbor_id)
                    new_path_entities = path_entities + (
                        [neighbor_entity] if neighbor_entity else []
                    )
                    if neighbor_id == target_id:
                        src_entity = self.get_entity(source_id)
                        all_entities = ([src_entity] if src_entity else []) + new_path_entities
                        return GraphQueryResult(
                            entities=all_entities,
                            relationships=new_path_rels,
                            total_count=len(all_entities),
                            query_time_ms=(time.time() - start) * 1000,
                        )
                    next_queue.append((neighbor_id, new_path_entities, new_path_rels))
            queue = next_queue

        return GraphQueryResult(
            total_count=0,
            query_time_ms=(time.time() - start) * 1000,
            metadata={"message": "No path found"},
        )

    def search(self, query: str, limit: int = 20) -> GraphQueryResult:
        start = time.time()
        assert self._conn is not None
        with self._lock:
            rows = self._conn.execute(
                """
                SELECT * FROM entities
                WHERE name LIKE ? OR properties LIKE ?
                ORDER BY updated_at DESC
                LIMIT ?
                """,
                (f"%{query}%", f"%{query}%", limit),
            ).fetchall()
        entities = [self._row_to_entity(r) for r in rows]
        return GraphQueryResult(
            entities=entities,
            total_count=len(entities),
            query_time_ms=(time.time() - start) * 1000,
            metadata={"query": query},
        )

    def get_project_subgraph(self, project_entity_id: str) -> GraphQueryResult:
        """Return the full subgraph rooted at a project entity (2-hop BFS)."""
        start = time.time()
        assert self._conn is not None

        visited_ids: set = set()
        all_entities: List[GraphEntity] = []
        all_rels: List[GraphRelationship] = []

        root = self.get_entity(project_entity_id)
        if not root:
            return GraphQueryResult(query_time_ms=(time.time() - start) * 1000)

        all_entities.append(root)
        visited_ids.add(project_entity_id)

        frontier = [project_entity_id]
        for _ in range(2):  # 2-hop expansion
            next_frontier: list = []
            for eid in frontier:
                result = self.get_neighbors(eid)
                for rel in result.relationships:
                    if rel.relationship_id not in {r.relationship_id for r in all_rels}:
                        all_rels.append(rel)
                for entity in result.entities:
                    if entity.entity_id not in visited_ids:
                        visited_ids.add(entity.entity_id)
                        all_entities.append(entity)
                        next_frontier.append(entity.entity_id)
            frontier = next_frontier

        return GraphQueryResult(
            entities=all_entities,
            relationships=all_rels,
            total_count=len(all_entities),
            query_time_ms=(time.time() - start) * 1000,
        )

    # ------------------------------------------------------------------
    # Stats & health
    # ------------------------------------------------------------------

    def get_stats(self) -> GraphStats:
        assert self._conn is not None
        with self._lock:
            entity_count = self._conn.execute("SELECT COUNT(*) FROM entities").fetchone()[0]
            rel_count = self._conn.execute("SELECT COUNT(*) FROM relationships").fetchone()[0]
            event_count = self._conn.execute("SELECT COUNT(*) FROM graph_events").fetchone()[0]

            entity_by_type = self._conn.execute(
                "SELECT entity_type, COUNT(*) as cnt FROM entities GROUP BY entity_type"
            ).fetchall()
            rel_by_type = self._conn.execute(
                "SELECT relationship_type, COUNT(*) as cnt FROM relationships GROUP BY relationship_type"
            ).fetchall()

        return GraphStats(
            total_entities=entity_count,
            total_relationships=rel_count,
            total_events=event_count,
            entity_counts={r["entity_type"]: r["cnt"] for r in entity_by_type},
            relationship_counts={r["relationship_type"]: r["cnt"] for r in rel_by_type},
        )

    def health_check(self) -> bool:
        try:
            assert self._conn is not None
            self._conn.execute("SELECT 1").fetchone()
            return True
        except Exception:
            return False
