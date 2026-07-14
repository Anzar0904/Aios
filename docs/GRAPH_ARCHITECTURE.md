# Knowledge Graph — Architecture Deep-Dive

## Design Philosophy

The Universal Knowledge Graph is designed around three principles:

1. **Zero dependencies** — pure Python + SQLite, works in CI without external services
2. **Fault-tolerant integration** — hooks never crash primary services
3. **Immutable audit trail** — every mutation is permanently recorded as an event

## Storage Engine

| Feature | Implementation |
|---------|----------------|
| Database | SQLite 3 |
| Journal mode | WAL (Write-Ahead Logging) — concurrent reads during writes |
| Foreign keys | `ON DELETE CASCADE` — entity deletion auto-removes edges |
| Thread safety | Module-level `threading.Lock` around write operations |
| Default location | `~/.aios_graph.db` (overridable via `AIOS_GRAPH_DB` env var) |
| CI location | In-memory / tmp via pytest `tmp_path` fixture |

## Transaction Model

All write operations use a context manager `_tx()` that wraps every mutation
in an explicit SQLite transaction. Read operations acquire the lock but do not
open a transaction, allowing parallel reads via WAL.

```python
@contextmanager
def _tx(self) -> Generator[sqlite3.Connection, None, None]:
    with self._lock:
        with self._conn:  # implicit COMMIT on success, ROLLBACK on error
            yield self._conn
```

## Event Sourcing

Every graph mutation (entity created/updated/deleted, relationship created/deleted)
automatically appends an immutable event to `graph_events`. This provides:

- Full audit trail of knowledge graph evolution
- Ability to replay or diff graph state at any timestamp
- Feed for future streaming integrations (webhooks, Redis pub/sub)

## Path Finding Algorithm

`find_path()` implements **BFS** (Breadth-First Search) across both edge directions:

```
visited = {source_id}
queue = [(source_id, [], [])]
for depth in range(max_depth):
    for each (current, path_entities, path_rels) in queue:
        for each edge incident to current:
            neighbor = opposite_endpoint(edge)
            if neighbor == target: return found path
            if neighbor not in visited: enqueue(neighbor)
```

- Handles cycles via `visited` set
- Returns empty result (not an error) when no path exists
- `max_depth` prevents runaway traversal on large graphs

## Subgraph Extraction

`get_project_subgraph()` performs a **2-hop BFS expansion** from a project node,
collecting all entities reachable within 2 edges in any direction. This captures
the typical "project universe": tasks, documents, workflows, repositories, and
decisions that are directly or transitively connected to the project.

## Integration Points

```
Memory Service         → on_memory_stored()       → DOCUMENT node
Task Engine            → on_task_created()         → TASK node + BELONGS_TO edge
Project Engine         → on_project_created()      → PROJECT + REPOSITORY nodes
Knowledge Hub / Notion → on_document_saved()       → DOCUMENT + NOTION_PAGE nodes
n8n / Workflow Engine  → on_workflow_deployed()    → WORKFLOW + MODEL nodes
Decision Engine        → on_decision_recorded()    → DECISION node
Research Service       → on_research_completed()   → RESEARCH node
```

## Scalability Notes

- SQLite WAL handles 10,000+ entities without performance degradation
- For production at 100k+ nodes, migrate `GraphServiceImpl` to PostgreSQL
  (replace `sqlite3` with `psycopg2`, same schema, minimal code change)
- Full-text search uses LIKE queries; for semantic search, integrate with
  the existing Qdrant vector store via an optional `GraphSearchExtension`
