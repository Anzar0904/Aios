# Calendar Intelligence Guide

The Calendar Engine tracks events schedules and analyzes them to detect execution time overrides.

---

## 1. Database Schema

Stored in `aios.db`:

```sql
CREATE TABLE calendar_events (
    event_id      TEXT PRIMARY KEY,
    title         TEXT NOT NULL,
    start_time    REAL NOT NULL,
    end_time      REAL NOT NULL,
    category      TEXT NOT NULL, -- meeting|hackathon|class|agency_call|research_session
    priority      INTEGER NOT NULL DEFAULT 1,
    description   TEXT NOT NULL DEFAULT ''
);
```

---

## 2. Overlap Conflict Detection

When multiple events overlap in execution time:
$$\max(e_1.\text{start}, e_2.\text{start}) < \min(e_1.\text{end}, e_2.\text{end})$$
The system automatically logs an overlap warning and notifies the user during calendar reviews.

---

## 3. CLI Management

```bash
# View calendar schedule
aios personal calendar

# Create a calendar event (offset parameters specify time offset in seconds)
aios personal calendar create "Design Standup" 0 3600 "meeting"
```
