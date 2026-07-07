# Notion Intelligence — Project Intelligence Integration
**Sprint 9 · Milestone 6** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define the project intelligence dashboard layouts, ticket mappings, milestone databases, and workload calculations.
* **Scope**: Governs Python project manager tools, status transition monitors, and progress builders.
* **Audience**: Product Managers, Systems Engineers, and AI developers.
* **Related Documents**:
  * [notion/data_model/database_model.md](file:///Users/anzarakhtar/aios/docs/notion/data_model/database_model.md) - Database row mappings.
  * [notion/capabilities.md](file:///Users/anzarakhtar/aios/docs/notion/capabilities.md) - Database capabilities.

---

## 1. Project Management Database Mappings

The **Project Intelligence** module translates database boards inside Notion into active project scopes. 

The AI OS uses three core databases to coordinate development tasks:

```
                  +-----------------------------------+
                  |         Milestones DB             | (Epics, Sprint Goals)
                  +-----------------------------------+
                                    | (1-to-Many Relation)
                                    v
                  +-----------------------------------+
                  |           Tasks DB                | (Tickets, To-Do items)
                  +-----------------------------------+
                                    | (Relation to Profile ID)
                                    v
                  +-----------------------------------+
                  |         Workload Allocation       | (Checked against profile stats)
                  +-----------------------------------+
```

---

## 2. Task Ticket Schema Mapping

When querying the Tasks DB, the database rows are mapped to Python **`TaskTicket`** instances:

```python
@dataclass
class TaskTicket:
    ticket_id: str
    title: str
    status: str  # 'Backlog', 'Ready', 'In Progress', 'Blocked', 'Done'
    priority: str  # 'P0', 'P1', 'P2'
    assignee_profile_id: str
    estimate_hours: float
    milestone_id: Optional[str] = None
    due_date: Optional[datetime] = None

    def is_overdue(self) -> bool:
        """Check if the task has exceeded its due date without completion."""
        if not self.due_date:
            return False
        return self.status != "Done" and datetime.utcnow() > self.due_date
```

---

## 3. Workload Calculations & Profile Integrations

To help with sprint planning:
1. **Fetch Workloads**: The OS queries the Tasks database for all open tickets assigned to the user:
   ```python
   # Query database for incomplete tasks assigned to the user profile
   assigned_tickets = database_service.query_tickets(
       filter={
           "and": [
               {"property": "Assignee", "people": {"contains": assignee_id}},
               {"property": "Status", "select": {"does_not_equal": "Done"}}
           ]
       }
   )
   ```
2. **Sum Estimates**: Sum the `estimate_hours` for all retrieved tickets.
3. **Compare Capacity**: Retrieve the user's weekly working hours constraint from the local `personal_profiles.json` registry.
4. **Warn Overload**: If the estimated workload exceeds the user's weekly capacity limit, the OS displays a warning in the REPL console:
   ```
   [Project Intelligence Warning]
   Assigned tasks in Sprint 9 total 45 hours, exceeding weekly capacity (40 hours).
   Please reschedule low-priority tickets.
   ```
