# Supabase Integration & Caching Strategy
**Sprint 12 · Milestone 1 (Foundation)** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define synchronization loops, SQL diff generators, vector mappings, and local caching parameters.
* **Scope**: Governs schema checkers, migration runners, and database caches.
* **Audience**: DBAs, Search Engineers, and Quality Auditors.
* **Related Documents**:
  * [workspace/integration_strategy.md](file:///Users/anzarakhtar/aios/docs/workspace/integration_strategy.md) - System workspace synchronization.
  * [supabase/capabilities.md](file:///Users/anzarakhtar/aios/docs/supabase/capabilities.md) - Mapped capabilities.

---

## 1. Schema Diffing & Local Compilation

To safely update remote databases, the system generates migrations using local compilation:

```
[Local Migration Files]
          |
          v
[Compute Schema Diff] <===> [Inspect Remote Supabase State]
          |
          +---> Compiles DDL commands (CREATE TABLE, ALTER COLUMN)
          |
          v
[Generate SQL Migration] ===> Dry-run locally ---> Apply to remote database
```

1. **Remote Inspection**: Queries remote catalogs to fetch the active schema structure.
2. **Schema Diffing**: Compares the remote schema against local migration files to identify differences.
3. **Migration Compilation**: Generates SQL migration scripts containing DDL commands to reconcile differences.
4. **Dry-Run Validation**: Executes migrations on a local PostgreSQL replica to test changes before applying them to Supabase.

---

## 2. Qdrant Vector Collection Mappings

Database schemas and postgres functions are embedded and saved to the **`supabase_memory`** collection in Qdrant:
* **Dimensions**: 384 dimensions.
* **Payload Fields**:
  ```json
  {
    "workspace_id": "profile_hash_value",
    "source": "supabase",
    "project_ref": "remote_project_id",
    "schema_name": "public",
    "table_name": "users_profile",
    "columns_schema": "id uuid primary key, updated_at timestamp...",
    "text_content": "Table public.users_profile holds profile info and tracks update times."
  }
  ```
* **Payload Indices**: `project_ref`, `schema_name`, and `table_name` are indexed in Qdrant, enabling sub-10ms semantic searches.

---

## 3. Local SQLite Schema Cache

* **Cache Lookup**: The inspection engine queries the local SQLite `schema_tables` table. If the cached schema has not expired, it returns results directly, avoiding network latency.
* **Expiration TTLs**:
  * Active schemas & tables: **3600 seconds (1 hour)**.
  * RLS policies & auth configurations: **1800 seconds (30 minutes)**.
  * Migration logs: **Permanent (Never expire)**.
