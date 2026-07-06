# Supabase Intelligence — Certification Playbook
**Sprint 12 · Milestone 7 (Certification)** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define the compliance validation playbook, audit scopes, and verification procedures for certifying Sprint 12 milestones.
* **Scope**: Governs all verification gates and health scoring indices for Supabase integrations.
* **Audience**: Quality Auditors, Systems Architects, and AI developers.
* **Related Documents**:
  * [16_ENGINEERING_BIBLE.md](file:///Users/anzarakhtar/aios/docs/16_ENGINEERING_BIBLE.md) - Core reference guidelines.
  * [supabase/certification/README.md](file:///Users/anzarakhtar/aios/docs/supabase/certification/README.md) - Navigation hub.

---

## 1. Playbook Framework & Scope

The **Supabase Intelligence Certification Playbook** verifies that all Sprint 12 milestones (Milestones 1–6) conform to the security, local-first, and structural guidelines of the Personal AI OS.

This certification is a **Design and Schema Compliance Audit**. It evaluates database discoverers, query explain checks, credentials vaults, AST blockers, Deno package maps, backups verification scripts, and database orchestration without altering active execution behaviors.

---

## 2. Validation Targets (M1–M6)

The compliance audit evaluates six target areas:

```
+------------------------------------+------------------------------------------+
| Validation Domain                  | Core Verification Criteria               |
+------------------------------------+------------------------------------------+
| 1. Supabase Foundation (M1)        | Local migrations source of truth,        |
|                                    | interface adapters, and DB schema caches.|
+------------------------------------+------------------------------------------+
| 2. Database Intelligence (M2)      | DDL catalog queries, relation checkers,  |
|                                    | index monitors, and EXPLAIN plans.       |
+------------------------------------+------------------------------------------+
| 3. Security Intelligence (M3)      | Key encryption vaults, AST query blocks, |
|                                    | local RLS testing, and drift detectors.  |
+------------------------------------+------------------------------------------+
| 4. Platform Intelligence (M4)      | Deno execution parameters, storage RLS,  |
|                                    | and platform health indicators.          |
+------------------------------------+------------------------------------------+
| 5. Operations Intelligence (M5)    | WebSocket publication checks, migration  |
|                                    | transaction locks, and pg_dump backups.  |
+------------------------------------+------------------------------------------+
| 6. AI DB Orchestration (M6)        | DAG planners, context compression,       |
|                                    | background walkers, and approvals.       |
+------------------------------------+------------------------------------------+
```

---

## 3. Compliance Methodologies

* **Structural Review**: Verify that database schemas, adapter classes, and process execution modules are syntactically complete.
* **Security Scans**: Confirm that AST parsers block DDL query injection attempts, and check that API keys are stored securely.
* **Vector Layout Validation**: Verify dimension compatibility (384d Cosine distance) with the local Sentence Transformer model.
* **Consent Auditing**: Ensure that the AI OS prompts the developer before running destructive database migrations.
