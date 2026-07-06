# Supabase Intelligence — Capabilities Matrix
**Sprint 12 · Milestone 1 (Foundation)** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define technical mappings, domain hierarchies, and processing rules for Supabase infrastructure components.
* **Scope**: Governs resource types, database mappings, and orchestration schemas.
* **Audience**: Systems Integrators, QA Engineers, and AI developers.
* **Related Documents**:
  * [17_KNOWLEDGE_BASE.md](file:///Users/anzarakhtar/aios/docs/17_KNOWLEDGE_BASE.md) - System definitions repository.
  * [supabase/architecture.md](file:///Users/anzarakhtar/aios/docs/supabase/architecture.md) - Technical architecture.

---

## 1. Canonical Infrastructure Hierarchy

To model Supabase resources consistently, the AI OS maps all infrastructure objects to a system-wide hierarchy:

**Infrastructure → Supabase Project → Database → Schema → Object → Record → Metadata → KnowledgeNode**

```
  +----------------------+
  |    Infrastructure    | (e.g. "Cloud backends")
  +----------------------+
            | (1-to-Many)
            v
  +----------------------+
  |   Supabase Project   | (e.g. "ai-os-prod-backend")
  +----------------------+
            | (1-to-1)
            v
  +----------------------+
  |       Database       | (e.g. "PostgreSQL Database Instance")
  +----------------------+
            | (1-to-Many)
            v
  +----------------------+
  |       Schema         | (e.g. "public", "auth", "storage")
  +----------------------+
            | (1-to-Many)
            v
  +----------------------+
  |       Object         | (e.g. "users_profile_table", "create_page_fn")
  +----------------------+
            | (1-to-Many)
            v
  +----------------------+
  |       Record         | (Row entry / function source code definition)
  +----------------------+
            | (1-to-1)
            v
  +----------------------+
  |      Metadata        | (RLS policies, trigger logs, index statistics)
  +----------------------+
            | (1-to-1)
            v
  +----------------------+
  |    KnowledgeNode     | (Local system memory representation)
  +----------------------+
```

---

## 2. Infrastructure Capabilities Matrix

The system classifies and manages Supabase resources across nine dimensions:

### 2.1 Databases & Schemas
* **Targets**: PostgreSQL instance configs, multiple schemas isolation (`public`, `auth`, `storage`, custom).
* **Inspections**: Queries table namespaces and column relationships to build local schemas.

### 2.2 Tables & Views
* **Targets**: PostgreSQL tables, primary keys, foreign key constraints, indexes, views.
* **Operations**: Runs queries, updates structures, and caches schemas locally.

### 2.3 Postgres Functions
* **Targets**: PL/pgSQL database functions, triggers, custom types.
* **Operations**: Parses code logic, updates triggers, and deploys functions.

### 2.4 Row-Level Security (RLS)
* **Targets**: RLS status flags, policy criteria (e.g. `using` and `with check` expressions).
* **Auditing**: Performs static analysis on policy criteria, flagging potential security bypasses.

### 2.5 Authentication (Auth)
* **Targets**: GoTrue tables, auth sessions configurations, SMTP templates, provider OAuth keys.
* **Auditing**: Audits token settings and verifies sign-up flows.

### 2.6 Storage
* **Targets**: Storage buckets, asset policies, metadata.
* **Operations**: Inspects buckets, configures access rules, and uploads assets.

### 2.7 Realtime
* **Targets**: WebSocket subscription channels, Postgres changes replication flags.
* **Operations**: Listens to database updates and formats event streams.

### 2.8 Edge Functions
* **Targets**: Deno runtimes, JavaScript/TypeScript edge scripts.
* **Operations**: Compiles scripts, bundles dependencies, runs local tests, and deploys functions.

### 2.9 Migrations
* **Targets**: PostgreSQL migration files, target system schemas state records.
* **Operations**: Compiles migration files locally, dry-runs scripts, and applies changes.
