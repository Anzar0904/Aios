# Graph CLI Reference — Phase 4.5

The `aios graph` command group provides interactive access to the Universal Knowledge Graph.

## Commands

### `aios graph` or `aios graph stats`

Display aggregate statistics for the knowledge graph.

```
$ aios graph

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━┓
┃ Metric                        ┃ Value ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━┩
│ Total Entities                │ 47    │
│ Total Relationships           │ 89    │
│ Total Events                  │ 312   │
│ ─────────────────────────     │       │
│   project                     │ 8     │
│   task                        │ 24    │
│   document                    │ 11    │
│   workflow                    │ 4     │
│ ─────────────────────────     │       │
│   BELONGS_TO                  │ 45    │
│   CONTAINS                    │ 22    │
│   SUPPORTS                    │ 12    │
└───────────────────────────────┴───────┘
```

---

### `aios graph search <query>`

Full-text search across entity names and property values.

```
$ aios graph search "AI OS"

🔍 Graph Search: 'AI OS' (3 results)
┏━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┓
┃ Entity ID       ┃ Type      ┃ Name                 ┃ Updated            ┃
┡━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━┩
│ a1b2c3d4e5...   │ project   │ AI OS Core           │ 2026-07-14 15:30   │
│ f6g7h8i9j0...   │ document  │ AI OS Architecture   │ 2026-07-14 12:10   │
│ k1l2m3n4o5...   │ task      │ Build AI OS Phase 5  │ 2026-07-13 08:00   │
└─────────────────┴───────────┴──────────────────────┴────────────────────┘
Query time: 1.2ms
```

---

### `aios graph relations <entity_name> [direction]`

Display all relationships for a named entity.

**Arguments:**
- `entity_name` — name or partial name of the entity
- `direction` — `both` (default), `inbound`, or `outbound`

```
$ aios graph relations "AI OS Core" outbound

╭─────────────────── 🔗 Entity Relations ────────────────────╮
│ AI OS Core                                                  │
│ Type: project  |  ID: a1b2c3d4e5f6g7h8...                  │
╰─────────────────────────────────────────────────────────────╯

Relationships (outbound)
┏━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┓
┃ Direction   ┃ Relationship ┃ Neighbor Name          ┃ Neighbor Type┃
┡━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━┩
│ → outbound  │ CONTAINS   │ PHASE45_KNOWLEDGE_GRAPH │ document    │
│ → outbound  │ CONTAINS   │ Architecture.md         │ document    │
└─────────────┴────────────┴─────────────────────────┴─────────────┘
```

---

### `aios graph project <project_name>`

Display the full knowledge subgraph rooted at a project.

```
$ aios graph project "AI OS Core"

╭─────────────────── 🗂️  Project Knowledge Graph ────────────────────╮
│ AI OS Core                                                          │
│ ID: a1b2c3d4e5f6g7h8i9j0k1l2...                                    │
│ Total graph nodes: 18  |  Relationships: 24                         │
╰─────────────────────────────────────────────────────────────────────╯

TASK (12)
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┓
┃ Name                             ┃ Entity ID       ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━┩
│ Implement Knowledge Graph        │ b2c3d4e5f6...   │
│ Write Phase 4.5 tests            │ c3d4e5f6g7...   │
└──────────────────────────────────┴─────────────────┘

DOCUMENT (4)
...
```

---

### `aios graph path <source_name> <target_name>`

Find the shortest path between two named entities.

```
$ aios graph path "Write Tests" "AI OS Core"

╭────────────────── 🛤️  Shortest Path ──────────────────────╮
│ Path: Write Tests → AI OS Core                             │
│ Length: 1 hop(s)  |  Time: 0.8ms                           │
╰─────────────────────────────────────────────────────────────╯
```

---

### `aios graph health`

Verify the graph engine is operational.

```
$ aios graph health

╭─────────── Knowledge Graph Health ───────────╮
│ ✓ Healthy                                     │
╰───────────────────────────────────────────────╯
```

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `AIOS_GRAPH_DB` | `~/.aios_graph.db` | Path to the SQLite database file |

---

## Python API

```python
from aios.services.graph_impl import GraphServiceImpl
from aios.services.graph_query import GraphQueryEngine
from aios.services.graph_hooks import GraphIntegrationHooks
from aios.services.graph import EntityType, RelationshipType, new_entity, new_relationship

# Initialize
graph = GraphServiceImpl()
graph.initialize()

# High-level API
engine = GraphQueryEngine(graph)
engine.link_task_to_project("My Task", "My Project")
result = engine.search_graph("My")

# Auto-integration hooks
hooks = GraphIntegrationHooks(graph)
hooks.on_task_created("task-001", "Deploy Service", project_name="Infra")
hooks.on_document_saved("README.md", project_name="Infra")

graph.shutdown()
```
