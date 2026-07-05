# Embedding Engine Architecture

This document describes the design, interfaces, cache strategies, and model versioning for the Vector Embedding subsystem.

---

## 1. Core Interfaces

* **`EmbeddingProvider`**: Concrete interface to query model vectors. Allows plugging future providers (like local Ollama, cloud OpenAI/Gemini, offline SentenceTransformers).
* **`EmbeddingService`**: Unified manager that maps providers to logical names and coordinates execution.
* **`EmbeddingVersionManager`**: Compares vector model hashes and flags index schemas when active configurations change.

---

## 2. In-Memory Vector Cache

To avoid expensive network API round-trips and CPU bottlenecks during recurring search queries:
* **Implementation**: `EmbeddingCacheImpl`.
* **Key Generation**: Concatenates active model version tags with raw text content strings (`version:text`).
* **Cache Eviction**: Supports manual invalidation (`invalidate`) and complete cache cleaning (`clear`).
* **Telemetry**: Measures hits, misses, and rolling hit ratio.

---

## 3. Migration Strategy

When the system configuration switches active embedding models:
1. `EmbeddingVersionManager` detects the version hash mismatch.
2. The system triggers a background migration job.
3. Raw documents are read from PostgreSQL, generated into new vector formats using the active model, and upserted into Qdrant.
