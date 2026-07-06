# Supabase Intelligence — Architecture Specification
**Sprint 12 · Milestone 1 (Foundation)** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define the technical architecture, interfaces, and database schemas for the Supabase Intelligence module.
* **Scope**: Governs Python service classes, database adapters, and local metadata databases.
* **Audience**: Systems Architects, Lead Developers, and AI coding agents.
* **Related Documents**:
  * [02_ARCHITECTURE_GUIDELINES.md](file:///Users/anzarakhtar/aios/docs/02_ARCHITECTURE_GUIDELINES.md) - Dependency Injection and registry rules.
  * [supabase/supabase_intelligence.md](file:///Users/anzarakhtar/aios/docs/supabase/supabase_intelligence.md) - Conceptual vision.

---

## 1. High-Level Architecture

Following the **Dependency Inversion Principle (DIP)** established in [02_ARCHITECTURE_GUIDELINES.md](file:///Users/anzarakhtar/aios/docs/02_ARCHITECTURE_GUIDELINES.md), the `SupabaseIntelligenceService` interacts with remote Supabase instances using abstract adapters:

```
                  +-----------------------------------+
                  |        ServiceRegistry            |
                  +-----------------------------------+
                                    |
                                    v
                  +-----------------------------------+
                  |     SupabaseIntelligenceService   |
                  +-----------------------------------+
                                    |
                                    v
                  +-----------------------------------+
                  |      SupabaseClientAdapter        | (Abstract Interface)
                  +-----------------------------------+
                                    ^
                                    |
                  +-----------------------------------+
                  |      BaseSupabaseClientAdapter    | (Concrete Implementation)
                  +-----------------------------------+
                    /                |                \
                   v                 v                 v
       +---------------+     +---------------+     +---------------+
       |   PostgREST   |     |   GoTrue      |     |   Realtime    |
       |    Adapter    |     |   Adapter     |     |    Adapter    |
       +---------------+     +---------------+     +---------------+
               |                     |                     |
               v                     v                     v
       +---------------+     +---------------+             |
       | Qdrant Vector |     | SQLite Cache  |             v
       | (Supabase DB) |     | (SQLCipher)   |     [Remote Supabase API]
       +---------------+     +---------------+
```

---

## 2. Component Deep Dive

### 2.1 SupabaseIntelligenceService
* **Namespace**: `aios.services.supabase`
* **Responsibility**: Coordinates schema discoveries, migration dry-runs, RLS validations, and Edge Function deployments.
* **Interface**:
  ```python
  class SupabaseIntelligenceService(ABC):
      @abstractmethod
      def inspect_schema(self, schema_name: str = "public") -> SupabaseSchema:
          """Inspect schema tables, views, relationships, and RLS states."""
          pass

      @abstractmethod
      def generate_migration(self, target_schema: SupabaseSchema) -> MigrationFile:
          """Compare target schema state with local workspace schema, generating diff SQL."""
          pass

      @abstractmethod
      def validate_rls_policies(self, table_name: str) -> List[RLSValidationResult]:
          """Audit RLS policies locally for security vulnerabilities."""
          pass
  ```

### 2.2 SupabaseClientAdapter
* **Namespace**: `aios.providers.supabase.adapters`
* **Responsibility**: Abstract client contract for executing SQL queries, managing users, and deploying functions.
* **Interface**:
  ```python
  class SupabaseClientAdapter(ABC):
      @abstractmethod
      def execute_sql(self, sql_query: str) -> QueryResult:
          """Execute raw SQL queries against the target database."""
          pass

      @abstractmethod
      def deploy_edge_function(self, function_name: str, code: str) -> DeploymentResult:
          """Deploy Edge Function code to the remote Supabase project."""
          pass
  ```

### 2.3 SupabaseStateStore
* **Namespace**: `aios.providers.supabase.storage`
* **Responsibility**: Manages the local SQLite database containing cached schemas, table metadata, and migration logs.
* **Schema**:
  ```sql
  CREATE TABLE IF NOT EXISTS supabase_instances (
      instance_id TEXT PRIMARY KEY,
      project_ref TEXT NOT NULL UNIQUE,
      api_url TEXT NOT NULL,
      cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  );

  CREATE TABLE IF NOT EXISTS schema_tables (
      table_id TEXT PRIMARY KEY,
      instance_id TEXT NOT NULL,
      schema_name TEXT NOT NULL,
      table_name TEXT NOT NULL,
      columns_schema TEXT NOT NULL,         -- JSON serialization of columns properties
      rls_enabled BOOLEAN NOT NULL DEFAULT FALSE,
      FOREIGN KEY(instance_id) REFERENCES supabase_instances(instance_id) ON DELETE CASCADE
  );
  ```

---

## 3. Operations Flow

When a developer agent processes a migration:
1. **Schema Check**: Queries the local SQLite catalog to inspect active table states.
2. **Local Diffing**: Compiles migrations locally and runs SQL diff checks.
3. **Approval Gate**: Intercepts modifications, presenting the SQL diff to the developer for confirmation.
4. **Execution**: Executes the migration on the remote database.
5. **Caching**: Updates local SQLite and indexes the new schema in Qdrant.
