# Database Operations & Maintenance Spec
**Sprint 12 · Milestone 5** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define database maintenance cron parameters, vacuum rules, and clean-up tasks.
* **Scope**: Governs cron setups, table vacuums, and database cleans.
* **Audience**: Systems Engineers, DBAs, and Lead Developers.
* **Related Documents**:
  * [supabase/database/database_health.md](file:///Users/anzarakhtar/aios/docs/supabase/database/database_health.md) - Database health.
  * [supabase/operations/realtime_intelligence.md](file:///Users/anzarakhtar/aios/docs/supabase/operations/realtime_intelligence.md) - State abstraction.

---

## 1. Maintenance Cron Tasks

The **Database Operations** module runs background maintenance tasks to optimize performance:
* **Table Vacuums**: Schedules `VACUUM ANALYZE [table_name]` during low-traffic periods to clean up dead rows and update query statistics.
* **Index Rebuilding**: Schedules concurrent index rebuilding (`REINDEX CONCURRENTLY [index_name]`) if index fragmentation exceeds **30%**.
* **Connection Pool Resets**: Monitors pool usage, issuing reset commands if connection limits are approached.
* **Diagnostics Logging**: Logs operational metrics to SQLite, updating the health dashboard.
