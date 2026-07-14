# Decision Log Guide

The Decision Log tracks architectural, model, and workflow design choices.

---

## 1. Decision Database Schema

Stored in `~/.aios_documentation.db`:

```sql
CREATE TABLE decisions (
    decision_id      TEXT PRIMARY KEY,
    title            TEXT NOT NULL,
    category         TEXT NOT NULL, -- architectural|technology|model|workflow|agency
    status           TEXT NOT NULL DEFAULT 'proposed', -- proposed|accepted|rejected
    context          TEXT NOT NULL DEFAULT '',
    consequences     TEXT NOT NULL DEFAULT '',
    owner            TEXT NOT NULL DEFAULT '',
    timestamp        REAL NOT NULL
);
```

---

## 2. Decision Log Flow

- Decisions are linked to the Knowledge Graph.
- Registered decisions represent system design targets and can be queried or linked to documentation updates.
