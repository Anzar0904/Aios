# Realtime, Migrations & Operations — Navigation Hub
**Sprint 12 · Milestone 5** · Version 1.0 · July 2026

---

> [!IMPORTANT]
> This directory houses the **Realtime, Migrations & Operations** specifications for the Personal AI OS.
> It builds upon the [Supabase Foundation](file:///Users/anzarakhtar/aios/docs/supabase/README.md), [Database Intelligence](file:///Users/anzarakhtar/aios/docs/supabase/database/README.md), [Security Intelligence](file:///Users/anzarakhtar/aios/docs/supabase/security/README.md), and [Platform Intelligence](file:///Users/anzarakhtar/aios/docs/supabase/platform/README.md) documents.
>
> In accordance with local-first system design guidelines, all realtime publications audits, migration dry-runs, backups inspections, alerting loops, and disaster recoveries are managed locally, keeping the AI OS kernel as the central director.

---

## Documents

| Document | Purpose |
|---|---|
| [realtime_intelligence.md](file:///Users/anzarakhtar/aios/docs/supabase/operations/realtime_intelligence.md) | Realtime publication channels, replication tables, and the Managed Resource state schema |
| [migration_orchestration.md](file:///Users/anzarakhtar/aios/docs/supabase/operations/migration_orchestration.md) | Migration ordering checkers, concurrent schema executions, and lock trackers |
| [database_operations.md](file:///Users/anzarakhtar/aios/docs/supabase/operations/database_operations.md) | Maintenance cron loops, database cleanups, and connection pool resets |
| [backup_restore.md](file:///Users/anzarakhtar/aios/docs/supabase/operations/backup_restore.md) | pg_dump configurations, verification scripts, WAL checks, and recovery testing |
| [monitoring_alerting.md](file:///Users/anzarakhtar/aios/docs/supabase/operations/monitoring_alerting.md) | CPU/RAM alarm thresholds, slow query loggers, and HTTP error alerts |
| [disaster_recovery.md](file:///Users/anzarakhtar/aios/docs/supabase/operations/disaster_recovery.md) | Failover check rules, replication standbys, and rollback sql scripts |
| [operational_health.md](file:///Users/anzarakhtar/aios/docs/supabase/operations/operational_health.md) | Index bloats, query lock diagnostics, and database repair actions |

---

## Reading Order

1. **[`realtime_intelligence.md`](file:///Users/anzarakhtar/aios/docs/supabase/operations/realtime_intelligence.md)** & **[`migration_orchestration.md`](file:///Users/anzarakhtar/aios/docs/supabase/operations/migration_orchestration.md)**: Start here to study Realtime and Migrations.
2. **[`database_operations.md`](file:///Users/anzarakhtar/aios/docs/supabase/operations/database_operations.md)** & **[`backup_restore.md`](file:///Users/anzarakhtar/aios/docs/supabase/operations/backup_restore.md)**: Explore maintenance and backup strategies.
3. **[`monitoring_alerting.md`](file:///Users/anzarakhtar/aios/docs/supabase/operations/monitoring_alerting.md)** & **[`disaster_recovery.md`](file:///Users/anzarakhtar/aios/docs/supabase/operations/disaster_recovery.md)**: Review alerts and disaster recovery failovers.
4. **[`operational_health.md`](file:///Users/anzarakhtar/aios/docs/supabase/operations/operational_health.md)**: Examine operational health checks and repair tasks.
