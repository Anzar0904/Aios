# Connector Registry Guide

The Connector Registry tracks configuration metadata for third-party adapters registered in the AI OS.

---

## 1. Registry Database Schema

Seeded in `~/.aios_integrations.db`:

```sql
CREATE TABLE connectors (
    connector_id    TEXT PRIMARY KEY,
    name            TEXT NOT NULL UNIQUE,
    version         TEXT NOT NULL,
    provider        TEXT NOT NULL, -- github|notion|n8n|supabase etc.
    status          TEXT NOT NULL DEFAULT 'disconnected',
    capabilities    TEXT NOT NULL DEFAULT '[]', -- JSON list
    auth_type       TEXT NOT NULL DEFAULT 'none',
    health_score    INTEGER NOT NULL DEFAULT 100,
    last_sync       REAL NOT NULL DEFAULT 0.0,
    project_ids     TEXT NOT NULL DEFAULT '[]' -- JSON list
);
```

---

## 2. Seeded Connectors

By default, 9 core connectors are registered:
1. **github**: PR, issue, and code repository monitors.
2. **notion**: Page creation, task sync, goal tracking.
3. **n8n**: Workflow deployment, health auditing.
4. **supabase**: Postgres project tables, migrations.
5. **gmail**: Mail inbox and label triggers.
6. **calendar**: Meeting event discovery and schedules.
7. **slack**: Channel message monitoring.
8. **discord**: Server channel alert logs.
9. **telegram**: Bot message alerts.

---

## 3. CLI Management

```bash
# Display connector profiles
aios integrations list
```
