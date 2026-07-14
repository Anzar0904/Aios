# Goals Intelligence Guide

The Goals Registry tracks short-term and long-term personal targets.

---

## 1. Database Schema

Stored in `aios.db`:

```sql
CREATE TABLE personal_goals (
    goal_id       TEXT PRIMARY KEY,
    title         TEXT NOT NULL,
    timeframe     TEXT NOT NULL, -- annual|quarterly|monthly|weekly|daily
    category      TEXT NOT NULL, -- career|agency|projects|research|learning|finance|health|personal
    priority      INTEGER NOT NULL DEFAULT 1,
    status        TEXT NOT NULL DEFAULT 'pending', -- pending|in_progress|achieved|failed
    progress      REAL NOT NULL DEFAULT 0.0,
    dependencies  TEXT NOT NULL DEFAULT '[]', -- JSON string list
    created_at    REAL NOT NULL,
    target_date   TEXT
);
```

---

## 2. CLI Management

```bash
# View list of active goals
aios personal goals

# Create a new goal
aios personal goals create "Read 10 Books" "annual" "personal"

# Mark a goal as achieved
aios personal goals achieve <goal_id>
```
