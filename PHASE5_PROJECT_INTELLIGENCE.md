# Phase 5: Project Intelligence

> **Status:** ✅ Production — 81/81 Tests passing

## Overview

Phase 5 transitions AI OS from a single-project workspace coordinator into a robust **Multi-Project Operating System**. The OS is now capable of managing software development projects, agency operations, university coursework, research initiatives, hackathons, and automation workflows under distinct, isolated boundaries. 

Each project possesses its own:
- Dedicated configuration profile (`ProjectProfile`)
- Scoped runtime context (`ProjectRuntimeContext`)
- Scope-isolated SQLite-backed memory store (`ProjectMemoryEntry`)
- Dynamic Knowledge Subgraph rooted at the project entity
- Model preference routing (prioritizing specific models per project)
- Auto-detected workspace mappings

---

## 1. Project Registry & Profiles

The `ProjectRegistryService` acts as the directory service for all project workspaces.

### Registry Schema

```sql
-- Node metadata catalog
CREATE TABLE projects (
    project_id    TEXT PRIMARY KEY,
    name          TEXT NOT NULL UNIQUE,
    data          TEXT NOT NULL DEFAULT '{}'
);

CREATE INDEX idx_projects_name ON projects(name COLLATE NOCASE);

-- Active project coordinator
CREATE TABLE project_state (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
```

### Seeding Canonical Projects
AI OS automatically registers and boots 7 core projects:
1. **AI OS** — Software core engine
2. **Agency** — Freelance business CRM & operations
3. **CampusConnect** — Software social network project
4. **College** — Academic education tasks
5. **Research** — Experiments and benchmark evaluations
6. **Hackathons** — Competitive prototypes
7. **Portfolio** — Showcase websites

---

## 2. Dynamic Context & Isolation

When switching projects via `aios project switch <name>`:
- The active context is updated in the SQLite `project_context_state` table.
- A clean `ProjectRuntimeContext` is instantiated, parsing active Git branches, Notion workspace databases, and open tasks.
- Preferred models are registered to the router so subsequent agent actions are dispatched to optimized models (e.g., DeepSeek Coder for AI OS, DeepSeek R1 for Research).

---

## 3. Project Memory Scoping

The `ProjectMemoryService` provides separate knowledge retrieval lanes for each workspace:

```sql
CREATE TABLE project_memory (
    entry_id    TEXT PRIMARY KEY,
    project_id  TEXT NOT NULL,
    category    TEXT NOT NULL, -- conversations, decisions, meetings, etc.
    title       TEXT NOT NULL,
    content     TEXT NOT NULL DEFAULT '',
    tags        TEXT NOT NULL DEFAULT '[]',
    created_at  REAL NOT NULL,
    updated_at  REAL NOT NULL
);
CREATE INDEX idx_pmem_project ON project_memory(project_id);
```

---

## 4. Knowledge Graph Bridge

The `ProjectGraphBridge` links project creation and mutations back to the Phase 4.5 Universal Knowledge Graph:
- Project profiles are auto-linked as `EntityType.PROJECT`.
- Repository directories are linked via `BELONGS_TO`.
- High-level queries like `aios project graph` construct dynamic subgraphs.
- Cross-project shared dependencies (e.g., discovering multiple projects sharing database endpoints like Postgres/Supabase or using local models like Ollama) are resolved via the bridge's analytical queries.

---

## 5. Unified Command Reference

Phase 5 introduces the `aios project` CLI group:

```bash
aios projects                       # List all projects
aios project list                   # List all projects (alias)
aios project create <name> <type>   # Create a project profile
aios project switch <name>          # Switch active context and models
aios project status                 # Quick overview of active project
aios project dashboard              # Full rich health dashboard
aios project graph                  # Display connected nodes
aios project memory                 # Retrieve and append to memory
aios project models                 # View preferred model routing profiles
aios project cross [cmd]            # Cross-project queries
```
