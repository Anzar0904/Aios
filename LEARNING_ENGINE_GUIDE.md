# Learning Engine Guide

The Learning Engine processes and structures historical research iterations to build long-term intelligence.

---

## 1. Summaries Database Schema

```sql
CREATE TABLE learning_summaries (
    summary_id          TEXT PRIMARY KEY,
    research_id         TEXT NOT NULL,
    topics              TEXT NOT NULL DEFAULT '[]', -- JSON list
    successful_findings TEXT NOT NULL DEFAULT '[]', -- JSON list
    failed_experiments  TEXT NOT NULL DEFAULT '[]', -- JSON list
    lessons_learned     TEXT NOT NULL DEFAULT '',
    timestamp           REAL NOT NULL
);
```

---

## 2. Capabilities

- **Success Tracking**: Logs configurations that worked (e.g. SQLite WAL journal).
- **Failure Audits**: Tracks failed runs to prevent duplicate mistakes.

---

## 3. CLI Management

```bash
# Display lessons learned summary logs
aios research learn
```
