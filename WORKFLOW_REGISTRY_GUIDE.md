# Workflow Registry Guide

The Workflow Registry Service acts as the centralized catalog of all automations running in the AI OS.

---

## 1. Database Schema

All workflow information is stored in `~/.aios_workflows.db`. Here are the schema definitions:

```sql
CREATE TABLE workflows (
    workflow_id      TEXT PRIMARY KEY,
    name             TEXT NOT NULL UNIQUE,
    description      TEXT NOT NULL DEFAULT '',
    version          INTEGER NOT NULL DEFAULT 1,
    project_id       TEXT NOT NULL DEFAULT '',
    client_id        TEXT NOT NULL DEFAULT '',
    status           TEXT NOT NULL DEFAULT 'inactive',
    owner            TEXT NOT NULL DEFAULT '',
    webhook_url      TEXT NOT NULL DEFAULT '',
    execution_url    TEXT NOT NULL DEFAULT '',
    deployment_date  REAL NOT NULL,
    last_execution   REAL NOT NULL DEFAULT 0.0,
    health_score     INTEGER NOT NULL DEFAULT 100,
    nodes            TEXT NOT NULL DEFAULT '[]',
    connections      TEXT NOT NULL DEFAULT '{}'
);

CREATE TABLE deployments (
    deployment_id    TEXT PRIMARY KEY,
    workflow_id      TEXT NOT NULL,
    version          INTEGER NOT NULL,
    status           TEXT NOT NULL DEFAULT 'success',
    deployed_by      TEXT NOT NULL DEFAULT '',
    changelog        TEXT NOT NULL DEFAULT '',
    nodes_count      INTEGER NOT NULL DEFAULT 0,
    triggers_count   INTEGER NOT NULL DEFAULT 0,
    raw_json         TEXT NOT NULL DEFAULT '',
    timestamp        REAL NOT NULL
);
```

---

## 2. Template Catalog

The registry seeds default template configurations for quick deployment:

- **Lead Generation System**: Periodically runs web scraping and logs outputs to Notion.
- **Cold Outreach Flow**: Detects CRM updates and dispatches emails via Gmail node.
- **CRM Sync Pipeline**: Keeps Notion databases and Google Sheets aligned.
- **GitHub Automation**: Receives repo webhooks and triggers CI status reports on Slack.

---

## 3. CLI Management

```bash
# View list of registered workflows
aios workflows

# View details of a specific template
aios workflow generate
```
