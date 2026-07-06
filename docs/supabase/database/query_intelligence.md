# SQL Query Intelligence & Plan Validation Spec
**Sprint 12 · Milestone 2** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define SQL query validation rules, EXPLAIN plan checks, and query performance metrics.
* **Scope**: Governs query parsers, AST validators, and explain log checks.
* **Audience**: AI Prompt Engineers, Integration Engineers, and Quality Auditors.
* **Related Documents**:
  * [supabase/security_model.md](file:///Users/anzarakhtar/aios/docs/supabase/security_model.md) - SQL security and AST checks.
  * [supabase/database/index_analysis.md](file:///Users/anzarakhtar/aios/docs/supabase/database/index_analysis.md) - Index analysis.

---

## 1. Query Execution & Verification

Before running database queries, the **Query Intelligence** engine analyzes inputs to verify compatibility and efficiency:
* **AST Validation**: Passes SQL to local parser libraries (`pg_query`) to verify syntax and ensure parameters match table schemas.
* **EXPLAIN Plan Auditing**: Prepends `EXPLAIN (ANALYZE, COSTS, VERBOSE, BUFFERS, FORMAT JSON)` to check execution plans:
  * Compiles cost estimations.
  * Flags sequential scans on large tables (> 10,000 rows).
  * Alerts developer if execution costs exceed threshold settings.

---

## 2. Latency Metrics Logging

* **Execution Tracking**: Connection adapters measure execution latency, logging queries that exceed **500ms** to `docs/supabase/scratch/slow_queries.log`.
* **Redis Caching Rules**: Frequently executed read queries are cached in Redis namespace scopes (`supabase:query_cache:[hash]`), reducing repeat database loads.
