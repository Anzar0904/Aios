# Qdrant Platform Operational Statistics

- **Queries Recorded**: 0
- **Average Search Latency**: 0.00ms
- **Average Embedding Latency**: 0.00ms
- **Total Index Vector Points**: 0
- **Memory Footprint**: 0.0MB

---

## 1. Operational Statistics Telemetry Design

Qdrant operational statistics will be collected by `QdrantStatisticsCollectorImpl` and forwarded to the global `RuntimeTelemetryCollector` under the key `qdrant_telemetry`:

* **`queries_recorded`**: Total semantic search lookups executed.
* **`avg_search_latency_ms`**: Rolling average search query duration.
* **`avg_embedding_latency_ms`**: Duration to generate text vectors using embedding providers.
* **`vector_count_by_collection`**: Map of collection names to point counts.
* **`cache_hit_rate`**: If local caching of hot search vectors is applied.
* **`network_retry_count`**: Number of connection re-establishments.
