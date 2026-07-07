# Notion Intelligence — Memory Integration
**Sprint 9 · Milestone 6** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define tiered memory coordination, vector embedding synchronization, and memory hierarchy mappings.
* **Scope**: Governs memory storage connectors, vector indexing pipelines, and query builders.
* **Audience**: Systems Architects, AI Developers, and Database DBAs.
* **Related Documents**:
  * [notion/search/semantic_memory.md](file:///Users/anzarakhtar/aios/docs/notion/search/semantic_memory.md) - Qdrant collection mappings.
  * [docs/16_ENGINEERING_BIBLE.md](file:///Users/anzarakhtar/aios/docs/16_ENGINEERING_BIBLE.md) - Tiered memory system.

---

## 1. Memory Tier Alignment

The Personal AI OS categorizes data into three memory tiers. The Notion Intelligence module integrates directly into this tiered hierarchy:

```
+-----------------------------------------------------------------------------------+
|                           MEMORY TIER ALIGNMENT                                   |
+------------------------+---------------------------------+------------------------+
| Memory Tier            | Target Data Types               | Storage Provider       |
+------------------------+---------------------------------+------------------------+
| Permanent Memory       | Core project scope files,       | Local SQLite cache +   |
|                        | career profile dashboards.      | Notion cloud replica.  |
+------------------------+---------------------------------+------------------------+
| Long-Lived Memory      | Synced wiki pages, API docs,    | Qdrant vector database |
|                        | code review logs (1-3 years).   | (`knowledge_memory`).  |
+------------------------+---------------------------------+------------------------+
| Short-Lived Memory     | Session tasks lists, transient  | Local Redis cache      |
|                        | comment updates (days/weeks).   | namespaces.            |
+------------------------+---------------------------------+------------------------+
```

---

## 2. Synchronization-Driven Memory Updates

To maintain consistency:
* **Background Sync**: The scheduler triggers incremental sync tasks. Retrieved text content updates the local SQLite cache and is re-indexed in Qdrant.
* **Context Loading**: When the `MemoryService` loads context for user queries, it performs parallel lookups across local files and the synced Notion vector database.
* **Memory Pruning**: When a document is disconnected or its credentials are deleted, the corresponding records are purged from both SQLite and Qdrant caches (see [notion/search/sync_indexing.md](file:///Users/anzarakhtar/aios/docs/notion/search/sync_indexing.md)).

---

## 3. Query Scoping and Context Filtering

To prevent context dilution (where search results are flooded with irrelevant notes), retrieval queries are scoped using metadata filters:

```python
class NotionMemoryConnector:
    def retrieve_memory_blocks(self, query: str, active_workspace_id: str) -> List[str]:
        # Step 1: Query vector memory with workspace keyword filters
        search_hits = qdrant_client.search(
            collection_name="knowledge_memory",
            query_vector=embedding_service.embed(query),
            query_filter=models.Filter(
                must=[
                    models.FieldCondition(key="source", match=models.MatchValue(value="notion")),
                    models.FieldCondition(key="workspace_id", match=models.MatchValue(value=active_workspace_id))
                ]
            ),
            limit=5
        )
        
        # Step 2: Format results as text blocks for the prompt context
        return [hit.payload["text_content"] for hit in search_hits]
```
