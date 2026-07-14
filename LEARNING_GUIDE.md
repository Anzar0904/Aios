# Learning Intelligence Guide

The Learning Tracker manages courses, book checklists, and skill acquisition items.

---

## 1. Database Schema

Stored in `aios.db`:

```sql
CREATE TABLE personal_learning_items (
    item_id       TEXT PRIMARY KEY,
    title         TEXT NOT NULL,
    item_type     TEXT NOT NULL, -- course|book|paper|skill|certification
    progress      REAL NOT NULL DEFAULT 0.0,
    status        TEXT NOT NULL DEFAULT 'pending'
);
```

---

## 2. CLI Management

```bash
# Browse learning objectives
aios personal learning

# Add a learning course
aios personal learning create "Advanced ML Parameters" "course"
```
