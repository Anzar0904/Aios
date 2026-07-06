# Approval Workflows & Verification Gates Spec
**Sprint 12 · Milestone 6** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define approval challenge rules, schema modification prompts, and bypass constraints.
* **Scope**: Governs prompt triggers, validation levels, and logs.
* **Audience**: AI Prompt Engineers, Integration Engineers, and Quality Auditors.
* **Related Documents**:
  * [supabase/security/security_auditing.md](file:///Users/anzarakhtar/aios/docs/supabase/security/security_auditing.md) - Security auditing.
  * [supabase/orchestration/schema_planning.md](file:///Users/anzarakhtar/aios/docs/supabase/orchestration/schema_planning.md) - Schema planning.

---

## 1. Outbound Schema Approvals

Schema modifications can result in data loss or security vulnerabilities. The **Database Orchestration** module coordinates with the local **Approval Engine** to check task risks:
* **Interactive Challenges**: High-risk operations (e.g. dropping columns, modifying tables, disabling RLS) prompt the developer for confirmation before execution.
* **REPL Console Prompts**:
  ```
  [Database Approval Challenge]
  Agent requests to execute migration script: '003_drop_users_table.sql'.
  This operation is DESTRUCTIVE and will delete all user records.
  Confirm execution? [y/N]
  ```

---

## 2. Policy Bypass Warnings

When an agent proposes changes to RLS policies:
1. **Analyze Policy**: The system checks if the changes weaken validation rules (e.g., adding a public access policy).
2. **Warn Developer**: If the changes are insecure, the system prints a warning in the REPL console, requiring explicit confirmation before deployment.
3. **Log Decision**: Logs the developer's decision (accept/reject) to the database.
