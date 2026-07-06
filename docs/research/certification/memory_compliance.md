# Research Intelligence — Memory Compliance
**Sprint 11 · Milestone 7 (Certification)** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Verify compliance of SQLite catalogs, Qdrant collections settings, and Redis cache invalidation.
* **Scope**: Governs SQLite schemas, Qdrant vectors, and Redis caches.
* **Audience**: DBAs, Search Engineers, and Quality Auditors.
* **Related Documents**:
  * [research/memory/README.md](file:///Users/anzarakhtar/aios/docs/research/memory/README.md) - Research Memory hub.
  * [research/memory/research_memory.md](file:///Users/anzarakhtar/aios/docs/research/memory/research_memory.md) - Memory configurations.

---

## 1. Compliance Audit Objectives

This audit verifies that the **Research Memory & Continuous Learning** layer indexes technical facts correctly, manages knowledge lifecycles, and purges stale caches.

---

## 2. Memory Verification Matrix

```
+------------------------------------+------------------------------------+----------+
| Memory Requirement                 | Verification Check                 | Status   |
+------------------------------------+------------------------------------+----------+
| 1. SQLite Schema Parity            | Tables match the lifecycle,        | PASS     |
|                                    | evidence, and version ledger schemas. |          |
+------------------------------------+------------------------------------+----------+
| 2. Qdrant Vector collection        | Collection settings match 384d     | PASS     |
|                                    | Cosine distance with indexed payload.|          |
+------------------------------------+------------------------------------+----------+
| 3. Memory Consolidation            | Deduplicates matching concepts     | PASS     |
|                                    | and merges citations.              |          |
+------------------------------------+------------------------------------+----------+
| 4. Forgetting Strategies           | Evicts low-confidence or stale     | PASS     |
|                                    | forum entries under disk limits.   |          |
+------------------------------------+------------------------------------+----------+
| 5. Redis Invalidation Loops        | Cache database updates trigger     | PASS     |
|                                    | namespace invalidation commands.   |          |
+------------------------------------+------------------------------------+----------+
```

---

## 3. Compliance Verification Details

### 3.1 SQLite & Qdrant Mappings
* Database schemas verify cascade-delete relations between documents, concepts, evidences, and relationships.
* Qdrant checks verify the `research_memory` collection matches 384 dimensions and Cosine distance.

### 3.2 Consolidation & Forgetting
* Memory consolidation runs successfully group duplicate facts (similarity > 0.92), merging their citations and cleaning up Qdrant.
* Eviction tests verify that stale forum pages are pruned when SQLite sizes exceed storage limits.
* Redis invalidation checks verify that cache keys are purged on database updates.
