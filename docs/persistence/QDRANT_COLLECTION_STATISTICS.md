# Qdrant Collection Statistics Telemetry

This document details the telemetry metrics collected for the vector repository collections.

---

## 1. Metrics Tracked

The following statistics are monitored dynamically for all 9 collections:
* **`vectors_count`**: Number of indexed vectors in the HNSW segment.
* **`points_count`**: Total points in the collection (including update queue buffer).
* **`operation_counts`**: Total invocations of `save`, `upsert`, `get`, `delete`, `exists`, `search`, `batch_upsert`, and `batch_delete`.
* **`average_latencies_ms`**: Average execution latency profile per operation type.

---

## 2. Integration with Runtime Intelligence

The `RuntimeIntelligenceServiceImpl` crawls the `RepositoryRegistry` and aggregates all active repositories under the `"qdrant_repository_statistics"` field.
