# Knowledge Versioning & Deprecation Spec
**Sprint 11 · Milestone 4** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define version revision schemas, deprecation flags, and catalog transaction logs.
* **Scope**: Governs database versions, fact updates, and release logs.
* **Audience**: DBAs, Backend Developers, and System Architects.
* **Related Documents**:
  * [research/processing/knowledge_structuring.md](file:///Users/anzarakhtar/aios/docs/research/processing/knowledge_structuring.md) - Database schemas.
  * [research/validation/evidence_graph.md](file:///Users/anzarakhtar/aios/docs/research/validation/evidence_graph.md) - Graph structure.

---

## 1. Knowledge Revision Control

As external library specifications and APIs evolve, cached facts can become outdated. The **Knowledge Versioning** engine tracks modifications to facts using a version ledger:

```sql
CREATE TABLE IF NOT EXISTS fact_version_ledger (
    version_id TEXT PRIMARY KEY,
    fact_id TEXT NOT NULL,
    version_number INTEGER NOT NULL,
    commit_sha256 TEXT NOT NULL,          -- Hash of active file prompting update
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    previous_fact_statement TEXT NOT NULL,
    new_fact_statement TEXT NOT NULL,
    change_reason TEXT,
    FOREIGN KEY(fact_id) REFERENCES codebase_facts(fact_id) ON DELETE CASCADE
);
```

---

## 2. Deprecation & Stale Flags

To prevent agents from using outdated APIs:
* **Stale Flags**: When a new version of a fact is verified (e.g. an API endpoint parameter changes), the previous version is marked as `DEPRECATED` and its CS drops to `0.0`.
* **Outdated Notifications**: If a workspace project depends on a package version associated with a deprecated fact, the AI OS prints a warning in the REPL console:
  ```
  [Research Version Alert]
  Workspace package 'next' is at v13.0, but Next.js docs indicate v14.0 is active.
  Some API routing schemas are deprecated.
  Please run 'npm update next' to sync with the latest specifications.
  ```
