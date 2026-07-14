# n8n Integration Guide

This guide describes how to configure, version, and link n8n workflows within the AI OS.

---

## 1. n8n Node Configurations

The AI OS maps workflows as JSON structures. For example:

```json
{
  "nodes": [
    {
      "name": "Cron Trigger",
      "type": "n8n-nodes-base.cron",
      "parameters": {
        "rule": "*/5 * * * *"
      }
    },
    {
      "name": "HTTP Request",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "http://localhost:8000/api/v1/context"
      }
    }
  ],
  "connections": {
    "Cron Trigger": {
      "main": [
        [
          {
            "node": "HTTP Request",
            "type": "main",
            "index": 0
          }
        ]
      ]
    }
  }
}
```

---

## 2. Version Control & Rollbacks

- Every deployment logs nodes configuration payloads and increments the version counter in the database.
- Rollbacks are supported via:
  `aios workflow rollback <workflow_id> <version>`
- Reverting rolls back node lists and triggers back to the target version state.

---

## 3. Knowledge Graph Linkages

- Workflows are linked to **Projects** via `BELONGS_TO`.
- Workflows are linked to **Clients** via `SERVES`.
- Trigger webhooks are registered as `webhook` nodes connected to `workflow` nodes via `SERVES`.
- Successful runs register `execution` nodes connected to the parent workflow via `EXECUTES`.
