# Research Registry Guide

The Research Registry manages research project configurations and metadata.

---

## 1. Database Schema

Stored in `~/.aios_research_intel.db` or unified `aios.db`:

```sql
CREATE TABLE research_projects (
    research_id       TEXT PRIMARY KEY,
    title             TEXT NOT NULL UNIQUE,
    category          TEXT NOT NULL, -- deep_learning|nlp|systems|agentic
    topic             TEXT NOT NULL,
    status            TEXT NOT NULL DEFAULT 'active',
    priority          INTEGER NOT NULL DEFAULT 1,
    owner             TEXT NOT NULL DEFAULT 'admin',
    created_at        REAL NOT NULL,
    updated_at        REAL NOT NULL,
    knowledge_sources TEXT NOT NULL DEFAULT '[]', -- JSON list
    project_ids       TEXT NOT NULL DEFAULT '[]'   -- JSON list
);
```

---

## 2. Seeded Research Projects

Upon setup, the registry seeds a default workspace project:
- **Agentic OS Architecture Research**: Researching context boundaries and multi-agent loops.

---

## 3. CLI Management

```bash
# List all active projects
aios research list
```
