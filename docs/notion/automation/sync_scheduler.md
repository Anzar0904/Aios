# Notion Intelligence — Synchronization Scheduler
**Sprint 9 · Milestone 5** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define synchronization scheduler intervals, cron jobs, network checks, throttling, and resource constraint rules.
* **Scope**: Governs Python sync loops, scheduler databases, and resource throttle policies.
* **Audience**: Backend Developers, Integration Engineers, and Systems Operators.
* **Related Documents**:
  * [notion/integration_strategy.md](file:///Users/anzarakhtar/aios/docs/notion/integration_strategy.md) - General sync strategies.
  * [docs/20_OPERATIONS_MANUAL.md](file:///Users/anzarakhtar/aios/docs/20_OPERATIONS_MANUAL.md) - Core scheduler rules.

---

## 1. Sync Scheduler Architecture

Relational caches, vector embeddings, and task boards must remain in sync with Notion. The scheduling layer manages periodic background checks to update local databases without blocking user commands.

Sync schedules are managed by the **`NotionSyncScheduler`** service, which runs under the `MemoryService` daemon.

---

## 2. Sync Profiles & Intervals

The system defines three sync profiles based on user activity and battery/network constraints:

```
+------------------+------------------------+---------------------------------------+
| Sync Profile     | Sync Interval          | Target Use Case                       |
+------------------+------------------------+---------------------------------------+
| Active           | Every 15 Minutes       | Workspace is active and the system is |
|                  |                        | connected to AC power.                |
+------------------+------------------------+---------------------------------------+
| Standard         | Every 60 Minutes       | Default background interval.          |
+------------------+------------------------+---------------------------------------+
| Battery-Saver    | Every 240 Minutes      | System is running on battery power.   |
+------------------+------------------------+---------------------------------------+
```

### Scheduler Database Table
Schedules are tracked inside the local SQLite database:
```sql
CREATE TABLE IF NOT EXISTS notion_scheduler_states (
    workspace_id TEXT PRIMARY KEY,
    sync_profile TEXT CHECK(sync_profile IN ('ACTIVE', 'STANDARD', 'BATTERY_SAVER')) NOT NULL,
    next_run_at TIMESTAMP NOT NULL,
    last_run_started_at TIMESTAMP,
    last_run_completed_at TIMESTAMP,
    last_run_status TEXT CHECK(last_run_status IN ('SUCCESS', 'FAILED', 'SKIPPED')) NOT NULL
);
```

---

## 3. Resource & Network Constraints

To ensure smooth local operations, the scheduler runs a validation checklist before starting a sync cycle:

```
  [Trigger Scheduled Sync]
              |
      [Is Network Active?]
             / \
           No   Yes
           /     \
          v       v
      [Skip]   [Is CPU Load < 80%?]
                 / \
               No   Yes
               /     \
              v       v
          [Delay]  [Is System in battery-saver mode?]
                     / \
                   Yes  No
                   /     \
                  v       v
    [Switch profile to]  [Execute Sync Cycle]
       [BATTERY_SAVER]
```

### Throttling Rules
* **API Jitter**: Outgoing calls are throttled using a token-bucket rate limiter that restricts API calls to **2 requests per second** (below Notion's 3 requests/sec limit) to accommodate other active services.
* **Batch Limits**: Sync cycles pull a maximum of **50 modified pages** per run. Remaining updates are queued and processed in the next scheduled cycle to prevent long-running tasks from locking local database caches.
