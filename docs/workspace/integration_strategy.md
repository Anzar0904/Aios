# Workspace Intelligence — Integration Strategy
**Sprint 10 · Milestone 1 (Foundation)** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define the filesystem watcher protocols, code symbol chunking strategies, vector memory mapping, and terminal trace caching.
* **Scope**: Governs backend indexing logic, database sync loops, and Qdrant collection schemes.
* **Audience**: Search Engineers, Database Administrators, and QA developers.
* **Related Documents**:
  * [05_SECURITY_GUIDELINES.md](file:///Users/anzarakhtar/aios/docs/05_SECURITY_GUIDELINES.md) - Security and path constraints.
  * [workspace/capabilities.md](file:///Users/anzarakhtar/aios/docs/workspace/capabilities.md) - Mapped capability domains.

---

## 1. Filesystem Watcher Protocol

To maintain a real-time index of the workspace without causing high CPU utilization or I/O bottleneck, Workspace Intelligence uses a dual-layer watch system:

```
[Local Filesystem Operations]
             |
             v
+--------------------------+
|  OS Filesystem Event Bus | (fsnotify / Watchdog)
+--------------------------+
             |
             +---> Check File Type (Skip binary, .git, node_modules, .venv, etc.)
             |
             v
+--------------------------+
|  Incremental Queue       | (Debounced 500ms to handle rapid saves)
+--------------------------+
             |
             v
+--------------------------+
|  Background Parser Thread | ===> Compiles AST -> SQLite + Qdrant update
+--------------------------+
```

1. **Exclusion Rules**: Path watchers ignore directories containing high-frequency temporary writes (e.g. `.git/`, `node_modules/`, `.venv/`, `target/`, `dist/`, `.pytest_cache/`, `.ruff_cache/`).
2. **Debouncing Events**: Rapid saves or git branch checkouts trigger many filesystem events. The queue debounces files for 500ms, ensuring each file undergoes compilation only once per editing burst.
3. **Polling Fallback**: On network filesystems or environments where OS-level notification limits are exceeded, the watcher falls back to a periodic digest check (polling every 10 seconds checking file modification timestamps).

---

## 2. Code Chunking & Semantic Indexing

Standard text splitters segment source files into fixed character-count chunks (e.g., 500 characters), which splits import statements or class signatures across sections, corrupting LLM understanding. Workspace Intelligence utilizes **AST-Based Semantic Chunking**:

```python
# Pseudo-implementation of AST-based chunk extraction
class ASTChunker:
    def chunk_file(self, file_path: str, source_code: str) -> List[CodeChunk]:
        tree = ast.parse(source_code)
        chunks = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                # Extract clean substring matching the node boundary
                chunk_text = self.get_node_source(source_code, node)
                metadata = {
                    "file_path": file_path,
                    "symbol_name": node.name,
                    "symbol_type": type(node).__name__,
                    "breadcrumbs": self.get_breadcrumbs_path(node)
                }
                chunks.append(CodeChunk(text=chunk_text, metadata=metadata))
        return chunks
  ```

* **Chunk Containment**: Code is chunked strictly by symbol scope boundaries (Classes, Functions, Methods, Struct definitions).
* **Metadata Injecting**: Each vector uploaded to Qdrant contains payload references:
  * `workspace_id`: Hash of root path (for scope isolation).
  * `source`: Set to `"workspace"`.
  * `symbol_name` / `symbol_type`: Type tags enabling filtered vector queries.
  * `breadcrumbs`: Visual scope path (e.g. `core/src/aios/services/approval_impl.py -> ApprovalEngine -> evaluate_consensus`).

---

## 3. Vector Database Collection Mappings

Workspace vectors are saved to the **`workspace_memory`** collection in Qdrant:
* **Dimensions**: 384 dimensions matching the local `all-MiniLM-L6-v2` embedding model.
* **Distance Metric**: Cosine distance (filtering similarity scores below `0.78`).
* **Payload Indexing**: Fields `workspace_id`, `symbol_type`, and `file_path` are explicitly indexed in Qdrant, enabling sub-millisecond retrieval filtering.

---

## 4. Temporary Context Caching (Build & Terminal Logs)

Unlike source code, terminal traces and compiler errors are highly transient.
* **SQLite Log Store**: Stdout logs and compiler outputs are stored as raw text in local SQLite databases, linked to command executions.
* **Transient Memory Injector**: During active debugging sessions, compiler errors are fetched from SQLite, embedded, and injected into a temporary Qdrant session namespace. When the developer completes the debugging run, this session memory is automatically purged, preventing stale build errors from polluting the agent's long-term retrieval context.
