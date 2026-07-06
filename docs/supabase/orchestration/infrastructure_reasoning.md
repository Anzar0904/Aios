# Infrastructure Reasoning & Dependency Analysis Spec
**Sprint 12 · Milestone 6** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define technical interfaces and logic for analyzing schemas, tracing dependencies, and auditing configurations.
* **Scope**: Governs schema analyzers, dependency graphs, and drift verifiers.
* **Audience**: Systems Integrators, DBAs, and Lead Developers.
* **Related Documents**:
  * [supabase/database/relationship_mapping.md](file:///Users/anzarakhtar/aios/docs/supabase/database/relationship_mapping.md) - Relationship mapping.
  * [supabase/security/rls_analysis.md](file:///Users/anzarakhtar/aios/docs/supabase/security/rls_analysis.md) - RLS analysis.

---

## 1. Schema & RLS Reasoning

The **Infrastructure Reasoning** engine evaluates database components to verify security and consistency:
* **Constraint Dependency Resolution**: Traces foreign key relationships to determine the correct order for DDL executions.
* **RLS Policy Audits**: Analyzes RLS policy criteria, flagging potential security bypasses.
* **Drift Analysis**: Compares desired configurations against active states to identify discrepancies.

---

## 2. Configuration State Evaluations

Evaluations are performed using the system state model:
* **Managed Resource**: PostgreSQL Table structure.
* **Desired State**: Expected configurations defined in local schemas.
* **Observed State**: Actual active configuration retrieved from Supabase.
* **Drift**: Discrepancies (e.g. missing column or disabled RLS).
* **Recommendation**: Suggested remediation.
* **Execution Plan**: Deploy the updated table schema via dry-run checked migrations.
