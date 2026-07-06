# Migration Workflows Spec
**Sprint 12 · Milestone 6** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define standard execution workflows, process states, and verification steps for common database tasks.
* **Scope**: Governs automated migrations, RLS checks, and function deployments.
* **Audience**: AI Prompt Engineers, Integration Engineers, and Quality Auditors.
* **Related Documents**:
  * [supabase/orchestration/schema_planning.md](file:///Users/anzarakhtar/aios/docs/supabase/orchestration/schema_planning.md) - Schema planning.
  * [supabase/orchestration/autonomous_operations.md](file:///Users/anzarakhtar/aios/docs/supabase/orchestration/autonomous_operations.md) - Autonomous operations.

---

## 1. Core Migration Workflows

The **Database Orchestration** module defines three standard workflows for common database tasks:

### 1.1 Deploy Schema Changes
1. **Target Identification**: Read target schema files.
2. **Compute Schema Diff**: Compare remote table structures against local migration files.
3. **Execute Dry-Run**: Run the migration locally in a container to verify constraint safety.
4. **Apply Changes**: Execute the DDL statements on the remote database, updating the schema.

### 1.2 Audit Security Policies
1. **Fetch Policies**: Query remote catalogs to locate active RLS policies.
2. **Verify USING Expressions**: Run static checks on policy criteria to identify vulnerabilities.
3. **Run Mock Queries**: Test policies under simulated user roles.
4. **Log Results**: Write warnings to the database.

### 1.3 Sync Storage Buckets
1. **Scan Local Bucket Configs**: Inspect local bucket settings.
2. **Retrieve Remote Bucket State**: Query Supabase Storage APIs.
3. **Update Buckets**: Reconcile bucket visibility, size limits, and allowed MIME types.
