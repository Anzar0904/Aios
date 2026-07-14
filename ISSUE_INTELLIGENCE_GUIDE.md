# Issue Intelligence Guide

The Issue Registry tracks bug reports, feature requests, priority levels, and labels.

---

## 1. Database Schema

Stored in `~/.aios_github_intel.db`:

```sql
CREATE TABLE issues (
    issue_id        TEXT PRIMARY KEY,
    repository_id   TEXT NOT NULL,
    title           TEXT NOT NULL,
    priority        INTEGER NOT NULL DEFAULT 1, -- 1 to 5 scale
    status          TEXT NOT NULL DEFAULT 'open',
    assignee        TEXT NOT NULL DEFAULT '',
    labels          TEXT NOT NULL DEFAULT '[]', -- JSON string list
    created_at      REAL NOT NULL
);
```

---

## 2. Priority Levels

- **Priority 5**: Blocker issues impacting system boots or core loop transactions.
- **Priority 3**: Functional defects impacting specific CLI subcommands.
- **Priority 1**: Non-blocking improvements or documentation updates.

---

## 3. CLI Management

```bash
# View open issues priorities
aios github issues
```
