# Workspace Memory Integration Spec
**Sprint 10 · Milestone 6** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define database schemas and vector mappings for workspace metadata and development history.
* **Scope**: Governs SQLite caches, Qdrant collection mappings, and Memory Service synchronization.
* **Audience**: DBAs, Search Engineers, and AI developers.
* **Related Documents**:
  * [workspace/codebase/symbol_index.md](file:///Users/anzarakhtar/aios/docs/workspace/codebase/symbol_index.md) - Symbol indexing configurations.
  * [workspace/source_control/repository_history.md](file:///Users/anzarakhtar/aios/docs/workspace/source_control/repository_history.md) - History mappings.

---

## 1. Local Workspace Index

The workspace memory maps structural development assets across both relational and vector stores.

### 1.1 SQLite Metadata Cache
Tracks project scopes, file configurations, and local task logs:
```sql
CREATE TABLE IF NOT EXISTS workspace_indices (
    index_id TEXT PRIMARY KEY,
    workspace_id TEXT NOT NULL,
    entity_type TEXT CHECK(entity_type IN ('WORKSPACE', 'PROJECT', 'REPOSITORY', 'PACKAGE', 'MODULE', 'FILE', 'SYMBOL', 'KNOWLEDGE_NODE')) NOT NULL,
    entity_name TEXT NOT NULL,
    parent_entity_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(parent_entity_id) REFERENCES workspace_indices(index_id) ON DELETE CASCADE
);
```

---

## 2. Qdrant Vector Integration

Source symbols, markdown documentation, and git commits are embedded and synced to Qdrant:
* **Collection Name**: `workspace_memory`
* **Configuration**:
  * Dimensions: **384** (matching the local `all-MiniLM-L6-v2` model).
  * Distance: **Cosine**.
* **Payload Fields**:
  ```json
  {
    "workspace_id": "ws_hash_value",
    "source": "workspace",
    "file_path": "core/src/aios/services/approval_impl.py",
    "symbol_name": "evaluate_consensus",
    "symbol_type": "METHOD",
    "text_content": "def evaluate_consensus(self, release_page): ...",
    "breadcrumbs": "Workspace / Core / approval_impl.py / evaluate_consensus"
  }
  ```

---

## 3. Memory Sync Pipeline

To keep local memory in sync with changes in the workspace:
1. **Incremental Updates**: File edits trigger background AST re-indexing and update the corresponding Qdrant vectors.
2. **Commit Records**: When code is committed, Git commit logs and diff summaries are indexed to Qdrant.
3. **Execution Summaries**: Test runs and build diagnostics are indexed to SQLite and Qdrant as temporary run context.
