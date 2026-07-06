# Migration Orchestration Spec
**Sprint 12 · Milestone 5** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define migration execution pipelines, transactional locks tracking, and schema validation.
* **Scope**: Governs migration steps, locks verifiers, and execution orders.
* **Audience**: DBAs, Systems Architects, and Lead Developers.
* **Related Documents**:
  * [supabase/database/migration_analysis.md](file:///Users/anzarakhtar/aios/docs/supabase/database/migration_analysis.md) - Migration analysis.
  * [supabase/operations/realtime_intelligence.md](file:///Users/anzarakhtar/aios/docs/supabase/operations/realtime_intelligence.md) - State abstraction.

---

## 1. Migration Execution Pipeline

The migration engine orchestrates updates using a structured pipeline:
* **Ordering Checks**: Verifies that migration files follow timestamp sequences, preventing out-of-order schema applications.
* **Lock Trackers**: Inspects `pg_locks` before execution. If a table has active write locks, the system pauses the migration to prevent transaction locks.
* **Execution Engine**: Executes migration scripts inside single transaction blocks, rolling back changes if errors occur.
* **Approval Gates Integration**: High-risk DDL queries (e.g. dropping columns, modifying tables) require developer confirmation before running.
