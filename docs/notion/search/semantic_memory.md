# Notion Intelligence — Semantic Memory Vector Storage
**Sprint 9 · Milestone 4** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define the Qdrant vector schema mapping, payload parameters, indexing optimizations, and query constraints.
* **Scope**: Governs Qdrant collections settings, index parameters, and Python vector repositories.
* **Audience**: Systems DBAs, Backend Developers, and AI coding agents.
* **Related Documents**:
  * [notion/search/embedding_pipeline.md](file:///Users/anzarakhtar/aios/docs/notion/search/embedding_pipeline.md) - Embedding pipeline.
  * [docs/persistence/QDRANT_PLATFORM_ARCHITECTURE.md](file:///Users/anzarakhtar/aios/docs/persistence/QDRANT_PLATFORM_ARCHITECTURE.md) - Core vector DB architecture.

---

## 1. Vector Database Collection Mapping

The Personal AI OS uses **Qdrant** as its primary vector memory engine. Notion page chunks are stored in a dedicated collection:

* **Collection Name**: `knowledge_memory`
* **Vector Configuration**:
  ```json
  {
    "vector_size": 384,
    "distance": "Cosine"
  }
  ```
  * *Note: Standardized on 384 dimensions to match the `all-MiniLM-L6-v2` Sentence Transformer running locally.*

---

## 2. Qdrant Payload Schema

Each point in the `knowledge_memory` collection represents a single page chunk. Points are tagged with metadata payloads to enable precise filtering before running search queries.

```json
{
  "id": "c71a39f1-ef07-4bc2-af8b-59da10fa22b1",
  "vector": [0.015, -0.048, 0.122, "... (384 values)"],
  "payload": {
    "document_id": "notion_8f8bca12-efd8-4ba3-bfd0-cd1712a4501a",
    "source": "notion",
    "workspace_id": "8f8bca12-efd8-4ba3-bfd0-cd1712a4501a",
    "parent_id": "9a38c11a-0fd7-4bca-8eb1-59da10faaea1",
    "title": "Notion Integration Design",
    "url": "https://www.notion.so/Notion-Integration-Design-8f8bca...",
    "chunk_index": 0,
    "total_chunks": 4,
    "last_modified": "2026-07-06T18:49:00+00:00",
    "text_content": "This document defines the sync state machine..."
  }
}
```

---

## 3. Payload Optimizations (Index Fields)

To keep query latencies under 10ms when searching millions of vectors, the system registers **Qdrant Payload Indexes**:

```python
# Register payload indexes in Qdrant during collection creation
qdrant_client.create_payload_index(
    collection_name="knowledge_memory",
    field_name="source",
    field_schema=models.PayloadSchemaType.KEYWORD
)

qdrant_client.create_payload_index(
    collection_name="knowledge_memory",
    field_name="workspace_id",
    field_schema=models.PayloadSchemaType.KEYWORD
)

qdrant_client.create_payload_index(
    collection_name="knowledge_memory",
    field_name="document_id",
    field_schema=models.PayloadSchemaType.KEYWORD
)
```

---

## 4. Query & Filter Mechanics

When retrieving context matching a user query:
1. The user's query is converted to an embedding.
2. The search is run against Qdrant, filtering by the active workspace and provider source:
   ```python
   qdrant_client.search(
       collection_name="knowledge_memory",
       query_vector=query_embedding,
       query_filter=models.Filter(
           must=[
               models.FieldCondition(key="source", match=models.MatchValue(value="notion")),
               models.FieldCondition(key="workspace_id", match=models.MatchValue(value=active_workspace_id))
           ]
       ),
       limit=10,
       score_threshold=0.75  # Filter out low-similarity hits
   )
   ```
