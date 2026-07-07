# Notion Intelligence — Notification Pipeline
**Sprint 9 · Milestone 5** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define user alert routing, local REPL notification logs, and Notion page notification comments.
* **Scope**: Governs notification publishers, REPL console outputs, and remote comment managers.
* **Audience**: Backend Developers, Integration Engineers, and System Architects.
* **Related Documents**:
  * [notion/capabilities.md](file:///Users/anzarakhtar/aios/docs/notion/capabilities.md) - Comment capabilities.
  * [notion/automation_engine.md](file:///Users/anzarakhtar/aios/docs/notion/automation/automation_engine.md) - Event dispatcher rules.

---

## 1. Notification Architecture

To keep the user informed of background sync results, workflow completions, and conflicts, the Notion module routes alerts through a **Multi-Channel Notification Pipeline**:

```
        [Notion Event / Workflow Result]
                       |
                       v
         [NotionNotificationDispatcher]
         /             |              \
        v              v               v
  [Local REPL]    [Local Log]    [Notion Page]
  Console popup   System audit   Inline comment
```

---

## 2. Notification Channels

### 2.1 Local REPL Console
* **Format**: Formatted Markdown messages printed directly to the active REPL shell interface.
* **Alert Levels**:
  * **`INFO`**: Standard sync success logs.
  * **`WARNING`**: Non-critical issues (e.g. API rate limit retries, minor schema drifts).
  * **`CRITICAL`**: Sync failures requiring user action (e.g. token expired, database conflict).

### 2.2 Local Security & System Logs
* Logs are written directly to `logs/notion_sync.log` and `logs/notion_security_audit.log`.

### 2.3 Remote Notion Page Notifications
* **Use Case**: Used by automated services (e.g. code review engines, approval managers) to post execution updates directly to the relevant Notion page.
* **Execution**: The `NotionNotificationDispatcher` writes comments using the page comments API (see [notion/data_model/comment_model.md](file:///Users/anzarakhtar/aios/docs/notion/data_model/comment_model.md)):
  ```json
  {
    "parent": {
      "page_id": "8f8bca12-efd8-4ba3-bfd0-cd1712a4501a"
    },
    "rich_text": [
      {
        "text": {
          "content": "[AI OS Alert] Automated validation run succeeded.\n- Pytest: Passed (14 tests)\n- Lint check: Passed"
        }
      }
    ]
  }
  ```

---

## 3. Configuration & Silencing Rules

To prevent alert fatigue, the user can configure notification settings in `config/config.toml`:

```toml
[providers.notion.notifications]
enable_console_popups = true
enable_notion_comments = true
silence_level = "WARNING" # Ignore INFO logs

# Quiet Hours (Local Time bounds)
quiet_hours_start = "22:00"
quiet_hours_end = "08:00"
```

* **Quiet Hours**: During quiet hours, `INFO` and `WARNING` notifications are queued locally and displayed when the quiet hours window ends. `CRITICAL` alerts (e.g. authorization failures) bypass quiet hours and are displayed immediately.
