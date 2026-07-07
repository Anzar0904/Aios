# Notion Intelligence — Workflow Execution
**Sprint 9 · Milestone 5** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define workflow execution paths, trigger rules, and integration pipelines with the Task Executor.
* **Scope**: Governs Python workflow execution managers, task dispatchers, and REPL shell scripts.
* **Audience**: Backend Developers, Integration Engineers, and System Architects.
* **Related Documents**:
  * [notion/automation/event_watchers.md](file:///Users/anzarakhtar/aios/docs/notion/automation/event_watchers.md) - Event payloads structure.
  * [docs/15_SYSTEM_DESIGN.md](file:///Users/anzarakhtar/aios/docs/15_SYSTEM_DESIGN.md) - System-wide task flow sequences.

---

## 1. Workflow Orchestration

When a Notion event matches a configured trigger, the system launches a local workflow. The **`NotionWorkflowManager`** coordinates this process, converting incoming events into execution pipelines run by the local **`TaskExecutor`** service.

```
 [Notion Event Watcher]  =====> Emits event: PAGE_UPDATED
           |
           v
 [NotionWorkflowManager] ===> Matches trigger rule: "run_test_suite_on_page_update"
           |
           v
 [Build Action Sequence] ===> Compiles tasks (Get Page, Check Code, Run Pytest)
           |
           v
 [TaskExecutor Service]  =====> Executes tasks in a local sandbox process
           |
           v
 [Write Execution Log]   =====> Publishes execution report to Notion database row
```

---

## 2. Trigger Rule Schema

Workflow trigger configurations are defined in the local sqlite database or `config/notion_workflows.toml`:

```toml
[[workflows]]
name = "Run Local Code Compiler"
trigger_event = "PAGE_UPDATED"
filter_page_id = "8f8bca12-efd8-4ba3-bfd0-cd1712a4501a"
action_type = "SHELL_TASK"
script = "make compile"
timeout_seconds = 300

[[workflows]]
name = "Sync Project Status"
trigger_event = "DATABASE_ROW_UPDATED"
filter_database_id = "d9fa12bc-e747-49d7-8e6f-54bf9e16bc82"
filter_properties = ["Status"]
action_type = "PYTHON_SERVICE"
service_name = "ApprovalEngineService"
method = "evaluate_transition_status"
```

---

## 3. Sequence Execution Flow

When executing a `SHELL_TASK` or `PYTHON_SERVICE` action:
1. **Context Assembly**: The workflow manager builds a context payload from the triggering event, including page metadata, modified block content, and the initiating user.
2. **Pre-Execution Check**: Ensure the script path falls within the system's safe directories (checked against path traversal rules in [05_SECURITY_GUIDELINES.md](file:///Users/anzarakhtar/aios/docs/05_SECURITY_GUIDELINES.md)).
3. **Task Dispatch**: The sequence is sent to the `TaskExecutor`'s async worker:
   ```python
   # Dispatch execution tasks to the system runner
   task_id = task_executor.dispatch_task(
       name=workflow.name,
       command=workflow.script,
       env={"NOTION_TRIGGER_PAGE_ID": event.document_id},
       risk_category="MEDIUM"
   )
   ```
4. **Post-Execution Log**: The task execution result (success/failure details, runtime logs) is written to a designated sync-log table and optionally appended as a comment on the source Notion page.
