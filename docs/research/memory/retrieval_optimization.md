# Retrieval Optimization Spec
**Sprint 11 · Milestone 5** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define hybrid search query parameters, Reciprocal Rank Fusion (RRF) constants, and Redis caching policies for research retrieval.
* **Scope**: Governs Qdrant search setups, SQLite ranking filters, and Redis caches.
* **Audience**: Search Engineers, DBAs, and System Architects.
* **Related Documents**:
  * [workspace/orchestration/context_management.md](file:///Users/anzarakhtar/aios/docs/workspace/orchestration/context_management.md) - Context sizing.
  * [research/integration_strategy.md](file:///Users/anzarakhtar/aios/docs/research/integration_strategy.md) - Vector settings.

---

## 1. Hybrid Search (RRF) & Relevance Rankings

To retrieve relevant context for research queries:
* **Hybrid Queries**: Fuses keyword searches (using SQLite FTS5 BM25 ranks) and vector similarities (using Qdrant cosine distance) using **Reciprocal Rank Fusion (RRF)**:
  $$\text{RRF Score}(d) = \sum_{m \in M} \frac{1}{60 + r_m(d)}$$
  (where $r_m(d)$ is the rank of document $d$ in search method $m$).
* **Relevance Filter**: Returns only results with RRF scores exceeding **0.02** and Qdrant similarity scores exceeding **0.78**.

---

## 2. Redis Query Cache Configuration

To speed up repeated query lookups:
* **Key Format**: `research:query:[sha256_query_hash]`
* **TTL Settings**: Caches search results for **3600 seconds (1 hour)**, reducing latency to **< 1ms** on cache hits.
* **Active Invalidation**: If the local database is updated, the system invalidates the corresponding Redis namespaces.

---

## 3. OmniRoute Offline Context Failover

* **Local Offline Path**: If `offline_mode` is enabled or the network connection drops, OmniRoute redirects queries to the local SQLite cache and Qdrant replica, preventing connection errors.
* **Context Compression**: Trims long code blocks and strips boilerplate text before injecting results into prompts, keeping token counts within limits.
