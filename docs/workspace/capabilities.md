# Workspace Intelligence — Capabilities Matrix
**Sprint 10 · Milestone 1 (Foundation)** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define the mapping schemas, domain entities, and behavioral patterns for workspace files, git states, compiler pipelines, terminal histories, and IDE hooks.
* **Scope**: Dictates the boundaries and formats of intelligence schemas processed by Workspace agents.
* **Audience**: Systems Integrators, QA Engineers, and AI developers.
* **Related Documents**:
  * [17_KNOWLEDGE_BASE.md](file:///Users/anzarakhtar/aios/docs/17_KNOWLEDGE_BASE.md) - System definitions repository.
  * [workspace/architecture.md](file:///Users/anzarakhtar/aios/docs/workspace/architecture.md) - Technical architecture.

---

## 1. Domain Object Mappings

The Workspace Intelligence subsystem maps physical workspace attributes to local Python dataclasses. This abstract schema allows AI agents to reason about development states consistently.

```
                  +-----------------------------------+
                  |         WorkspaceProject          | (Root folder metadata)
                  +-----------------------------------+
                                    |
            +-----------------------+-----------------------+
            v                                               v
  +-------------------+                           +-------------------+
  |   GitRepository   |                           |    BuildContext   |
  +-------------------+                           +-------------------+
   - Active branch     \                           - Toolchain version
   - Dirty/staged files \                          - Lockfile contents
   - Stash list          \                         - Environment vars
                          \                                 |
                           v                                v
                  +-------------------+           +-------------------+
                  |   WorkspaceFile   |           |    BuildTask      |
                  +-------------------+           +-------------------+
                   - Relative path                 - Compile script
                   - AST Class/Symbol              - Diagnostic logs
                   - Binary / Text flag            - Run status code
```

---

## 2. Capability Domains

### 2.1 Repositories & Projects
The AI OS reads workspace configuration files (e.g., `package.json`, `pyproject.toml`, `Cargo.toml`, `.git/config`) to discover project names, metadata, target runtime versions, and active configurations.
* **Workspaces Registry**: Stores project roots, developer preferences, and build histories in a centralized local index.
* **Active Profile Binding**: Matches development projects to specific user goals in `personal_profiles.json`.

### 2.2 File AST & Symbol Indexing
Instead of treating code files as flat text strings, the system compiles supported languages to Abstract Syntax Trees (ASTs):
* **Symbol Resolving**: Identifies imports, variable bindings, function calls, class variables, and decorator macros.
* **Breadcrumbs Mapped Context**: For code chunking, lines are prefixed with their structural path (e.g., `aios/services/knowledge_hub_impl.py -> Class: LocalKnowledgeHub -> def sync_document`).

### 2.3 Compilers & Build Systems
Workspace Intelligence interfaces with common compiler outputs and build tools (`make`, `cargo`, `npm`, `maven`, `poetry`, `pip`):
* **Diagnostic Log Parsing**: Automatically extracts warning and error lines from compilation outputs, tagging them with line numbers and file paths.
* **Dependency Graphs**: Analyzes static imports to construct file dependency maps, identifying affected modules when code files are changed.

### 2.4 Package Managers
Tracks dependency graphs, packages, and security lockfiles:
* **Drift Detection**: Alerts developers if active virtual environment libraries do not match lockfile declarations.
* **License & Security Guard**: Scans incoming packages against blacklist restrictions prior to installation runs.

### 2.5 Git & Version Control
Observes and manages repository history states:
* **Status Monitoring**: Tracks modified files, untracked scripts, stashed blocks, and active branch changes.
* **Diff Comprehension**: Parses diff headers and hunks, separating changes into structural deletions, modifications, and additions.

### 2.6 Sandboxed Terminals
Controls and records CLI activities:
* **Output Stream Buffer**: Spawns terminal processes using a custom shell runner, capturing stdout and stderr streams.
* **Liveness Timers**: Cancels hung CLI processes (e.g. waiting for input or infinite loops) when liveness timeout expires.

### 2.7 IDEs & Language Server Protocol (LSP)
Pairs with existing developer editors (VSCode, Cursor, Vim, Emacs):
* **LSP Client Adapter**: Issues requests to local language servers to retrieve definitions, autocompletions, and type signatures.
* **Cursor Context Sync**: Tracks which file is open and the active line cursor to provide contextual AI updates.
