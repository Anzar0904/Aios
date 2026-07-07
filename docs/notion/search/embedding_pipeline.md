# Notion Intelligence — Embedding Pipeline Specification
**Sprint 9 · Milestone 4** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define the embedding generation pipeline, local model setups, text pre-processing, chunking bounds, and thread worker queues.
* **Scope**: Governs Python embedding client adapters, chunk splitting classes, and concurrency runtimes.
* **Audience**: Systems Developers, Performance Engineers, and AI architects.
* **Related Documents**:
  * [notion/search/semantic_memory.md](file:///Users/anzarakhtar/aios/docs/notion/search/semantic_memory.md) - Qdrant collection settings.
  * [docs/persistence/EMBEDDING_ENGINE_ARCHITECTURE.md](file:///Users/anzarakhtar/aios/docs/persistence/EMBEDDING_ENGINE_ARCHITECTURE.md) - Core system embedding configs.

---

## 1. Local Embedding Model Specification

In alignment with the [Project Constitution](file:///Users/anzarakhtar/aios/docs/00_PROJECT_VISION.md)'s privacy mandates, **embeddings are generated locally, with zero external network dependencies**.

* **Model**: `all-MiniLM-L6-v2` (from the Sentence Transformers family).
* **Dimensions**: 384 dimensions.
* **Metric**: Cosine similarity.
* **Execution Engine**: Loaded via PyTorch or ONNX Runtime locally.
* **Fallback Routing**: If the local HuggingFace cache is unavailable at startup, the system routes queries to a local Ollama service (`nomic-embed-text` endpoint) before flagging connection errors.

---

## 2. Text Pre-Processing & Chunking

To preserve search context, page body text is split using a structural chunking parser:

```
                  +----------------------------------+
                  |        Notion Page Text          |
                  +----------------------------------+
                                   |
                                   v
                  +----------------------------------+
                  |      Clean Markdown AST          |
                  +----------------------------------+
                                   |
                                   v
                  +----------------------------------+
                  |       Structural Chunking        |
                  |  - Size: 500 Tokens Max          |
                  |  - Overlap: 50 Tokens            |
                  |  - Preserves H1/H2/H3 Paths      |
                  +----------------------------------+
```

### Chunk Format
Each chunk is prefixed with structural metadata to maintain context when embedded:
```
Page Title: Notion Integration Design
Section Path: # Architecture Specification -> ## High-Level Architecture
---
[Paragraph content block text...]
```

---

## 3. Concurrency & Pipeline Thread Pool

Embedding generation is a CPU-intensive operation. To prevent thread contention and keep the REPL interface responsive:

* **Worker Queue**: The `NotionSemanticIndexer` submits chunk processing requests to a dedicated background task queue (`notion_embedding_workers`).
* **Concurrency Bounds**: Thread executions are restricted by a CPU pool worker count:
  $$\text{Workers} = \max(1, \text{CPU\_Cores} - 2)$$
  * *Note: Leaves two CPU cores free to handle REPL interface rendering and LLM provider stream tasks.*
* **Execution Timeout**: A timeout threshold of **30 seconds** is enforced for each batch. If a batch fails or times out, it is returned to the queue and retried with exponential back-off.
