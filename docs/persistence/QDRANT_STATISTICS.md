# Qdrant Platform Operational Statistics

- **Queries Recorded**: 0
- **Average Query Latency**: 0.00ms
- **Embedding Cache Hits**: 0
- **Embedding Cache Misses**: 0
- **Cache Hit Ratio**: 0.00%

---

## 1. Statistics Telemetry Design

Telemetry statistics are updated dynamically:
* **`queries_recorded`**: Total query points lookups.
* **`average_query_latency_ms`**: Average execution duration in milliseconds.
* **`embedding_cache_statistics`**: In-memory cache hit/miss count and ratio.
* **`qdrant_statistics`**: Connection parameters and query latency histograms.
