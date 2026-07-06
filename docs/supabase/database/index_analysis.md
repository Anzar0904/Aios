# Database Index Analysis Spec
**Sprint 12 · Milestone 2** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define index scan queries, access patterns evaluations, and index suggestion heuristics.
* **Scope**: Governs indexes tables, performance counters, and recommendations engines.
* **Audience**: DBAs, Systems Engineers, and Lead Developers.
* **Related Documents**:
  * [supabase/integration_strategy.md](file:///Users/anzarakhtar/aios/docs/supabase/integration_strategy.md) - Caching and integration.
  * [supabase/database/schema_intelligence.md](file:///Users/anzarakhtar/aios/docs/supabase/database/schema_intelligence.md) - Schema intelligence.

---

## 1. Index Scanning & Types

The **Index Analysis** engine scans tables to identify index configurations and usage metrics:
* **Index Configurations**:
  ```sql
  SELECT tablename, indexname, indexdef FROM pg_indexes 
  WHERE schemaname = :schema_name;
  ```
* **Index Types**: Classifies indexes by type (B-tree for primary keys, GIN for JSONB and search columns, GiST for geo-spatial metrics).

---

## 2. Usage Statistics & Recommendations

To keep index overhead low:
* **Unused Index Checks**: Queries `pg_stat_user_indexes` to identify indexes with low scan counts (`idx_scan < 5` on tables with > 10,000 rows), suggesting removal to save disk write cycles.
* **Missing Index Suggestions**: Inspects `pg_stat_user_tables` and identifies tables with high numbers of sequential scans (`seq_scan`), suggesting new index configurations on commonly queried columns.
* **Index Cache Parity**: Stores active index definitions in SQLite and updates vectors in Qdrant, helping agents write queries that use existing indexes.
