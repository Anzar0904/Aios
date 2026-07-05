# Semantic Search Optimizations

This document details the retrieval and performance optimizations implemented for semantic search.

---

## 1. Caching Strategies

* **Embedding Cache**: Caches generated text embeddings using version tags. Prevents duplicate calculation calls.
* **Query Cache**: Caches top-k search results per query string and filter values. Expirations invalidate older caches.

---

## 2. Low-Latency Pre-Filtering

Pre-filters compile into Qdrant keyword indices before search execution. This reduces search spaces to only relevant workspaces or projects, increasing top-k query speeds.

---

## 3. Lazy Payload Loading & Timeouts

* **Lazy Loading**: Payloads are extracted from returned Qdrant points lazily, mapping only fields like `text` to `SemanticResult`.
* **Timeout Controls**: Search queries respect connection timeouts to degrade gracefully to DB lookups if Qdrant exceeds latency limits.
