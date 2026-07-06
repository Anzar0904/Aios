# Symbol Database & Vector Indexing Spec
**Sprint 10 · Milestone 3** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define database schemas, Qdrant vector layouts, payload filters, and Redis caching policies for indexing code symbols.
* **Scope**: Governs SQL definitions, vector dimensions, and lookup caching rules.
* **Audience**: DBAs, Backend Developers, and System Architects.
* **Related Documents**:
  * [workspace/architecture.md](file:///Users/anzarakhtar/aios/docs/workspace/architecture.md) - Storage and architecture components.
  * [workspace/codebase/ast_analysis.md](file:///Users/anzarakhtar/aios/docs/workspace/codebase/ast_analysis.md) - AST parsing scopes.

---

## 1. Relational Database Symbol Schemas

AST-extracted code symbols are cached in PostgreSQL/SQLite for fast structural queries.

```sql
CREATE TABLE IF NOT EXISTS codebase_symbols (
    symbol_id TEXT PRIMARY KEY,
    workspace_id TEXT NOT NULL,
    file_path TEXT NOT NULL,
    symbol_name TEXT NOT NULL,
    symbol_type TEXT CHECK(symbol_type IN ('CLASS', 'METHOD', 'FUNCTION', 'STRUCT', 'VARIABLE')) NOT NULL,
    start_line INTEGER NOT NULL,
    end_line INTEGER NOT NULL,
    docstring TEXT,
    signature TEXT NOT NULL,
    is_exported INTEGER CHECK(is_exported IN (0, 1)) NOT NULL,
    FOREIGN KEY(workspace_id) REFERENCES workspaces(workspace_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_symbols_name_type ON codebase_symbols(symbol_name, symbol_type);
CREATE INDEX IF NOT EXISTS idx_symbols_workspace ON codebase_symbols(workspace_id);
```

---

## 2. Qdrant Semantic Memory Indexing

To resolve semantic code queries (e.g. "where is the approval consensus evaluated?"), symbols are embedded and saved to Qdrant:
* **Collection Name**: `workspace_memory`
* **Configuration**:
  * Vector dimensions: **384** (matching `all-MiniLM-L6-v2` locally).
  * Distance metric: **Cosine**.
* **Payload Fields**:
  ```json
  {
    "workspace_id": "ws_hash_value",
    "source": "workspace",
    "file_path": "core/src/aios/services/approval_impl.py",
    "symbol_name": "evaluate_consensus",
    "symbol_type": "METHOD",
    "breadcrumbs": "ApprovalEngine / evaluate_consensus",
    "text_content": "def evaluate_consensus(self, release_page): ..."
  }
  ```
* **Payload Indices**: `workspace_id`, `symbol_name`, and `symbol_type` are indexed in Qdrant, enabling sub-10ms similarity searches under specific workspace scopes.

---

## 3. Redis Cache & Invalidation Policies

For high-speed REPL and editor auto-completion support, symbol lookup queries are cached in **Redis**:
* **Query Cache Key**: `workspace:ws_hash_value:symbol:symbol_name`
* **Cache TTL**: **900 seconds** (15 minutes).
* **Active Invalidation Loop**: When a file update occurs:
  1. The watcher flags the modified path.
  2. The system queries PostgreSQL/SQLite to identify symbols matching the updated file path.
  3. The matching Redis cache namespace is immediately invalidated (`DEL` command issued), forcing the next query to pull fresh definitions.
