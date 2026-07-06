# Schema Planning & Rollback Spec
**Sprint 12 · Milestone 6** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define DAG planner generation, lock failovers, and rollback planning rules for database tasks.
* **Scope**: Governs execution step graphs, transaction checks, and rollback triggers.
* **Audience**: AI Prompt Engineers, Integration Engineers, and Quality Auditors.
* **Related Documents**:
  * [supabase/operations/migration_orchestration.md](file:///Users/anzarakhtar/aios/docs/supabase/operations/migration_orchestration.md) - Migration orchestration.
  * [supabase/operations/disaster_recovery.md](file:///Users/anzarakhtar/aios/docs/supabase/operations/disaster_recovery.md) - Disaster recovery.

---

## 1. DAG Schema Planner

The **Schema Planner** converts database updates into a Directed Acyclic Graph (DAG) of task steps ($G_{plan} = (V_{steps}, E_{dependencies})$):

```
       [Step 1: Fetch remote database schema]
                        |
                        v
        [Step 2: Generate DDL schema diff]
                        |
                        v
      [Step 3: Write migration SQL script]
                        |
                        v
     [Step 4: Dry-run locally in container]
         /             \
    (Success)        (Failure)
       /                 \
      v                   v
[Step 5: Apply remote]   [Step 6: Reprocess Schema] ===> Link back to Step 2
```

* **Nodes ($V_{steps}$)**: Custom tool executions (e.g. `ExecuteDiff`, `WriteSQL`, `RunDryRun`, `ApplyMigration`).
* **Dependencies ($E_{dependencies}$)**: Execution orders (e.g. Step 4 cannot run until Step 3 completes).

---

## 2. Lock Failovers & Rollback Loops

When a step fails (e.g. hitting a write lock or constraint violation):
1. **Analyze Failure**: The planner captures stderr outputs, transaction status, and connection logs.
2. **Execute Failover**:
   * If a write lock exists: Pauses execution and schedules a retry.
   * If a constraint violation occurs: Rolls back the transaction, returns the database to its previous schema state, and alerts the developer.
3. **Mutate DAG**: Updates the execution graph to continue the task.
