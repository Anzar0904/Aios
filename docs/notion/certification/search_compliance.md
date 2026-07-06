# Notion Intelligence — Search & Memory Compliance
**Sprint 9 · Milestone 7 (Certification)** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Verify compliance of SQLite FTS5 indexing, Qdrant vector schemas, embedding pipeline configurations, and Redis cache strategies.
* **Scope**: Governs index schema audits, vector dimension checks, and cache TTL validations.
* **Audience**: DBAs, Search Engineers, and Quality Auditors.
* **Related Documents**:
  * [notion/search/README.md](file:///Users/anzarakhtar/aios/docs/notion/search/README.md) - Search navigation hub.
  * [docs/persistence/QDRANT_PLATFORM_ARCHITECTURE.md](file:///Users/anzarakhtar/aios/docs/persistence/QDRANT_PLATFORM_ARCHITECTURE.md) - Core vector DB architecture.

---

## 1. Compliance Audit Objectives

This audit verifies that the **Search & Semantic Memory** layer indexes page content correctly, retrieves relevant context under target latency thresholds, and caches frequent queries without data freshness violations.

---

## 2. Search & Memory Verification Matrix

```
+------------------------------------+------------------------------------+----------+
| Search/Memory Requirement          | Verification Check                 | Status   |
+------------------------------------+------------------------------------+----------+
| 1. SQLite FTS5 Schema              | `notion_pages_fts` virtual table   | PASS     |
|                                    | uses porter + unicode61 tokenizers |          |
+------------------------------------+------------------------------------+----------+
| 2. Qdrant Collection Settings      | `knowledge_memory` uses 384-dim    | PASS     |
|                                    | Cosine distance with payload       |          |
|                                    | indexes on source & workspace_id.  |          |
+------------------------------------+------------------------------------+----------+
| 3. Embedding Pipeline              | `all-MiniLM-L6-v2` produces 384-d  | PASS     |
|                                    | vectors locally; Ollama fallback   |          |
|                                    | is configured.                     |          |
+------------------------------------+------------------------------------+----------+
| 4. Hybrid Search (RRF)             | BM25 and Cosine results are fused  | PASS     |
|                                    | using $k=60$ RRF algorithm.        |          |
+------------------------------------+------------------------------------+----------+
| 5. Similarity Threshold            | Qdrant searches filter results     | PASS     |
|                                    | below $0.75$ cosine score.         |          |
+------------------------------------+------------------------------------+----------+
| 6. Redis Cache TTLs                | Query cache: 900s; Document: 3600s;| PASS     |
|                                    | Metadata: 86400s.                  |          |
+------------------------------------+------------------------------------+----------+
| 7. Sync-Aware Index Pruning        | Vector points are deleted before   | PASS     |
|                                    | re-indexing on page modification.  |          |
+------------------------------------+------------------------------------+----------+
| 8. Active Cache Invalidation       | SQLite sync changes immediately    | PASS     |
|                                    | purge matching Redis namespace.    |          |
+------------------------------------+------------------------------------+----------+
```

---

## 3. Compliance Verification Details

### 3.1 Chunking Strategy Validation
* Chunk size is verified at ≤ 500 tokens with a 50-token overlap.
* Structural chunking confirms all chunks are prefixed with heading path breadcrumbs (`Page Title / Section Path`).

### 3.2 Latency Targets
* Qdrant similarity search with payload filters: **< 10ms** for indexed fields.
* SQLite FTS5 keyword match with BM25 rank sort: **< 5ms** per query.
* Redis cached query response: **< 1ms** for cache hits.

### 3.3 Workspace Scope Isolation
* All Qdrant queries include `workspace_id` and `source=notion` payload filters, preventing cross-workspace context leakage.
