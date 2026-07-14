# GitHub Actions Intelligence Guide

The CI Auditor monitors workflow builds, execution runs, status flags, and durations.

---

## 1. Database Schema

Stored in `~/.aios_github_intel.db`:

```sql
CREATE TABLE action_workflows (
    workflow_id     TEXT PRIMARY KEY,
    repository_id   TEXT NOT NULL,
    name            TEXT NOT NULL,
    status          TEXT NOT NULL DEFAULT 'success', -- success|failed|running
    duration_secs   INTEGER NOT NULL DEFAULT 0,
    timestamp       REAL NOT NULL
);
```

---

## 2. Capabilities

- **Failure Analysis**: Detects failed action run logs to flag build breakdowns.
- **Duration Auditing**: Tracks execution times to locate long-running build tasks.

---

## 3. CLI Management

```bash
# Browse GitHub Actions CI runs
aios github actions
```
