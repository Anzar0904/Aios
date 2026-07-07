# Notion Intelligence — Sync-Aware Indexing
**Sprint 9 · Milestone 4** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define sync-aware indexing updates, chunk deletions, vector pruning routines, and transaction alignments.
* **Scope**: Governs Python index managers, sync observers, and vector database cleanup scripts.
* **Audience**: Backend Engineers, QA Testers, and Database Architects.
* **Related Documents**:
  * [notion/integration_strategy.md](file:///Users/anzarakhtar/aios/docs/notion/integration_strategy.md) - General sync strategies.
  * [notion/search/semantic_memory.md](file:///Users/anzarakhtar/aios/docs/notion/search/semantic_memory.md) - Qdrant collection mappings.

---

## 1. Index Lifecycle Sync

Because external Notion workspaces are dynamic, the local vector indexes must update and prune entries in step with remote changes. 

The `NotionSyncEngine` coordinates with the `NotionSemanticIndexer` to run index updates alongside changes to the local SQLite database cache.

```
 [NotionSyncEngine Pull] ===> Detects Changes (Created, Modified, Deleted)
                                      |
                     [Evaluate Document Change States]
                     /                |                \
                    v                 v                 v
               [Page Created]   [Page Modified]   [Page Deleted]
                    |                 |                 |
                    v                 v                 v
               [Add Chunks]     [Prune Chunks &   [Delete All matching
                                 Add New Chunks]   document_id]
```

---

## 2. Index Operations

### 2.1 Creation Indexing
When a new page is synced:
1. Parse the page's block tree and generate chunks.
2. Compute embeddings and write points to Qdrant's `knowledge_memory` collection.
3. Insert page body text into the SQLite `notion_pages_fts` table.
4. Log the indexing event in `notion_indexing_logs`.

### 2.2 Modification Re-Indexing
When an existing page is edited, its block structure changes. This invalidates all previously generated vector chunks for that page:
1. Delete all existing points matching the page's ID from Qdrant:
   ```python
   # Prune existing points before inserting new chunks
   qdrant_client.delete(
       collection_name="knowledge_memory",
       points_selector=models.FilterSelector(
           filter=models.Filter(
               must=[
                   models.FieldCondition(
                       key="document_id",
                       match=models.MatchValue(value=f"notion_{page_id}")
                   )
               ]
           )
       )
   )
   ```
2. Delete the matching row in `notion_pages_fts`.
3. Process the new block structure, generate new chunks, compute embeddings, and insert the updated records into Qdrant and FTS5.
4. Update the sync database record timestamp.

### 2.3 Deletion Indexing (Pruning)
When a page is deleted in the remote Notion workspace:
1. Delete all points matching the page ID from Qdrant.
2. Delete the matching row in `notion_pages_fts`.
3. Update the local SQLite sync state table, marking the document status as `REVOKED` or deleting the record completely.

---

## 3. Transaction Safety (Relational Alignment)

To prevent index drift where vectors remain in Qdrant but are missing from SQLite, the system runs index operations inside a **Unit of Work** pattern:
* If writing to Qdrant fails due to connection issues, the SQLite sync cache modifications are rolled back.
* The index state is marked as `DIRTY` in the database, and the page is queued for re-processing during the next synchronization cycle.
