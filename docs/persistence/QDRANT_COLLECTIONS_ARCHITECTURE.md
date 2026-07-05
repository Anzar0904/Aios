# Qdrant Collections Architecture

This document describes the collections layout, HNSW parameters, indexing strategy, and pre-filtering payloads setup for the Vector Platform.

---

## 1. Schema Validation and Indexing

On system startup, each of the 9 vector repositories performs automatic checks:
1. **Existence Verification**: Verifies the collection exists. If not, creates it.
2. **Quantization Setup**: Configures Scalar Int8 quantization (if enabled).
3. **Payload Indexing**: Registers keyword payload indices on standard pre-filtering attributes to optimize query response latencies.

---

## 2. Dynamic Payload Schemes

All collections share a consistent metadata scheme:
* `workspace_id` (Keyword index)
* `project_id` (Keyword index)
* `session_id` (Keyword index)
* `user_id` (Keyword index)
* `document_id` (Keyword index)
* `memory_type` (Keyword index)
* `tags` (Keyword index)
* `importance` (Integer index)
* `created_at` (Float index)
* `updated_at` (Float index)
* `embedding_version` (Keyword index)
