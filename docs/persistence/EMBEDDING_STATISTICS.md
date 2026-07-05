# Embedding & Search Telemetry Statistics

This document outlines the telemetry statistics logged for embedding generation and semantic queries.

---

## 1. Metrics Tracked

* **Embedding Latency**: Average computation time per text generation.
* **Search Latency**: Query execution times.
* **Cache Hit Ratio**: Calculates hit vs miss counts in `EmbeddingCache` and `QueryCache`.
* **Throughput**: Records counts of `embed`, `batch_embed`, and `search` operations.

---

## 2. Telemetry Aggregation

The `RuntimeIntelligenceServiceImpl` pulls statistics from `EmbeddingEngine` and `SemanticSearchService` under `"embedding_engine_statistics"` and `"semantic_search_statistics"`.
