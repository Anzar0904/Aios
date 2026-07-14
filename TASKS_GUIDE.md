# Tasks Intelligence Guide

The Personal Tasks Registry monitors tasks categorizations, due dates, and statuses.

---

## 1. Database Schema

Stored in `aios.db`:

```sql
CREATE TABLE personal_tasks (
    task_id       TEXT PRIMARY KEY,
    title         TEXT NOT NULL,
    category      TEXT NOT NULL, -- personal|project|agency|research|learning
    priority      INTEGER NOT NULL DEFAULT 1,
    status        TEXT NOT NULL DEFAULT 'pending', -- pending|in_progress|completed
    due_date      TEXT,
    dependencies  TEXT NOT NULL DEFAULT '[]', -- JSON list
    context       TEXT NOT NULL DEFAULT '',
    created_at    REAL NOT NULL
);
```

---

## 2. CLI Management

```bash
# Browse tasks
aios personal tasks

# Register a new task
aios personal tasks create "Refactor core event loop" "project"

# Complete a task
aios personal tasks complete <task_id>
```
