# Infrastructure Governance & Key Vaults Spec
**Sprint 12 · Milestone 6** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define SQL query AST filters, key encryption vaults, and database access controls.
* **Scope**: Governs SQL security, key storage, and access controls.
* **Audience**: Security Auditors, System Architects, and Integration Developers.
* **Related Documents**:
  * [supabase/security_model.md](file:///Users/anzarakhtar/aios/docs/supabase/security_model.md) - Security model.
  * [supabase/orchestration/approval_workflows.md](file:///Users/anzarakhtar/aios/docs/supabase/orchestration/approval_workflows.md) - Approval workflows.

---

## 1. SQL Query AST Filtering

To prevent execution of unauthorized commands:
* **AST Scanners**: Passes SQL queries to local parsers (`pg_query`) to verify syntax and ensure parameters match table schemas.
* **Query Blockers**: Standard query tools block destructive commands (e.g. `DROP`, `TRUNCATE`, `ALTER`), requiring developer confirmation before running.

---

## 2. API Key Vault Guards

* **Service Role Keys**: Service role keys are stored in the database using SQLCipher. Access is limited to registered migration adapters, preventing plaintext keys from leaking in console outputs or logs.
* **Connection Lockdowns**: Changes to database connection settings (e.g. host IP, port, database name) require explicit user approval before saving, preventing redirection to unauthorized servers.
