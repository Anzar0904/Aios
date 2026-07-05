# Embedding Engine Architecture

This document describes the design patterns, provider abstractions, and retry execution mechanisms of the Embedding Engine.

---

## 1. Engine Architecture

The `EmbeddingEngineImpl` coordinates embedding creation, checking the local `EmbeddingCache` to prevent duplicate calculations, validating outputs, and logging telemetry.

```text
+-------------------------------------------------------------+
|                     EmbeddingEngine                         |
+-------------------------------------------------------------+
                                │
          ┌─────────────────────┴─────────────────────┐
          ▼                                           ▼
+───────────────────+                       +───────────────────+
|  EmbeddingCache   |                       | EmbeddingService  |
+───────────────────+                       +───────────────────+
                                                      │
                                                      ▼
                                            +───────────────────+
                                            | EmbeddingProvider |
                                            +───────────────────+
```

---

## 2. Decoupled Provider Plugins

All providers implement the `EmbeddingProvider` interface:
* **MockEmbeddingProvider**: Default provider for local verification.
* **SentenceTransformerProvider**: CPU fallback provider using the local `sentence-transformers` library.
* **Cloud Abstractions**: Interface placeholders for `OpenAIProvider`, `GeminiProvider`, and `OllamaProvider`.

---

## 3. Database Retry Queue

If embedding generation fails, requests are stored in the `pending_embedding_jobs` table in PostgreSQL. A daemon thread calls `run_retry_cycle()` periodically to re-attempt execution and clear successful transactions.
