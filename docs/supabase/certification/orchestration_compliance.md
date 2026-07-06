# Supabase Intelligence — Orchestration Compliance
**Sprint 12 · Milestone 7 (Certification)** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Verify compliance of database planners, context compilers, background maintenance, and approvals.
* **Scope**: Governs planners, context, and approvals.
* **Audience**: AI Engineers, Quality Auditors, and System Architects.
* **Related Documents**:
  * [supabase/orchestration/README.md](file:///Users/anzarakhtar/aios/docs/supabase/orchestration/README.md) - Database Orchestration hub.
  * [supabase/orchestration/database_orchestration.md](file:///Users/anzarakhtar/aios/docs/supabase/orchestration/database_orchestration.md) - Coordinator.

---

## 1. Compliance Audit Objectives

This audit verifies that the **AI Database Orchestration** layer manages database plans, compiles prompt contexts, runs background walkers, and prompts the user for approvals.

---

## 2. Orchestration Verification Matrix

```
+------------------------------------+------------------------------------+----------+
| Orchestration Requirement          | Verification Check                 | Status   |
+------------------------------------+------------------------------------+----------+
| 1. DAG Schema Planner              | Resolves execution steps (Inspect, | PASS     |
|                                    | Diff, Write) and handles failures. |          |
+------------------------------------+------------------------------------+----------+
| 2. Context Compiler (OmniRoute)    | Summarizes DDL schemas and filters | PASS     |
|                                    | details when over token limit.     |          |
+------------------------------------+------------------------------------+----------+
| 3. Governance Approval Gates       | Destructive migrations prompt      | PASS     |
|                                    | developers before execution.       |          |
+------------------------------------+------------------------------------+----------+
| 4. Background Maintenance          | Runs background vacuums, reindexing| PASS     |
|                                    | and lock cleanups.                 |          |
+------------------------------------+------------------------------------+----------+
```

---

## 3. Compliance Verification Details

### 3.1 Planners & Context
* Planner checks verify that database write locks trigger retry steps, pausing migrations until locks release.
* Context compilers use signature extractions and relevance filtering to fit schema context into token windows.

### 3.2 Governance & Approvals
* Governance tests confirm that destructive operations (e.g. `DROP TABLE`) trigger user approval challenges.
* Connection settings changes require explicit user approval before saving, preventing unauthorized redirection.
