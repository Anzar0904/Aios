# Memory Consolidation Spec
**Sprint 11 · Milestone 5** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define periodic task pipelines for merging concept nodes and removing redundant text chunks.
* **Scope**: Governs consolidation queues, deduplication scripts, and database optimization.
* **Audience**: DBAs, Backend Developers, and System Architects.
* **Related Documents**:
  * [research/processing/summarization_pipeline.md](file:///Users/anzarakhtar/aios/docs/research/processing/summarization_pipeline.md) - Summarization spec.
  * [research/memory/knowledge_lifecycle.md](file:///Users/anzarakhtar/aios/docs/research/memory/knowledge_lifecycle.md) - Lifecycle states.

---

## 1. Deduplication & Consolidation Pipeline

Scraping multiple pages can result in duplicate entries (e.g. three different blogs describing the same API parameter details). The **Memory Consolidation** engine runs background loops to merge these records:

```
[Trigger Consolidation] (Cron scheduled / idle CPU)
          |
          v
[Scan Local Database] ===> Find facts with matching concept names
          |
          v
[Compute Semantic Overlap] ===> Group facts with high similarity (> 0.92)
          |
          v
[Merge Evidences] ===> Combine citation links into a single FactNode
          |
          v
[Evict Redundant Chunks] ===> Delete old Qdrant points
```

* **Deduplication Check**: Groups facts with semantic similarity scores above **0.92**.
* **Evidence Merging**: Combines the citations of duplicate records into a single consolidated `FactNode` containing multiple `SUPPORTED_BY` edges.
* **Redundancy Eviction**: Deletes the redundant duplicate vectors from Qdrant, reclaiming local memory resources.
