# Repository History & Knowledge Nodes Spec
**Sprint 10 · Milestone 4** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define relation graphs mapping git commits to code symbols and system Knowledge Nodes.
* **Scope**: Governs history schemas, metadata relations, and semantic node lookups.
* **Audience**: Systems Architects, DBAs, and AI developers.
* **Related Documents**:
  * [workspace/codebase/symbol_index.md](file:///Users/anzarakhtar/aios/docs/workspace/codebase/symbol_index.md) - Database symbol indexes.
  * [workspace/source_control/commit_analysis.md](file:///Users/anzarakhtar/aios/docs/workspace/source_control/commit_analysis.md) - Commit parsing.

---

## 1. Mappings Graph: Commit-Symbol-Knowledge Node

In the Personal AI OS, codebase files, documentation modules, and system designs are represented as **Knowledge Nodes** in the cognitive database. The Repository History module links Git events directly to these nodes:

```
+------------------+                   +------------------+
|    CommitNode    | ==(MODIFIED)===>  |     FileNode     | (Module)
+------------------+                   +------------------+
         |                                       |
     (CHANGED)                               (CONTAINS)
         v                                       v
+------------------+                   +------------------+
|    SymbolNode    | ==(REPRESENTS)==> |  KnowledgeNode   |
+------------------+                   +------------------+
```

* **`CommitNode`**: A Git commit, containing hash, author, date, and conventional type.
* **`FileNode`**: A physical module file in the workspace directory.
* **`SymbolNode`**: An AST-defined class, function, or method.
* **`KnowledgeNode`**: A unit of system knowledge, documentation, or code reference stored in the vector database (`Qdrant`).

---

## 2. History Tracking Schema

The history tracker records changes to specific symbols in local SQLite databases to trace evolution:

```sql
CREATE TABLE IF NOT EXISTS symbol_history_ledger (
    ledger_id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol_id TEXT NOT NULL,
    commit_hash TEXT NOT NULL,
    author_email TEXT NOT NULL,
    committed_at TIMESTAMP NOT NULL,
    lines_added INTEGER NOT NULL,
    lines_deleted INTEGER NOT NULL,
    change_type TEXT CHECK(change_type IN ('ADDITION', 'MODIFICATION', 'DELETION')) NOT NULL,
    FOREIGN KEY(symbol_id) REFERENCES symbols(symbol_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_symbol_history_commit ON symbol_history_ledger(commit_hash);
```

---

## 3. Knowledge Evolution Lookups

By linking git histories to Knowledge Nodes, the AI OS can resolve queries like:
* "Show changes to `class NotionProvider` over the last 30 days."
* "Who was the last contributor to modify `def sync_document`?"
* "What commits introduced modifications to the `KnowledgeHubService` interface?"

This mapping lets the reasoning core understand how codebase components and design schemas have evolved, providing context for automated code changes and bug diagnostics.
