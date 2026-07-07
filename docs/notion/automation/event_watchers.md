# Notion Intelligence — Event Watchers
**Sprint 9 · Milestone 5** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define Notion event polling watchers, n8n webhook listeners, and event structures.
* **Scope**: Governs event monitoring threads, API polling intervals, and webhook payload schemas.
* **Audience**: Integration Developers, DevOps Engineers, and System Architects.
* **Related Documents**:
  * [notion/automation/automation_engine.md](file:///Users/anzarakhtar/aios/docs/notion/automation/automation_engine.md) - Subsystem architecture.
  * [notion/capabilities.md](file:///Users/anzarakhtar/aios/docs/notion/capabilities.md) - Notion API capabilities.

---

## 1. Event Polling & Webhook Listeners

Because Notion integrations do not support native outbound webhooks directly without third-party services, the Personal AI OS uses a **Dual Event-Detection Pipeline**:

```
+-----------------------------------------------------------------------------------+
|                           EVENT DETECTION PIPELINE                                |
+------------------------+---------------------------------+------------------------+
| Pipeline               | Trigger Mechanism                | Target latency         |
+------------------------+---------------------------------+------------------------+
| n8n Webhook (Primary)  | An n8n workflow monitors Notion | Immediate (~2 seconds) |
|                        | changes and triggers an HTTP    |                        |
|                        | payload to the local AI OS port. |                        |
+------------------------+---------------------------------+------------------------+
| Local Poller (Fallback)| A background polling thread     | Configurable           |
|                        | queries the Notion Search API   | (default: 5 minutes)   |
|                        | for modified pages.             |                        |
+------------------------+---------------------------------+------------------------+
```

---

## 2. Event Types & Schemas

The system handles four primary event types:

### 2.1 `PAGE_CREATED`
* **Trigger**: A new page is created in a shared folder or workspace.
* **Payload**:
  ```json
  {
    "event_type": "PAGE_CREATED",
    "workspace_id": "8f8bca12-efd8-4ba3-bfd0-cd1712a4501a",
    "document_id": "notion_8f8bca12-efd8-4ba3-bfd0-cd1712a4501a",
    "details": {
      "title": "New Project Specs",
      "created_by": "c71a39f1-ef07-4bc2-af8b-59da10fa22b1"
    }
  }
  ```

### 2.2 `PAGE_UPDATED`
* **Trigger**: Block content inside a page is modified.
* **Payload**:
  ```json
  {
    "event_type": "PAGE_UPDATED",
    "workspace_id": "8f8bca12-efd8-4ba3-bfd0-cd1712a4501a",
    "document_id": "notion_8f8bca12-efd8-4ba3-bfd0-cd1712a4501a",
    "details": {
      "last_edited_by": "c71a39f1-ef07-4bc2-af8b-59da10fa22b1",
      "last_edited_time": "2026-07-06T18:49:00Z"
    }
  }
  ```

### 2.3 `DATABASE_ROW_UPDATED`
* **Trigger**: A database row value is updated (e.g. changing task status from `In Progress` to `Review`).
* **Payload**:
  ```json
  {
    "event_type": "DATABASE_ROW_UPDATED",
    "workspace_id": "8f8bca12-efd8-4ba3-bfd0-cd1712a4501a",
    "document_id": "notion_9a38c11a-0fd7-4bca-8eb1-59da10faaea1",
    "details": {
      "database_id": "d9fa12bc-e747-49d7-8e6f-54bf9e16bc82",
      "row_id": "8f8bca12-efd8-4ba3-bfd0-cd1712a4501a",
      "changed_properties": ["Status"]
    }
  }
  ```

### 2.4 `COMMENT_ADDED`
* **Trigger**: A comment thread is added to a page or block.
* **Payload**:
  ```json
  {
    "event_type": "COMMENT_ADDED",
    "workspace_id": "8f8bca12-efd8-4ba3-bfd0-cd1712a4501a",
    "document_id": "notion_8f8bca12-efd8-4ba3-bfd0-cd1712a4501a",
    "details": {
      "comment_id": "b838c01c-e747-49d7-8e6f-54bf9e16bc82",
      "author": "c71a39f1-ef07-4bc2-af8b-59da10fa22b1",
      "text": "Consensus approval completed."
    }
  }
  ```

---

## 3. Polling Thread Management
The fallback polling execution runs on a single background worker managed by the `MemoryService`'s loop. The scheduler monitors CPU workloads and pauses polling loops if CPU usage exceeds **85%** to conserve system resources.
