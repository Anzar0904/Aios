# Forgetting & Eviction Strategy Spec
**Sprint 11 · Milestone 5** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define database cleanup tasks, cache eviction parameters, and low-confidence filters.
* **Scope**: Governs SQLite cleans, Qdrant deletion pipelines, and database cron tasks.
* **Audience**: DBAs, Backend Developers, and System Architects.
* **Related Documents**:
  * [research/security_model.md](file:///Users/anzarakhtar/aios/docs/research/security_model.md) - Security path guards.
  * [research/memory/knowledge_lifecycle.md](file:///Users/anzarakhtar/aios/docs/research/memory/knowledge_lifecycle.md) - Lifecycle states.

---

## 1. Eviction Triggers & Rules

To keep local storage usage within bounds:
* **Storage Limit Gate**: Triggered when the SQLite database exceeds **1GB** or when the local disk space falls below **5%** capacity.
* **Low-Confidence Clean**: Automatically deletes `UNVERIFIED` facts whose confidence scores fall below **0.40** after 3 days.

---

## 2. Age Decay & Deprecations Evictions

Background cron tasks scan database entries to identify eviction targets:
* **Stale Blogs & Forums Cleanup**: Deletes cached forum pages and blogs with no active citations that are older than **30 days**.
* **Obsolete API Evictions**: Deletes deprecated package version details when the workspace project updates to a new major release.
* **Permanent Specifications Preservation**: Official standards (RFCs, language specs) are explicitly flagged in the database and are **never** evicted.

---

## 3. Database Cleanup Process

When an eviction is triggered:
1. Delete the raw downloaded text files from disk.
2. Delete the matching database rows in SQLite.
3. Issue a `delete` payload request to Qdrant to remove the corresponding vector points.
4. Run SQLite `VACUUM` to reclaim disk space.
