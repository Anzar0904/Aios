# Repository Registry Guide

The Repository Registry manages tracked GitHub repositories profiles and metadata.

---

## 1. Database Schema

Stored in `~/.aios_github_intel.db`:

```sql
CREATE TABLE repositories (
    repository_id   TEXT PRIMARY KEY,
    name            TEXT NOT NULL UNIQUE,
    owner           TEXT NOT NULL,
    description     TEXT NOT NULL DEFAULT '',
    visibility      TEXT NOT NULL DEFAULT 'public',
    default_branch  TEXT NOT NULL DEFAULT 'main',
    language        TEXT NOT NULL DEFAULT 'python',
    stars           INTEGER NOT NULL DEFAULT 0,
    forks           INTEGER NOT NULL DEFAULT 0,
    open_issues     INTEGER NOT NULL DEFAULT 0,
    open_prs        INTEGER NOT NULL DEFAULT 0,
    created_at      REAL NOT NULL,
    updated_at      REAL NOT NULL,
    health_score    INTEGER NOT NULL DEFAULT 100
);
```

---

## 2. Default Seeded Repositories

Upon database setup, the registry seeds:
- **Anzar0904/Aios**: Core repo containing local model adapters and command dispatchers.

---

## 3. CLI Management

```bash
# View list of registered repositories
aios github repos
```
