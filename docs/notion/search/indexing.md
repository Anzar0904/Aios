# Notion Intelligence — Lexical Indexing Specification
**Sprint 9 · Milestone 4** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define database indexing mechanisms, SQLite FTS5 schemas, virtual table models, and text indexes.
* **Scope**: Governs Python database indexers, FTS5 migration triggers, and lexical search engines.
* **Audience**: DBAs, Backend Developers, and AI coding agents.
* **Related Documents**:
  * [notion/data_model/page_model.md](file:///Users/anzarakhtar/aios/docs/notion/data_model/page_model.md) - Page representations.
  * [notion/search/README.md](file:///Users/anzarakhtar/aios/docs/notion/search/README.md) - Search navigation hub.

---

## 1. Local Lexical Indexing Strategy

While vector embeddings are essential for semantic searches, standard keywords, code function identifiers, and specific tags require exact-match query searches. 

To achieve sub-millisecond keyword searches locally, the Personal AI OS replicates Notion page body text and metadata properties inside a **SQLite Full-Text Search (FTS5)** virtual database index.

---

## 2. SQLite FTS5 Schema

The local relational database defines a virtual index, `notion_pages_fts`, backed by SQLite's FTS5 extension:

```sql
-- Virtual Table mapping for Full-Text Search
CREATE VIRTUAL TABLE IF NOT EXISTS notion_pages_fts USING fts5(
    document_id,
    workspace_id,
    title,
    content,
    properties_flat,
    content_pin DEFAULT 'UNPINNED',
    tokenize="porter unicode61"
);

-- Relational table to store structural triggers
CREATE TABLE IF NOT EXISTS notion_indexing_logs (
    index_id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id TEXT NOT NULL,
    indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tokens_count INTEGER,
    index_type TEXT CHECK(index_type IN ('FTS5', 'QDRANT', 'BOTH')) NOT NULL
);
```

### Tokenizer Settings
* **`unicode61`**: Guarantees correct word parsing for emojis and non-English scripts.
* **`porter`**: Enforces Porter Stemming algorithms, mapping suffixes to root word keys (e.g. searching for `running` matches matches for `run` or `runs`).

---

## 3. Index Updating & Maintenance

To keep database queries fast:
* **Asynchronous Updates**: When the sync engine pulls a changed page, the raw text is compiled and written to the SQLite cache. The FTS5 virtual table is updated inside a background database transaction.
* **Transaction Safe**: Writes to `notion_pages_fts` are wrapped in relational transactions matching `SyncStateStore` changes, preventing orphan index logs.
* **Keyword Matching Execution**:
  ```sql
  SELECT document_id, bm25(notion_pages_fts) AS rank
  FROM notion_pages_fts
  WHERE notion_pages_fts MATCH 'auth* AND loopback'
  ORDER BY rank ASC
  LIMIT 10;
  ```
