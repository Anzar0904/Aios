# Knowledge Lifecycle Management Spec
**Sprint 11 · Milestone 5** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define state transitions, validation checks, and deprecation flags for technical knowledge nodes.
* **Scope**: Governs database state keys, pipeline logs, and cron checkers.
* **Audience**: AI Prompt Engineers, Integration Engineers, and Quality Auditors.
* **Related Documents**:
  * [research/capabilities.md](file:///Users/anzarakhtar/aios/docs/research/capabilities.md) - Capabilities domains.
  * [research/processing/acquisition_pipeline.md](file:///Users/anzarakhtar/aios/docs/research/source_discovery/acquisition_pipeline.md) - Acquisition stages.

---

## 1. Lifecycle State Machine

Technical facts undergo a structured lifecycle, moving from raw web downloads to verified system knowledge:

```
[Acquired] (Raw document downloaded)
    |
    v
[Processing] (Markdown cleaned, entities recognized)
    |
    v
[Validated] (SSRF/HTTPS checked, direct tests pass, CS > 0.80)
    |
    v
[Consolidated] (Merged into core fact catalog, duplicates removed)
    |
    +---> [Stale / Deprecated] (New version verified -> CS set to 0.0)
    |         |
    |         v
    +---> [Forgotten] (Low-use data evicted from disk/RAM cache)
```

---

## 2. State Indicators & Database Schema

The state of each knowledge node is tracked in the local SQLite database:

```sql
CREATE TABLE IF NOT EXISTS knowledge_lifecycle_ledger (
    ledger_id INTEGER PRIMARY KEY AUTOINCREMENT,
    fact_id TEXT NOT NULL,
    current_state TEXT CHECK(current_state IN ('ACQUIRED', 'PROCESSING', 'VALIDATED', 'CONSOLIDATED', 'DEPRECATED', 'FORGOTTEN')) NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    state_change_reason TEXT,
    FOREIGN KEY(fact_id) REFERENCES codebase_facts(fact_id) ON DELETE CASCADE
);
```

* **Validated State**: Requires a confidence score (CS) above **0.80**.
* **Consolidated State**: Triggered when a fact is successfully merged into the core catalog, removing redundant chunks.
* **Deprecated State**: Triggered when a new version of the fact is verified.
