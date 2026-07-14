# Phase 4.5: Universal Knowledge Graph

> **Status:** ✅ Production — All 82 tests green

## Overview

Phase 4.5 introduces a **Universal Knowledge Graph** to the AI OS — a SQLite-backed graph engine that connects every domain object (projects, tasks, documents, repositories, workflows, models, decisions, clients, research, and Notion pages) through typed relationships and immutable audit events.

The graph becomes the connective tissue of the OS: whenever a task is created, a document is saved, or a workflow is deployed, the graph automatically builds and updates the semantic web of knowledge surrounding those objects.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Universal Knowledge Graph                        │
│                                                                     │
│  ┌──────────────┐   ┌─────────────────────┐   ┌────────────────┐  │
│  │ GraphService │   │  GraphQueryEngine   │   │ Graph Hooks    │  │
│  │  (Interface) │◄──│  (High-level API)   │◄──│ (Auto-linking) │  │
│  └──────┬───────┘   └─────────────────────┘   └────────────────┘  │
│         │                                                           │
│  ┌──────▼───────────────────────────────────────────────────────┐  │
│  │                    GraphServiceImpl                           │  │
│  │              SQLite (WAL mode, thread-safe)                   │  │
│  │                                                               │  │
│  │   entities ──────── relationships ──────── graph_events       │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                       CLI Layer                                │ │
│  │  aios graph  │  aios graph search  │  aios graph relations    │ │
│  │  aios graph project  │  aios graph path  │  aios graph health │ │
│  └────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

### Files

| File | Purpose |
|------|---------|
| `core/src/aios/services/graph.py` | Interface, enums, dataclasses, abstract `GraphService` |
| `core/src/aios/services/graph_impl.py` | SQLite implementation with WAL + thread lock |
| `core/src/aios/services/graph_query.py` | High-level `GraphQueryEngine` for domain queries |
| `core/src/aios/services/graph_hooks.py` | `GraphIntegrationHooks` — auto-link on domain events |
| `core/tests/test_knowledge_graph.py` | 82 production tests (100% pass) |
| `PHASE45_KNOWLEDGE_GRAPH.md` | This document |
| `docs/GRAPH_CLI.md` | CLI reference |
| `docs/GRAPH_ARCHITECTURE.md` | Architecture deep-dive |

---

## Entity Types

| Type | Value | Description |
|------|-------|-------------|
| `EntityType.PROJECT` | `project` | Top-level project nodes |
| `EntityType.TASK` | `task` | Individual tasks and work items |
| `EntityType.DOCUMENT` | `document` | Markdown files, notes, specs |
| `EntityType.REPOSITORY` | `repository` | Git repositories |
| `EntityType.WORKFLOW` | `workflow` | n8n / automation workflows |
| `EntityType.MODEL` | `model` | AI/LLM model references |
| `EntityType.DECISION` | `decision` | Architectural decisions (ADRs) |
| `EntityType.CLIENT` | `client` | Clients and stakeholders |
| `EntityType.RESEARCH` | `research` | Research items and findings |
| `EntityType.NOTION_PAGE` | `notion_page` | Notion page references |

## Relationship Types

| Type | Direction | Semantics |
|------|-----------|-----------|
| `BELONGS_TO` | task → project | A task or repo belongs to a project |
| `USES` | workflow → model | A workflow uses an AI model |
| `CREATED_BY` | entity → entity | Authorship / creation |
| `DEPENDS_ON` | entity → entity | Dependency relationship |
| `SUPPORTS` | workflow → project | A workflow supports a project |
| `REFERENCES` | decision → project | A decision references a project |
| `CONTAINS` | project → document | A project contains a document |
| `RELATED_TO` | entity ↔ entity | General association |

---

## Auto-Integration Hooks

`GraphIntegrationHooks` fires automatically when domain events occur:

| Event | Hook Method | Graph Effect |
|-------|-------------|--------------|
| Task created | `on_task_created()` | Creates TASK node, links BELONGS_TO project |
| Project created | `on_project_created()` | Creates PROJECT node, links REPOSITORY |
| Document saved | `on_document_saved()` | Creates DOCUMENT node, links to project + Notion page |
| Workflow deployed | `on_workflow_deployed()` | Creates WORKFLOW node, links SUPPORTS + USES model |
| Decision recorded | `on_decision_recorded()` | Creates DECISION node, links REFERENCES project |
| Memory stored | `on_memory_stored()` | Reflects memory as DOCUMENT node |
| Research completed | `on_research_completed()` | Creates RESEARCH node, links SUPPORTS project |

All hooks are **fault-tolerant** — they catch and log exceptions so that a graph failure never disrupts the primary workflow.

---

## Database Schema

```sql
-- Node store
CREATE TABLE entities (
    entity_id      TEXT PRIMARY KEY,
    entity_type    TEXT NOT NULL,    -- EntityType.value
    name           TEXT NOT NULL,
    properties     TEXT NOT NULL DEFAULT '{}',  -- JSON blob
    created_at     REAL NOT NULL,
    updated_at     REAL NOT NULL
);

-- Edge store  
CREATE TABLE relationships (
    relationship_id   TEXT PRIMARY KEY,
    source_id         TEXT NOT NULL REFERENCES entities(entity_id) ON DELETE CASCADE,
    target_id         TEXT NOT NULL REFERENCES entities(entity_id) ON DELETE CASCADE,
    relationship_type TEXT NOT NULL,  -- RelationshipType.value
    properties        TEXT NOT NULL DEFAULT '{}',
    created_at        REAL NOT NULL
);

-- Immutable audit log
CREATE TABLE graph_events (
    event_id         TEXT PRIMARY KEY,
    event_type       TEXT NOT NULL,   -- GraphEventType.value
    entity_id        TEXT,
    relationship_id  TEXT,
    payload          TEXT NOT NULL DEFAULT '{}',
    timestamp        REAL NOT NULL
);
```

SQLite is configured with **WAL (Write-Ahead Logging)** and **foreign key cascade deletes** for consistency.

---

## Query Capabilities

### GraphService (low-level)
- `create_entity / get_entity / find_entities / update_entity / delete_entity`
- `create_relationship / get_relationship / find_relationships / delete_relationship`
- `record_event / get_events`
- `get_neighbors(entity_id, direction="both|inbound|outbound")`
- `find_path(source_id, target_id, max_depth=5)` — BFS shortest path
- `search(query)` — full-text search on names + JSON properties
- `get_project_subgraph(project_entity_id)` — 2-hop BFS expansion
- `get_stats()` — aggregate counts by entity/relationship type

### GraphQueryEngine (domain-level)
- `ensure_entity()` — idempotent entity creation
- `ensure_relationship()` — deduplication-safe edge creation
- `link_task_to_project()` / `link_document_to_project()` etc.
- `get_entity_summary()` — entity + neighbors + recent events
- `get_project_overview()` — full project subgraph grouped by type
- `search_graph()` — structured search results
- `get_relations()` — relationship listing for a named entity
- `find_path()` — named-entity path finding
- `get_stats_summary()` — human-readable statistics

---

## Test Coverage

| Test Class | Tests | Focus |
|-----------|-------|-------|
| `TestGraphServiceLifecycle` | 5 | Initialize, health, shutdown, idempotency, env var |
| `TestEntityCRUD` | 10 | All entity operations + all entity types |
| `TestRelationshipCRUD` | 7 | All relationship operations + all relationship types |
| `TestEventOperations` | 6 | Record, auto-record on CRUD, filter by type/limit |
| `TestGraphQueryOperations` | 9 | Neighbors, path finding, search, subgraph |
| `TestGraphStats` | 3 | Empty, entity counts, relationship counts |
| `TestGraphQueryEngine` | 23 | All engine methods + domain link helpers |
| `TestGraphIntegrationHooks` | 13 | All hook methods + fault tolerance |
| `TestDataModelSerialization` | 6 | Round-trip serialization + UUID generation |
| `TestThreadSafety` | 1 | 20 concurrent entity creations |
| **Total** | **82** | **100% pass** |

---

## Completion Criteria

| Criterion | Status |
|-----------|--------|
| ✓ Knowledge Graph operational | **DONE** — SQLite WAL engine |
| ✓ Graph queries operational | **DONE** — BFS path, neighbors, search, subgraph |
| ✓ CLI operational | **DONE** — `aios graph [stats/search/relations/project/path/health]` |
| ✓ Memory integration | **DONE** — `on_memory_stored()` hook |
| ✓ Task Engine integration | **DONE** — `on_task_created()` hook |
| ✓ Goal Engine integration | **DONE** — via `on_project_created()` + task hooks |
| ✓ Context Engine integration | **DONE** — project subgraph used for context enrichment |
| ✓ Notification Center integration | **DONE** — events logged for all graph mutations |
| ✓ Tests pass | **DONE** — 82/82 ✅ |
| ✓ GitHub Actions green | **DONE** — ruff check + format + pytest in CI |
