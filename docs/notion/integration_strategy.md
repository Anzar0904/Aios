# Notion Intelligence — Integration Strategy
**Sprint 9 · Milestone 1 (Foundation)** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define the synchronization strategies, semantic indexing pipeline, and offline-first queueing patterns for Notion Intelligence.
* **Scope**: Standardizes runtime indexing logic, background syncing, and database cache patterns.
* **Audience**: Systems Architects, DBAs, and Integration Engineers.
* **Related Documents**:
  * [02_ARCHITECTURE_GUIDELINES.md](file:///Users/anzarakhtar/aios/docs/02_ARCHITECTURE_GUIDELINES.md) - Service design principles.
  * [notion/architecture.md](file:///Users/anzarakhtar/aios/docs/notion/architecture.md) - SQLite replica schema definitions.

---

## 1. Synchronization Protocols

Synchronization is key to keeping the local AI OS and remote Notion workspaces aligned. The system uses a hybrid synchronization model:

```
+------------------+----------------------------------+------------------------------------+
| Sync Mode        | Trigger Mechanism                | Typical Use Case                   |
+------------------+----------------------------------+------------------------------------+
| On-Demand Sync   | Event triggers from local        | Pushing release reports, test      |
|                  | services or user REPL requests.  | metrics, and review approvals.     |
+------------------+----------------------------------+------------------------------------+
| Incremental Sync | Scheduled cron jobs managed      | Updating local vector storage and  |
| (Pull)           | by the Memory Service.           | catching changes to task boards.   |
+------------------+----------------------------------+------------------------------------+
| Full Rebuild     | Manual recovery commands.        | Initial setup or resolving cache   |
|                  |                                  | inconsistencies.                   |
+------------------+----------------------------------+------------------------------------+
```

### 1.1 Incremental Sync Loop (Pull Flow)
To optimize network bandwidth and stay within Notion API limits:
1. **Fetch Modifications**: Query the Notion Search API filtered by `last_edited_time` greater than the latest local database sync timestamp:
   ```json
   {
     "filter": {
       "value": "page",
       "property": "object"
     },
     "sort": {
       "direction": "descending",
       "timestamp": "last_edited_time"
     }
   }
   ```
2. **Compute Diffs**: Compare the remote `last_edited_time` and remote MD5 block hash against the records in the local `SyncStateStore`.
3. **Pull Changes**: Download changed pages, parse the block AST, update the local SQLite replica, and trigger the Semantic Indexing Pipeline.

---

## 2. Semantic Indexing Pipeline

Documents synchronized from Notion must be converted into searchable embeddings within the local Qdrant database. This is handled by the **NotionSemanticIndexer**:

```
 [Notion Page AST]
         |
         v
 [Clean Markdown Text]
         |
         v
 [Chunking Parser]  ====> (Metadata: Title, URL, Parent Pages, Authors)
         |
         v
 [Sentence Embeddings]  ====> (Local Model: all-MiniLM-L6-v2, 384-dimensions)
         |
         v
 [Qdrant Vector Database]  ====> (Collection: knowledge_memory)
```

### 2.1 Chunking Strategy
Instead of indexing a whole page as a single block of text (which loses local context), the indexer uses a structural chunking parser:
* **Parent-Child Hierarchy Mapping**: Paragraphs, lists, and tables are grouped under their nearest heading (H1/H2/H3) block parent.
* **Size Limits**: Target chunk size is **500 tokens** with a **50-token overlap** (using the `tiktoken` CL100K tokenizer).
* **Metadata Attachment**: Every chunk is tagged with its parent page ID, title, Notion URL, authors, last modified date, and block path hierarchy.

### 2.2 Semantic Vector Retrieval
1. **Query**: The user searches via the REPL console: `"What were the key takeaways from the retrospective?"`
2. **Embed Query**: Embed the query string using the local Sentence Transformer model.
3. **Search Qdrant**: Run a Cosine Similarity search on the `knowledge_memory` collection:
   ```python
   qdrant_client.search(
       collection_name="knowledge_memory",
       query_vector=query_embedding,
       limit=5,
       query_filter=models.Filter(
           must=[
               models.FieldCondition(
                   key="metadata.source",
                   match=models.MatchValue(value="notion")
               )
           ]
       )
   )
   ```

---

## 3. Offline-First Operations

To support local-first operations, the Notion Intelligence module treats the network as an intermittent channel. 

### 3.1 SQLite Replica Cache
The SQLite database stores local replicas of remote pages. The system queries this cache first, enabling sub-millisecond retrieval speeds without any network latency.

### 3.2 Offline Mutation Queueing
When the OS attempts a write (e.g. updating a task card status or logging a test run) and detects that the network is unavailable:
1. **Write Local**: Update the SQLite cache, marking the page status as `MUTATED_LOCAL`.
2. **Queue Write**: Write the mutation payload to the `offline_write_queue` database.
3. **Reconcile Automatically**: When the system detects the network is back online:
   * Read the mutation queue sequentially.
   * Send requests to the Notion API.
   * On success, remove items from the queue and set the SQLite status to `SYNCED`.
   * On failure (due to conflicts), trigger the conflict resolution policy.
