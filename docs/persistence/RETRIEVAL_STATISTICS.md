# Retrieval Statistics Telemetry Documentation

This document describes the telemetry statistics collected and exposed by the Hybrid Retrieval service and its components in the Personal AI OS.

---

## 1. Hybrid Retrieval Statistics

The `HybridRetrievalServiceImpl.get_statistics()` method returns a unified telemetry payload:

```json
{
  "operation_counts": {
    "retrieve": 12
  },
  "average_latency_ms": 42.5,
  "collection_utilisation": {
    "engineering_memory": 8,
    "documentation_memory": 4
  },
  "collection_matches": {
    "engineering_memory": 45,
    "documentation_memory": 12
  },
  "cache_stats": {
    "query_hits": 2,
    "query_misses": 10,
    "query_sets": 10,
    "candidate_hits": 5,
    "candidate_misses": 5,
    "candidate_sets": 5,
    "ranking_hits": 0,
    "ranking_misses": 0,
    "ranking_sets": 0,
    "context_hits": 0,
    "context_misses": 0,
    "context_sets": 0,
    "total_hits": 7,
    "total_misses": 15,
    "hits": 7,
    "misses": 15,
    "overall_hit_ratio": 0.3182,
    "cache_sizes": {
      "query": 10,
      "candidate": 5,
      "ranking": 0,
      "context": 0
    },
    "redis_available": true
  },
  "ranker_stats": {
    "total_ranked": 57,
    "average_ranking_latency_ms": 1.2,
    "current_weights": {
      "semantic_similarity": 0.35,
      "importance": 0.20,
      "freshness": 0.15,
      "workspace_relevance": 0.10,
      "project_relevance": 0.10,
      "source_quality": 0.05,
      "engineering_priority": 0.03,
      "metadata_confidence": 0.02,
      "duplicate_penalty": -0.10
    }
  },
  "optimizer_stats": {
    "total_optimizations": 12,
    "total_candidates_processed": 57,
    "total_candidates_included": 35,
    "total_tokens_budgeted": 48000,
    "total_tokens_output": 12500
  },
  "recommendations": []
}
```

---

## 2. Telemetry Coverage

### 2.1 Cache Statistics
* **Hit Ratio**: Computed per tier and overall across all requests.
* **LRU Sizes**: Monitored count of active items stored in local fallbacks.
* **Double-counting Fix**: Resolves historical bugs where checking local cache after a Redis miss double-counted misses and misrecorded local hits.

### 2.2 Collection Utilisation
* **Usage Counters**: Tracks routing frequency per collection to evaluate domain maps skew.
* **Match Densities**: Tracks candidates returned per collection.

### 2.3 Ranker Statistics
* **Rank Volumes**: Count of total candidates evaluated by the composite formula.
* **Latency Profiles**: Timing metrics for executing time-decay and sorting heuristics.

### 2.4 Context Optimizer Statistics
* **Compression Factors**: Computes token usage against the allocated budgets.
* **Candidate Gating counts**: Number of candidates successfully packed vs skipped.
