# Workspace Scanning Spec
**Sprint 10 · Milestone 2** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define filesystem traversal rules, exclusion patterns, parser scheduling, and performance boundaries.
* **Scope**: Governs backend search walkers, file indexing queues, and hash caches.
* **Audience**: DBAs, Backend Developers, and System Architects.
* **Related Documents**:
  * [workspace/integration_strategy.md](file:///Users/anzarakhtar/aios/docs/workspace/integration_strategy.md) - System file synchronization.
  * [workspace/project_discovery/repository_discovery.md](file:///Users/anzarakhtar/aios/docs/workspace/project_discovery/repository_discovery.md) - VCS boundary rules.

---

## 1. Directory Walkers & Exclusion Mappings

Scanning workspaces containing millions of files (such as Node.js or monorepos) can exhaust memory and cause high disk I/O. The workspace walker implements strict filters before traversing paths:

```
[Walk Path]
    |
    +---> Is Path Symlink? (Check containment boundary; skip if outside workspace)
    +---> Matches Excluded Directories? (node_modules, .git, .venv, target, etc.) -> Skip
    +---> Matches Excluded Extensions? (.png, .mp4, .zip, .exe, etc.) -> Skip
    +---> File Size Exceeds Limit? (> 2MB for text files) -> Skip
    |
    v
[Parse File MD5/SHA-256] -> Check Cache -> Skip if Match -> Compile AST
```

* **Ignore Patterns Registry**: The walker parses custom ignore files (e.g. `.gitignore`, `.aiosignore`, `.ignore`) found in directory roots.
* **Fallback Hard Exclusions**: High-frequency or dependency folders are blocked unconditionally:
  ```python
  HARD_EXCLUSIONS = {
      "node_modules", ".git", ".venv", "venv", "env", ".hg", ".svn",
      "__pycache__", ".pytest_cache", ".ruff_cache", "build", "dist",
      "target", ".cargo", "bin", "obj", ".idea", ".vscode"
  }
  ```

---

## 2. Scanning Execution Cycles

Workspace scans are scheduled to balance context accuracy and performance:

1. **Initial Registration Scan**: Executed when a project root is first registered. Performs a full file scan, populating the local SQLite index.
2. **Event-Driven Scan**: File watcher notifications (saves, additions, deletions) trigger targeted, single-file AST parsing.
3. **Periodic Maintenance Scan**: Runs once per day (or on manual REPL request) to audit the database against the filesystem, reconciling any events missed by the filesystem observers.

---

## 3. Concurrency & Performance Thresholds

To keep the local machine responsive while scanning:
* **Thread Throttling**: File scanning is offloaded to a background thread pool, utilizing at most **2 threads** or **50% of CPU cores** to prevent compilation locks.
* **Hash Validation Cache**: If a file's last modified timestamp and size match the database record, the parser skips hashing and AST compilation, reducing warm scan times to **< 1.5 seconds** for standard-sized projects.
