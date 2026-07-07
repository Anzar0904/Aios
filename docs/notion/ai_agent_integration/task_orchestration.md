# Notion Intelligence — Task Orchestration
**Sprint 9 · Milestone 6** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define goal decomposition, task orchestration sequences, local tool executions, and ticket status update triggers.
* **Scope**: Governs Python task managers, agent task registers, and shell pipeline executors.
* **Audience**: Backend Developers, Integration Engineers, and System Architects.
* **Related Documents**:
  * [notion/ai_agent_integration/project_intelligence.md](file:///Users/anzarakhtar/aios/docs/notion/ai_agent_integration/project_intelligence.md) - Project tracking ticket boards.
  * [docs/15_SYSTEM_DESIGN.md](file:///Users/anzarakhtar/aios/docs/15_SYSTEM_DESIGN.md) - System-wide task flow sequences.

---

## 1. Goal Decomposition & Orchestration

The **Task Executor** decomposes objectives fetched from Notion databases into executable local shell commands and tool calls. 

The execution lifecycle updates task card statuses on Notion as steps complete.

```
 [Read Tasks DB: Get 'Ready' Ticket]
                  |
                  v
 [Task Executor: Decompose Objective] ===> Generate planned step lists
                  |
                  v
 [Update Status: "In Progress" on Notion]
                  |
                  v
 [Execute planned steps locally] ===> Runs compile, lint, test commands
                 / \
             Fail   Success
             /       \
            v         v
 [Update Status:      [Update Status: "Done" on Notion]
  "Blocked" on Notion]
```

---

## 2. Python Task Orchestrator Interface

The orchestrator logic lives under `aios.providers.notion.automation.orchestrator`:

```python
from typing import Dict, Any, List

class NotionTaskOrchestrator:
    def __init__(self, task_executor, database_service):
        self.task_executor = task_executor
        self.database_service = database_service

    def process_next_ticket(self, database_id: str) -> None:
        """Poll the database for 'Ready' tasks, decompose objectives, and run them."""
        tickets = self.database_service.query_tickets(
            database_id=database_id,
            filter={"property": "Status", "select": {"equals": "Ready"}}
        )
        if not tickets:
            return

        # Process the highest-priority ticket
        target_ticket = tickets[0]
        
        # Step 1: Update status to 'In Progress' on Notion
        self.database_service.update_status(target_ticket.ticket_id, "In Progress")
        
        # Step 2: Decompose task into steps and execute locally
        success = self.execute_task_pipeline(target_ticket)
        
        # Step 3: Update remote status based on execution results
        final_status = "Done" if success else "Blocked"
        self.database_service.update_status(target_ticket.ticket_id, final_status)

    def execute_task_pipeline(self, ticket: Any) -> bool:
        """Submit the task command sequence to the TaskExecutor and return completion status."""
        try:
            # Dispatch command pipeline run to the TaskExecutor
            run_id = self.task_executor.execute_command(
                command=ticket.values.get("Command", "make check"),
                timeout=600
            )
            return run_id.status == "SUCCESS"
        except Exception:
            return False
```
