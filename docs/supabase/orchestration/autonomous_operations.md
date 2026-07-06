# Autonomous Operations & Background Maintenance Spec
**Sprint 12 · Milestone 6** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define background maintenance cron scheduling, backup validation, and query lock evictions.
* **Scope**: Governs backend crons, vacuum loops, and data repair scripts.
* **Audience**: DBAs, Backend Developers, and System Architects.
* **Related Documents**:
  * [supabase/operations/database_operations.md](file:///Users/anzarakhtar/aios/docs/supabase/operations/database_operations.md) - Database operations.
  * [supabase/operations/backup_restore.md](file:///Users/anzarakhtar/aios/docs/supabase/operations/backup_restore.md) - Backup and restore.

---

## 1. Background Operations Walkers

To maintain a healthy database, the AI OS runs background **Operations Walkers** during idle system periods:
* **Cron Walkers**: Scheduled tasks run `VACUUM ANALYZE [table_name]` once per week to clean up dead rows.
* **Index Rebuilders**: Periodically checks index fragmentation, triggering concurrent index rebuilds if fragmentation exceeds limits.
* **Backup Verifiers**: Restores backup snapshots to local containers once per week to verify backup integrity.

---

## 2. Automated Lock Evictions

When a connection lock is detected:
1. **Identify Lock**: Scans `pg_locks` to identify blocking write transactions.
2. **Track Duration**: Monitors the duration of the lock.
3. **Terminate Connection**: If the lock persists for **> 120 seconds**, the system terminates the connection (`pg_terminate_backend`) to prevent database hangs.
4. **Log Event**: Logs details to the database and alerts the developer.
