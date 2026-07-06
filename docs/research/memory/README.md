# Research Memory & Continuous Learning — Navigation Hub
**Sprint 11 · Milestone 5** · Version 1.0 · July 2026

---

> [!IMPORTANT]
> This directory houses the **Research Memory & Continuous Learning** specifications for the Personal AI OS.
> It builds upon the [Research Foundation](file:///Users/anzarakhtar/aios/docs/research/README.md), [Source Discovery](file:///Users/anzarakhtar/aios/docs/research/source_discovery/README.md), [Research Processing](file:///Users/anzarakhtar/aios/docs/research/processing/README.md), and [Knowledge Validation](file:///Users/anzarakhtar/aios/docs/research/validation/README.md) specifications.
>
> In accordance with local-first system guidelines, all long-term memory indexes, lifecycle state machines, consolidation routines, forgetting evictions, and health check-ups are processed locally, utilizing PostgreSQL databases, Qdrant vectors, and Redis caches.

---

## Documents

| Document | Purpose |
|---|---|
| [research_memory.md](file:///Users/anzarakhtar/aios/docs/research/memory/research_memory.md) | Long-term memory indexing across relational databases and Qdrant collections |
| [knowledge_lifecycle.md](file:///Users/anzarakhtar/aios/docs/research/memory/knowledge_lifecycle.md) | State machine transitions: Acquired → Processing → Validated → Consolidated → Deprecated |
| [memory_consolidation.md](file:///Users/anzarakhtar/aios/docs/research/memory/memory_consolidation.md) | Periodic summarization, merging raw chunks, and removing duplicate facts |
| [incremental_learning.md](file:///Users/anzarakhtar/aios/docs/research/memory/incremental_learning.md) | Updating concept nodes, appending evidence records, and boosting confidence scores |
| [forgetting_strategy.md](file:///Users/anzarakhtar/aios/docs/research/memory/forgetting_strategy.md) | Eviction thresholds, cleaning old developer blogs, and clearing stale context |
| [retrieval_optimization.md](file:///Users/anzarakhtar/aios/docs/research/memory/retrieval_optimization.md) | Hybrid search queries (RRF), Redis caches configuration, and OmniRoute filters |
| [memory_health.md](file:///Users/anzarakhtar/aios/docs/research/memory/memory_health.md) | Index fragmentation ratios, orphan facts diagnostics, and database repair scripts |

---

## Reading Order

1. **[`research_memory.md`](file:///Users/anzarakhtar/aios/docs/research/memory/research_memory.md)** & **[`knowledge_lifecycle.md`](file:///Users/anzarakhtar/aios/docs/research/memory/knowledge_lifecycle.md)**: Start here to understand storage mapping and states.
2. **[`memory_consolidation.md`](file:///Users/anzarakhtar/aios/docs/research/memory/memory_consolidation.md)** & **[`incremental_learning.md`](file:///Users/anzarakhtar/aios/docs/research/memory/incremental_learning.md)**: Study how facts are merged and updated.
3. **[`forgetting_strategy.md`](file:///Users/anzarakhtar/aios/docs/research/memory/forgetting_strategy.md)**: Review criteria for evicting outdated records.
4. **[`retrieval_optimization.md`](file:///Users/anzarakhtar/aios/docs/research/memory/retrieval_optimization.md)**: Explore hybrid search queries and Redis cache strategies.
5. **[`memory_health.md`](file:///Users/anzarakhtar/aios/docs/research/memory/memory_health.md)**: Review database health diagnostics.
