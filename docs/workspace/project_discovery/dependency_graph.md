# Dependency Graph Generation Spec
**Sprint 10 · Milestone 2** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define data structures, import parsers, and node schemas for building project dependency graphs.
* **Scope**: Governs static import analyzers, lockfile parsing routines, and graph builders.
* **Audience**: Systems Architects, Lead Developers, and AI developers.
* **Related Documents**:
  * [workspace/capabilities.md](file:///Users/anzarakhtar/aios/docs/workspace/capabilities.md) - Capabilities domains.
  * [workspace/project_discovery/project_classification.md](file:///Users/anzarakhtar/aios/docs/workspace/project_discovery/project_classification.md) - Project stacks triggers.

---

## 1. Graph Node & Edge Mappings

To trace import dependencies and project boundaries, Workspace Intelligence constructs a local directed graph ($G = (V, E)$). 

```
+-------------------------------------------------------------+
| Nodes (V)                                                   |
+-------------------------------------------------------------+
| 1. ProjectNode  : Root project boundaries.                 |
| 2. PackageNode  : Installed third-party packages (lockfiles)|
| 3. ModuleNode   : Source code files (.py, .ts, etc.)        |
+-------------------------------------------------------------+
                              |
                              v (Edges (E))
+-------------------------------------------------------------+
| 1. DEPENDS_ON   : ProjectNode -> ProjectNode                |
| 2. IMPORTS      : ModuleNode -> ModuleNode (Static imports) |
| 3. REQUIRES     : ProjectNode -> PackageNode                |
+-------------------------------------------------------------+
```

---

## 2. Multi-Project & Package Mappings

### 2.1 Project-to-Project Dependencies
The graph builder parses configurations to detect cross-project requirements:
* **Cargo Workspaces**: Parses member declarations in root `Cargo.toml`.
* **Npm Workspaces**: Parses `workspaces` arrays in root `package.json`.
* **Python Path Mappings**: Scans workspace path structures and virtual environment configurations to map local workspace editable package dependency links.

### 2.2 Package-Level Dependencies
By parsing lockfiles (`poetry.lock`, `package-lock.json`, `Cargo.lock`), the AI OS catalogs exactly which package versions are imported. This enables agents to:
* Verify lock integrity.
* Flag vulnerabilities.
* Estimate downstream compilation impacts when updating third-party libraries.

---

## 3. Import-Level Dependency Analysis

The graph builder extracts code-level imports via static analysis (without executing code):
* **Python**: Walks the abstract syntax tree (AST) searching for `Import` and `ImportFrom` nodes.
* **TypeScript / JavaScript**: Parses files looking for `import * from ...` or `require(...)` calls.
* **Resolving Aliases**: Evaluates custom routing paths (e.g. `tsconfig.json` paths mapping, python sys.path structures) to resolve relative imports to their actual canonical source files, creating an `IMPORTS` edge between module nodes.
