# Qdrant Platform Architecture Discovery Report

This report outlines the proposed architecture, collection strategies, embedding models abstractions, search patterns, and production validation plans for the Qdrant Platform in Sprint 6 of the Personal AI OS.

---

## 1. Executive Architecture Summary

The Qdrant Platform acts as the **semantic memory and vector search layer** for the Personal AI OS. It manages vector embeddings, semantic storage, similarity lookups, and metadata filtering.

### Separation of Platform Responsibilities:
* **PostgreSQL**: The permanent source of truth for all structured data (users, projects, workspaces, conversation logs, etc.).
* **Redis**: The runtime state acceleration, session registry cache, lock coordinator, and execution rate limiter.
* **Qdrant**: The vector index and semantic retriever. It does *not* replace PostgreSQL. All raw texts, source items, and transactional histories are persisted in PostgreSQL. Qdrant stores the text chunks, their dense vector representations, and metadata payload filters.

If Qdrant is unavailable, the system degrades gracefully by falling back to PostgreSQL lexical substring lookups (`LIKE` queries) and metadata filtering.

---

## 2. Existing Component Analysis & Integration Points

The active Personal AI OS codebase contains several modules that will naturally integrate with Qdrant:
* **Memory Service (`aios.services.memory`)**: Currently uses `LocalJSONMemoryStorage`. The concrete implementation `LocalMemoryService` will delegate to `QdrantProvider` to index and retrieve memory vectors.
* **Context Service (`aios.services.context`)**: Provides active workspace/project details. Qdrant queries will use these variables to perform strict pre-filtering (e.g. `workspace_id == active_workspace_id`).
* **OmniRoute (`aios.services.model_impl`)**: Resolves active LLM providers. It can evaluate context windows and use Qdrant semantic memory to append relevant context while avoiding prompt inflation.
* **Runtime Intelligence (`aios.services.persistence_impl`)**: Collects query statistics and profiles transaction latencies. It will wire with Qdrant telemetry to record semantic query latencies and vector count growth.

---

## 3. Qdrant Responsibility Boundaries

| Feature | Qdrant Responsibility | PostgreSQL Responsibility | Redis Responsibility |
| :--- | :--- | :--- | :--- |
| **Vector Storage** | Vector arrays, dense indexes | None | None |
| **Document Text Chunks** | Text payloads inside vector points | Complete, un-chunked document bodies | None |
| **Metadata Filtering** | pre-filters (workspace, project, tags) | Complex relational queries, SQL joins | Fast keyspace lookups |
| **Retrieval State** | Similarity scoring, Top-K candidates | Full-text query fallbacks | Cached lookup results |

---

## 4. Collection Strategy

To prevent cross-talk and maintain clean domain separation, we propose 9 distinct collections. Each collection will use `cosine` distance metric and be configured dynamically with dimensions matching the active embedding model.

### Collections:
1. **Engineering Memory**: Commits, reviews, technical debt tracking, coding standards.
2. **Workspace Memory**: Workspace configurations, active file structures, active directory logs.
3. **Project Memory**: Active project targets, issues, roadmaps, sprint definitions.
4. **Documentation Memory**: System specifications, PRDs, guides, codebooks, API docs.
5. **Conversation Memory**: Historical dialog turns, user query history, summarizations.
6. **Automation Memory**: n8n workflows, triggers, automation logs.
7. **Provider Memory**: AI provider configurations, cost estimation, capabilities.
8. **Research Memory**: Literature documents, web search notes, research trails.
9. **Future Knowledge Memory**: User preferences, learned facts, dynamic heuristics.

### Payload Schema:
```json
{
  "id": "uuid-string-of-point",
  "workspace_id": "workspace-123",
  "project_id": "project-456",
  "category": "conversation",
  "timestamp": 1783259272.66,
  "content": "Raw text chunk content here...",
  "tags": ["redis", "sprint-5"],
  "importance": 2,
  "additional_metadata": {}
}
```

### Indexing Strategy:
* **Vector Index**: HNSW index on the dense vector field (`cosine` distance).
* **Payload Fields Indexing**: Keyword indexes on `workspace_id`, `project_id`, `category`, and `tags` to allow low-latency pre-filtering. Numerical range index on `timestamp` for time-bounded queries.

---

## 5. Embedding Strategy

The system will decouple vector generation from the underlying service:
* **Embedding Interface**: `EmbeddingService` interface with `embed_text(text: str) -> List[float]` and `embed_batch(texts: List[str]) -> List[List[float]]`.
* **Embedding Model Versioning**: Vector payloads will include `embedding_model` and `embedding_model_version`.
* **Dimensions**: Configured per collection. Default dimensions range from 384 (local `all-MiniLM-L6-v2`) to 1536 (cloud `text-embedding-3-small`).
* **Migrations**: Parallel collections will be created when the active model changes, and a background task will re-embed records from PostgreSQL.
* **Compatibility**: Supports local offline execution (via SentenceTransformers library) and cloud endpoints (OpenAI / OpenRouter).

---

## 6. Search Capabilities

* **Semantic Search**: Top-K retrieval based on cosine similarity of text embeddings.
* **Similarity Search**: Direct document-to-document nearest neighbor matching.
* **Hybrid Search**: Pre-filtering using keyword metadata values (workspace, project, category) combined with dense semantic search.
* **Cross-memory Search**: Union querying across multiple collections.
* **Top-K & Score Thresholds**: Bound candidate list length (`limit`) and ignore points below a minimum relevance threshold (e.g. `score < 0.7`).
* **Reranking Hook**: Placeholders for future reranking layers (cross-encoders).

---

## 7. Failure Recovery Strategy

* **Graceful Degradation**: If Qdrant becomes unavailable, semantic lookups are bypassed. The `MemoryService` falls back to querying PostgreSQL via lexical substring matches.
* **No Data Loss**: Transactions are always written to PostgreSQL. When indexing to Qdrant fails, a record is marked as `pending_index` in PostgreSQL, enabling background synchronization when the service returns.
* **Auto-Reconnect**: Connection manager retries connections using exponential backoffs.

---

## 8. Engineering Learning Strategy

Qdrant provider telemetry will collect:
* Search performance and accuracy indices.
* Dimension drift statistics.
* Average query latencies.
* HNSW graph construction times.
