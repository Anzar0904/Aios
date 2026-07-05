# Qdrant Runtime Statistics

This document outlines the metrics, operation counts, and cache statistics tracked by the Qdrant Runtime Statistics Collector in the Personal AI OS.

---

## 1. Tracked Metrics

* **Queries Recorded**: Total number of search operations executed since startup.
* **Cache Statistics**: Tracks hits, misses, and set counts across the Query, Candidate, Ranking, and Context caches.
* **Embedding Statistics**: Monitors vector dimensions size, model names, and generation counts.
* **Repository Statistics**: Captures CRUD operations frequency and latency metrics for each specific vector collection repository.

---

## 2. Learning Metadata Schema

The statistics collector exposes a `learning_metadata` block forwarded to the global monorepo dashboard to track configuration settings:

```json
{
  "learning_metadata": {
    "vector_dims": 1536,
    "distance_metric": "Cosine",
    "model_version": "v1.0"
  }
}
```

This data is used by model routers to evaluate semantic search capacities and prevent collection schema mismatch during upgrades.
