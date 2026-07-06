# Migration Analysis & Schema Diff Spec
**Sprint 12 · Milestone 2** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define migration tracking schemas, schema version validations, and local diff checkers.
* **Scope**: Governs migration ledgers, migration sql checks, and DDL diff generators.
* **Audience**: DBAs, Systems Architects, and Lead Developers.
* **Related Documents**:
  * [supabase/integration_strategy.md](file:///Users/anzarakhtar/aios/docs/supabase/integration_strategy.md) - Caching and integration.
  * [supabase/database/schema_intelligence.md](file:///Users/anzarakhtar/aios/docs/supabase/database/schema_intelligence.md) - Schema intelligence.

---

## 1. Migration History Tracking

The system tracks applied migrations by querying the remote schema history table (e.g. `supabase_migrations.schema_migrations` or `prisma_migrations` based on active configurations):

```sql
SELECT version, statements, applied_at FROM supabase_migrations.schema_migrations 
ORDER BY version ASC;
```

Discovered migration runs are saved to the local SQLite version ledger, keeping history synchronized.

---

## 2. Local Diff & Syntax Checks

Before applying migration SQL scripts:
* **DDL Diff Engine**: Generates DDL scripts (e.g. `CREATE TABLE`, `ALTER COLUMN`) by comparing local schema files against remote states.
* **Syntax Validation**: Passes SQL statements to local parsers to check for syntax errors before execution.
* **Destructive Command Warning**: Flags commands that delete data (e.g. `DROP COLUMN`, `DROP TABLE`), requiring user approval before running.
* **PostgreSQL dry-runs**: Dry-runs migrations on a local PostgreSQL container, verifying that scripts execute without constraints errors.
