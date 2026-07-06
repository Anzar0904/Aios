# Research Memory Model Spec
**Sprint 11 · Milestone 5** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define data mappings and collection specifications for long-term research memory storage.
* **Scope**: Governs SQL tables, Qdrant memory collections, and cache indices.
* **Audience**: DBAs, Search Engineers, and AI developers.
* **Related Documents**:
  * [research/architecture.md](file:///Users/anzarakhtar/aios/docs/research/architecture.md) - Database architecture.
  * [research/validation/evidence_graph.md](file:///Users/anzarakhtar/aios/docs/research/validation/evidence_graph.md) - Evidence graph.

---

## 1. Long-Term Storage Integration

The **Research Memory** system coordinates relational and vector databases to store technical facts:

```
                  +-----------------------------------+
                  |         MemoryManager             |
                  +-----------------------------------+
                    /                               \
                   v                                 v
       +---------------+                     +---------------+
       | SQLite Cache  |                     | Qdrant Vector |
       | (SQLCipher)   |                     |     Index     |
       +---------------+                     +---------------+
        - Documents                           - Fact embeddings
        - Citation offsets                    - Cosine similarities
        - Version ledger                      - Metadata payloads
```

* **Relational Storage (SQLite/PostgreSQL)**: Stores document layouts, citation offsets, version ledgers, and raw content hashes.
* **Semantic Storage (Qdrant)**: Stores fact embeddings, metadata payloads, and cosine similarity indexes in the `research_memory` collection.

---

## 2. Qdrant Memory Collection Settings

The `research_memory` collection is configured with the following settings:
* **Dimensions**: 384 dimensions.
* **Distance**: Cosine.
* **Payload Fields**:
  ```json
  {
    "workspace_id": "profile_hash_value",
    "source": "research",
    "concept_name": "RRF Hybrid Search",
    "fact_id": "fact_uuid_value",
    "text_content": "Fuses keyword rank and vector similarity using k=60 RRF."
  }
  ```
* **Payload Indexes**: `workspace_id`, `concept_name`, and `fact_id` are explicitly indexed in Qdrant, enabling sub-10ms similarity searches under specific workspace scopes.
