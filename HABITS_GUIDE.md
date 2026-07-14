# Habits Intelligence Guide

The Habit Tracker tracks streaks consistency, success rates, and scores.

---

## 1. Database Schema

Stored in `aios.db`:

```sql
CREATE TABLE habits (
    habit_id          TEXT PRIMARY KEY,
    name              TEXT NOT NULL UNIQUE,
    frequency         TEXT NOT NULL, -- daily|weekly
    streak            INTEGER NOT NULL DEFAULT 0,
    success_rate      REAL NOT NULL DEFAULT 100.0,
    consistency_score REAL NOT NULL DEFAULT 100.0
);
```

---

## 2. Streak Calculations

Streak counts increment consecutively each time a habit is checked off:
- **Consistency Score**: Evaluated based on historical compliance.

---

## 3. CLI Management

```bash
# Browse habit metrics
aios personal habits

# Increment streak
aios personal habits check <habit_id>
```
