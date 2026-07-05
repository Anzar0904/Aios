# Hybrid Retrieval Architecture

This document describes the pipeline routing, normalization, and aggregation architecture of the Hybrid Retrieval Service.

---

## 1. System Layout

The `HybridRetrievalServiceImpl` coordinates the retrieval pipeline:

```text
    [ Query String ]
          │
          ▼
   [ Query Analyzer ] ───(Intent, domains, scope)
          │
          ▼
  [ Collection Selector ] ───(Target collections & weights)
          │
          ▼
   [ Vector Search ] ───(Qdrant semantic search)  === (PG Lexical fallback if Qdrant offline)
          │
          ▼
  [ Candidate Ranker ] ───(Score normalization + weighting)
          │
          ▼
  [ Context Optimizer ] ───(Deduplication + token budget packing)
          │
          ▼
    [ Final Context ]
```

---

## 2. Score Normalization

Returned semantic similarity scores (typically between `0.0` and `1.0` for cosine distance) are aggregated alongside payload importance tags and freshness weights to generate a composite sorting score.
