# Database Health & Performance Diagnostics Spec
**Sprint 12 · Milestone 2** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define database performance checks, index bloat queries, lock checks, and repair routines.
* **Scope**: Governs database diagnostics, locks caches, and clean-up tasks.
* **Audience**: DBAs, Systems Engineers, and Lead Developers.
* **Related Documents**:
  * [supabase/capabilities.md](file:///Users/anzarakhtar/aios/docs/supabase/capabilities.md) - Capabilities matrix.
  * [supabase/database/database_health.md](file:///Users/anzarakhtar/aios/docs/supabase/database/database_health.md) - This file.

---

## 1. Database Health Indicators

The **Database Health** module runs background checks on Supabase database instances to monitor performance:

```
+------------------------------------+------------------------------------+----------+
| Health Indicator                   | Target Range                       | Priority |
+------------------------------------+------------------------------------+----------+
| 1. Database Cache Hit Ratio        | > 99% hit ratio                    | High     |
+------------------------------------+------------------------------------+----------+
| 2. Index Bloat Estimation          | < 20% bloat ratio                  | Medium   |
+------------------------------------+------------------------------------+----------+
| 3. Active Locks Count              | 0 active write locks blockings     | High     |
+------------------------------------+------------------------------------+----------+
| 4. Disk Space Utilization          | < 80% capacity                     | High     |
+------------------------------------+------------------------------------+----------+
```

---

## 2. Performance Diagnostics Queries

* **Cache Hit Ratio**:
  ```sql
  SELECT sum(heap_blks_read) AS heap_read, sum(heap_blks_hit) AS heap_hit,
         sum(heap_blks_hit) / (sum(heap_blks_hit) + sum(heap_blks_read))::float AS hit_ratio
  FROM pg_statio_user_tables;
  ```
* **Index Bloat Estimation**: Queries table statistics to identify indexes consuming excessive disk space relative to table row counts.
* **Active Locks Finder**: Identifies blocked queries by scanning `pg_locks` and `pg_stat_activity`.

---

## 3. Maintenance & Reindexing Loops

If health checks fail (e.g. index bloat exceeds 30%):
1. **Re-indexing**: Appends a reindexing task (`REINDEX CONCURRENTLY [index_name]`) to the executor queue.
2. **Vacuum Cleaning**: Schedules `VACUUM ANALYZE [table_name]` to clean up dead rows and update query statistics.
3. **Locks Terminations**: If a query holds a write lock for **> 120 seconds**, the scheduler terminates the connection (`pg_terminate_backend`) to prevent database hangs.
