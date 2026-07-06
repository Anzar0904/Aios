# Workspace Intelligence — Codebase Compliance
**Sprint 10 · Milestone 7 (Certification)** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Verify compliance of AST parsing pipelines, Qdrant vector index configurations, and Redis query cache invalidation.
* **Scope**: Governs AST parsers, Qdrant schemas, and Redis caches.
* **Audience**: DBAs, Search Engineers, and Quality Auditors.
* **Related Documents**:
  * [workspace/codebase/README.md](file:///Users/anzarakhtar/aios/docs/workspace/codebase/README.md) - Codebase Intelligence hub.
  * [workspace/codebase/symbol_index.md](file:///Users/anzarakhtar/aios/docs/workspace/codebase/symbol_index.md) - Symbol indexing.

---

## 1. Compliance Audit Objectives

This audit verifies that the **Codebase Intelligence** layer parses source files correctly, structures index records, and syncs caches without stale data leakage.

---

## 2. Codebase Verification Matrix

```
+------------------------------------+------------------------------------+----------+
| Codebase Requirement               | Verification Check                 | Status   |
+------------------------------------+------------------------------------+----------+
| 1. AST Scope Compilation           | Correctly extracts classes,        | PASS     |
|                                    | functions, signatures, docstrings,  |          |
|                                    | and imports.                       |          |
+------------------------------------+------------------------------------+----------+
| 2. Qdrant Collection Layout        | Matches the 384d Cosine similarity | PASS     |
|                                    | config with indexed payload fields. |          |
+------------------------------------+------------------------------------+----------+
| 3. Redis Invalidation Loops        | File changes trigger automatic     | PASS     |
|                                    | invalidation of matching keys.     |          |
+------------------------------------+------------------------------------+----------+
| 4. Incremental Change Checks       | Timestamp and SHA-256 verifications | PASS     |
|                                    | skip re-compilation for unchanged  |          |
|                                    | files.                             |          |
+------------------------------------+------------------------------------+----------+
```

---

## 3. Compliance Verification Details

### 3.1 AST & Scope Verifications
* AST traversals verify that code sections are chunked by logical boundaries (Classes/Methods) and mapped to start/end line numbers.
* Incremental scanning checks confirm that when a file is modified, only the changed line ranges are re-compiled and updated, preserving unchanged symbols.

### 3.2 Database & Cache Synchronization
* Qdrant collection mappings are verified at 384 dimensions using Cosine distance, with indexes configured for `workspace_id`, `symbol_name`, and `symbol_type`.
* Redis cache checks verify that modifying a file immediately invalidates its cached symbols.
