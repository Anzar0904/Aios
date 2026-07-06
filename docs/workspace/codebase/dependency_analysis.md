# Dependency & Import Analysis Spec
**Sprint 10 · Milestone 3** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define data structures and algorithms for module-level dependency resolution and cyclic import detection.
* **Scope**: Governs static graph builders, import path resolvers, and cycle analyzers.
* **Audience**: Systems Architects, DBAs, and Lead Developers.
* **Related Documents**:
  * [workspace/project_discovery/dependency_graph.md](file:///Users/anzarakhtar/aios/docs/workspace/project_discovery/dependency_graph.md) - Project dependency schemas.
  * [workspace/codebase/ast_analysis.md](file:///Users/anzarakhtar/aios/docs/workspace/codebase/ast_analysis.md) - AST import parsers.

---

## 1. Module-Level Import Mappings

The **Dependency Analysis** engine extracts import edges between individual source modules to build a directed codebase topology:

```
+------------------+                    +------------------+
|  Module A (.py)  | ===(IMPORTS)===>   |  Module B (.py)  |
+------------------+                    +------------------+
                                                 |
                                            (IMPORTS)
                                                 v
                                        +------------------+
                                        |  Module C (.py)  |
                                        +------------------+
```

When a module node is parsed, the analyzer maps imports to physical targets:
1. **Third-Party Imports**: Imports targeting external libraries (e.g. `import pytest`) are resolved to package nodes (`PackageNode`), feeding the environment security audit.
2. **Local Internal Imports**: Imports targeting workspace modules (e.g. `import aios.config`) are resolved using compiler paths to absolute files, creating an `IMPORTS` edge between module nodes.

---

## 2. Cyclic Import Detection

Cyclic dependencies (e.g., Module A imports Module B, which imports Module C, which imports Module A) can cause runtime compiler deadlocks and make modules difficult to test.

The Dependency Engine runs **Tarjan's strongly connected components (SCC) algorithm** on the module graph:
* **Detection Gate**: Analyzes the import topology to identify cycles.
* **Alert Trigger**: If an import cycle is introduced by a file edit, the AI OS prints a warning in the console:
  ```
  [Dependency Warning]
  Cyclic dependency detected:
  core/src/aios/services/approval_impl.py ->
  core/src/aios/services/knowledge_hub_impl.py ->
  core/src/aios/services/approval_impl.py
  Please refactor shared types to avoid compiler locks.
  ```

---

## 3. Dynamic Dependency Invalidation

When a filesystem watcher triggers a modification event:
1. Delete all outgoing `IMPORTS` edges for the changed module.
2. Re-parse the AST imports list for the file.
3. Construct new `IMPORTS` edges matching the fresh imports.
4. Re-run the cycle check loop to ensure RHI metrics remain valid.
