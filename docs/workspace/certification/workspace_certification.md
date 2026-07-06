# Workspace Intelligence — Certification Playbook
**Sprint 10 · Milestone 7 (Certification)** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define the compliance validation playbook, audit scopes, and verification procedures for certifying Sprint 10 milestones.
* **Scope**: Governs all verification gates and health scoring indices for Workspace integrations.
* **Audience**: Quality Auditors, Systems Architects, and AI developers.
* **Related Documents**:
  * [16_ENGINEERING_BIBLE.md](file:///Users/anzarakhtar/aios/docs/16_ENGINEERING_BIBLE.md) - Core reference guidelines.
  * [workspace/certification/README.md](file:///Users/anzarakhtar/aios/docs/workspace/certification/README.md) - Navigation hub.

---

## 1. Playbook Framework & Scope

The **Workspace Intelligence Certification Playbook** verifies that all Sprint 10 milestones (Milestones 1–6) conform to the security, local-first, and structural guidelines of the Personal AI OS.

This certification is a **Design and Schema Compliance Audit**. It evaluates file monitoring systems, AST parsers, database schemas, git history DAGs, tool integrations, and AI orchestration without altering active execution behaviors.

---

## 2. Validation Targets (M1–M6)

The compliance audit evaluates six target areas:

```
+------------------------------------+------------------------------------------+
| Validation Domain                  | Core Verification Criteria               |
+------------------------------------+------------------------------------------+
| 1. Workspace Foundation (M1)       | Path containment rules, JSON-RPC, and    |
|                                    | dependency inversion interfaces.         |
+------------------------------------+------------------------------------------+
| 2. Repository Discovery (M2)       | VCS boundary walkers, classification     |
|                                    | heuristics, and database schemas.        |
+------------------------------------+------------------------------------------+
| 3. Codebase Intelligence (M3)      | AST parsers, Qdrant symbol indexes,     |
|                                    | and Redis active invalidation loops.     |
+------------------------------------+------------------------------------------+
| 4. Git & Source Control (M4)       | Commit graph DAG, conventional lints,     |
|                                    | and symbol history ledgers.              |
+------------------------------------+------------------------------------------+
| 5. Development Tools (M5)          | LSP client proxies, DAP debugger checks, |
|                                    | compiler diagnostics, and lock audits.   |
+------------------------------------+------------------------------------------+
| 6. Workspace Orchestration (M6)    | Concurrency scheduler, context loaders,  |
|                                    | and Approval Engine check loops.         |
+------------------------------------+------------------------------------------+
```

---

## 3. Compliance Methodologies

* **Structural Review**: Verify that database schemas, adapter classes, and process execution modules are syntactically complete.
* **Security Scans**: Confirm that path containment checks block directory traversal attempts, and check that environment variable sanitizers strip keys.
* **Vector Layout Validation**: Verify dimension compatibility (384d Cosine distance) with the local Sentence Transformer model.
* **Consent Auditing**: Ensure that the AI OS prompts the developer before running medium-to-critical risk operations.
