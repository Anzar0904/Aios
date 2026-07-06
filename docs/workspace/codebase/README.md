# File System & Codebase Intelligence — Navigation Hub
**Sprint 10 · Milestone 3** · Version 1.0 · July 2026

---

> [!IMPORTANT]
> This directory houses the **File System & Codebase Intelligence** specifications for the Personal AI OS.
> It builds upon the [Development Workspace Foundation](file:///Users/anzarakhtar/aios/docs/workspace/README.md) and the [Project Discovery](file:///Users/anzarakhtar/aios/docs/workspace/project_discovery/README.md) specifications.
>
> In accordance with local-first system guidelines, all AST parsing, symbol indexing, dependency graphing, change tracking, and code health evaluations are managed locally by the AI OS, utilizing PostgreSQL/SQLite catalogs, Qdrant vectors, and Redis caches.

---

## Documents

| Document | Purpose |
|---|---|
| [filesystem_intelligence.md](file:///Users/anzarakhtar/aios/docs/workspace/codebase/filesystem_intelligence.md) | Real-time file system monitoring, path validation, and directory tree metadata caching |
| [ast_analysis.md](file:///Users/anzarakhtar/aios/docs/workspace/codebase/ast_analysis.md) | Abstract Syntax Tree (AST) compilation, scope extraction, and import mappings |
| [symbol_index.md](file:///Users/anzarakhtar/aios/docs/workspace/codebase/symbol_index.md) | Schema definitions for database symbol tables, Qdrant vector indexing, and Redis lookup caching |
| [code_navigation.md](file:///Users/anzarakhtar/aios/docs/workspace/codebase/code_navigation.md) | Specifications for resolving "Go to Definition", "Find References", and outline maps |
| [dependency_analysis.md](file:///Users/anzarakhtar/aios/docs/workspace/codebase/dependency_analysis.md) | Module-level dependency resolution, cyclic import detection, and graph builds |
| [change_detection.md](file:///Users/anzarakhtar/aios/docs/workspace/codebase/change_detection.md) | Debounced file change processing, line-range delta hashes, and index invalidation loops |
| [code_health.md](file:///Users/anzarakhtar/aios/docs/workspace/codebase/code_health.md) | Metrics parsing cognitive complexity, code-to-comment ratios, duplication, and quality scores |

---

## Reading Order

1. **[`filesystem_intelligence.md`](file:///Users/anzarakhtar/aios/docs/workspace/codebase/filesystem_intelligence.md)**: Explore filesystem watchers and path containment checks.
2. **[`ast_analysis.md`](file:///Users/anzarakhtar/aios/docs/workspace/codebase/ast_analysis.md)**: Study compilation layers and AST parsing.
3. **[`symbol_index.md`](file:///Users/anzarakhtar/aios/docs/workspace/codebase/symbol_index.md)**: Review database storage configurations (PostgreSQL, Qdrant, Redis).
4. **[`code_navigation.md`](file:///Users/anzarakhtar/aios/docs/workspace/codebase/code_navigation.md)**: Learn how definitions, references, and outlines are resolved.
5. **[`dependency_analysis.md`](file:///Users/anzarakhtar/aios/docs/workspace/codebase/dependency_analysis.md)**: Read about module imports and cycle tracking.
6. **[`change_detection.md`](file:///Users/anzarakhtar/aios/docs/workspace/codebase/change_detection.md)** & **[`code_health.md`](file:///Users/anzarakhtar/aios/docs/workspace/codebase/code_health.md)**: Examine file change delta tracking and code quality grading.
