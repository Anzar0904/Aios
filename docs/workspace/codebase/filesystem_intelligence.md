# Filesystem Intelligence Spec
**Sprint 10 · Milestone 3** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define filesystem event processing loops, directory tree caching schemas, and path containment validation rules.
* **Scope**: Governs backend path monitors, virtual filesystem caches, and security intercepts.
* **Audience**: Systems Developers, Security Auditors, and AI developers.
* **Related Documents**:
  * [workspace/security_model.md](file:///Users/anzarakhtar/aios/docs/workspace/security_model.md) - Security path containment checks.
  * [workspace/project_discovery/workspace_scanning.md](file:///Users/anzarakhtar/aios/docs/workspace/project_discovery/workspace_scanning.md) - Filesystem scanning triggers.

---

## 1. Real-Time Filesystem Monitoring

The **Filesystem Intelligence** layer processes operating system disk events (using `watchdog` on macOS/Windows and `inotify` on Linux) to track updates to files within registered workspace folders.

```
[Local File Operations] ===> OS Filesystem Events (Create, Modify, Delete)
                                    |
                                    v
                        [Path Security Filter] ===> Skip if outside containment boundary
                                    |
                                    v
                         [Ignore Rules Filter] ===> Skip if matched by .gitignore / .aiosignore
                                    |
                                    v
                           [Event Debouncer] ===> Group changes within 500ms
                                    |
                                    v
                         [Workspace Index Queue] ===> Update DB & trigger AST Parse
```

* **Recursive Path Monitors**: Filesystem watches are registered recursively on root directories, excluding heavy build directories.
* **Symlink Validation**: Symlinks are evaluated to ensure their target targets fall inside the workspace directory boundary. If a symlink points outside, the monitor skips the path, preventing directory traversal.

---

## 2. Directory Tree Caching

To avoid triggering heavy disk read operations when resolving relative workspace paths (e.g. searching import chains), Filesystem Intelligence maintains a local replica of the directory structure in PostgreSQL/SQLite:

```sql
CREATE TABLE IF NOT EXISTS directory_tree_cache (
    node_id TEXT PRIMARY KEY,
    workspace_id TEXT NOT NULL,
    parent_node_id TEXT,
    name TEXT NOT NULL,
    is_directory INTEGER CHECK(is_directory IN (0, 1)) NOT NULL,
    relative_path TEXT NOT NULL,
    absolute_path TEXT NOT NULL UNIQUE,
    depth INTEGER NOT NULL,
    FOREIGN KEY(parent_node_id) REFERENCES directory_tree_cache(node_id) ON DELETE CASCADE
);
```

* **Fast Search Indices**: Database indexes are built on `relative_path` and `parent_node_id`. This reduces directory hierarchy queries to **< 1ms**, bypassing physical disk searches.
* **Cache Reconciliation**: On startup, a shallow traversal (comparing file sizes and modified timestamps) is executed to align the SQL cache with physical disk contents.
