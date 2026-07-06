# Row-Level Security (RLS) Policy Analysis Spec
**Sprint 12 · Milestone 3** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define database queries for extracting RLS policy configurations and validating table security.
* **Scope**: Governs RLS catalogs, policy extraction loops, and parser rules.
* **Audience**: DBAs, Systems Engineers, and Lead Developers.
* **Related Documents**:
  * [supabase/database/schema_intelligence.md](file:///Users/anzarakhtar/aios/docs/supabase/database/schema_intelligence.md) - Schema intelligence.
  * [supabase/security/auth_intelligence.md](file:///Users/anzarakhtar/aios/docs/supabase/security/auth_intelligence.md) - Auth state check.

---

## 1. RLS Policy Extraction

The **RLS Analysis** module queries the PostgreSQL system catalog (`pg_policies`) to identify active table policies and check their configurations:

```sql
SELECT schemaname AS schema_name,
       tablename AS table_name,
       policyname AS policy_name,
       permissive,
       roles,
       cmd AS operation,                        -- SELECT, INSERT, UPDATE, DELETE, ALL
       qual AS using_expression,                -- USING clause filter
       with_check AS with_check_expression      -- WITH CHECK clause filter
FROM pg_policies
WHERE schemaname = :schema_name;
```

---

## 2. Table RLS Activation Checks

* **RLS Status Queries**: Checks `pg_class` to verify if Row-Level Security is enabled on tables:
  ```sql
  SELECT c.relname AS table_name, c.relrowsecurity AS rls_enabled, c.relforcerowsecurity AS rls_forced
  FROM pg_class c
  JOIN pg_namespace n ON n.oid = c.relnamespace
  WHERE n.nspname = :schema_name AND c.relkind = 'r';
  ```
* **Forced RLS Auditing**: Flags tables where RLS is enabled but not forced, warning that the table owner could bypass policies.
* **Metadata Logging**: Maps policy metadata to SQLite as `InfrastructureResource` instances, indexing definitions in Qdrant for semantic analysis.
