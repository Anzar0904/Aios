# Release Intelligence Guide

The Release Intelligence Service tracks versions, tags, features, and assets.

---

## 1. Database Schema

Stored in `~/.aios_github_intel.db`:

```sql
CREATE TABLE releases (
    release_id      TEXT PRIMARY KEY,
    repository_id   TEXT NOT NULL,
    version         TEXT NOT NULL UNIQUE, -- e.g. v1.0.0
    title           TEXT NOT NULL,
    features        TEXT NOT NULL DEFAULT '[]', -- JSON list
    fixes           TEXT NOT NULL DEFAULT '[]', -- JSON list
    timestamp       REAL NOT NULL
);
```

---

## 2. Capabilities

- **Release Summaries**: Compiles features log checklists and bug fixes.
- **Release Verification**: Asserts that default branches match target release tags.

---

## 3. CLI Management

```bash
# View list of releases
aios github releases
```
