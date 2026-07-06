# Operational Health & Performance Diagnostics Spec
**Sprint 12 · Milestone 5** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define database integrity tests, connection lock diagnostics, and reindexing tasks.
* **Scope**: Governs health limits, diagnostic checks, and repair scripts.
* **Audience**: Quality Auditors, DBAs, and Systems Engineers.
* **Related Documents**:
  * [supabase/database/database_health.md](file:///Users/anzarakhtar/aios/docs/supabase/database/database_health.md) - Database health.
  * [supabase/operations/realtime_intelligence.md](file:///Users/anzarakhtar/aios/docs/supabase/operations/realtime_intelligence.md) - State abstraction.

---

## 1. Operational Health Metrics

The **Operational Health** module monitors database metrics to track performance and stability:

```
+------------------------------------+------------------------------------+----------+
| Health Indicator                   | Target Range                       | Priority |
+------------------------------------+------------------------------------+----------+
| 1. Index Fragmentation             | < 20% index fragmentation          | Medium   |
+------------------------------------+------------------------------------+----------+
| 2. Transaction Locks Count         | 0 active write locks blockings     | High     |
+------------------------------------+------------------------------------+----------+
| 3. Storage Tier Limit              | < 90% project storage tier         | Medium   |
+------------------------------------+------------------------------------+----------+
| 4. Database Parity                 | 100% schema match (local vs remote)| High     |
+------------------------------------+------------------------------------+----------+
```

---

## 2. Health Recovery Actions

* **Clean Locks**: Terminates blocked write queries if locks persist for **> 120 seconds** to prevent database hangs.
* **Reindexing**: Triggers concurrent index rebuilds (`REINDEX CONCURRENTLY [index_name]`) if fragmentation exceeds limits.
* **Storage Cleanup**: Evicts temporary files from storage buckets to free space.
