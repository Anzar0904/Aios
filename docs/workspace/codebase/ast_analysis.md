# AST Parsing & Scope Analysis Spec
**Sprint 10 · Milestone 3** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define technical specifications for parsing source files, traversing syntax trees, and extracting structural code scopes.
* **Scope**: Governs Python, TypeScript, and Go AST parsing pipelines.
* **Audience**: Systems Integrators, AI Prompt Engineers, and AI developers.
* **Related Documents**:
  * [workspace/capabilities.md](file:///Users/anzarakhtar/aios/docs/workspace/capabilities.md) - Capabilities domains.
  * [workspace/codebase/filesystem_intelligence.md](file:///Users/anzarakhtar/aios/docs/workspace/codebase/filesystem_intelligence.md) - Filesystem events.

---

## 1. Abstract Syntax Tree (AST) Parsing

The AI OS uses language-specific compiler modules to construct abstract syntax representations of code files:
* **Python**: Uses python's built-in `ast` module to build complete syntax trees.
* **TypeScript / JavaScript**: Integrates with local Node.js compilation tools (using TypeScript Compiler API or `esprima`) to extract node objects.
* **Go**: Utilizes standard library `go/parser` and `go/ast` packages.

```
                  +-----------------------------------+
                  |          Source File              |
                  +-----------------------------------+
                                    |
                                    v (Language Parser)
                  +-----------------------------------+
                  |           AST Tree                |
                  +-----------------------------------+
                                    |
                                    v (Scope Extractor)
                  +-----------------------------------+
                  |         Code Outline              |
                  +-----------------------------------+
                   - Imports list
                   - Classes (properties, methods)
                   - Global variables & functions
```

---

## 2. Scope & Symbol Extraction

During tree traversal, the AST Analyzer records structural scope metadata:
1. **Class Scope**:
   * Extracts class identifiers, base inheritances (superclasses), properties, and method definitions.
   * Isolates constructor configurations and instance parameters.
2. **Function / Method Scope**:
   * Identifies function arguments, parameter type hints, default values, return type definitions, and local variable declarations.
   * Extracts docstrings, comments, and decorator flags (e.g. `@staticmethod`, `@property`).
3. **Import Mappings**:
   * Extracts module import nodes (e.g. `import os`, `from aios.config import NotionConfig`).
   * Maps relative imports (e.g. `from .utils import parse`) to absolute workspace modules, feeding the dependency graph.

---

## 3. Dynamic Scope Breadcrumbs

To support language model prompt injections:
* **Scope Breadcrumb Path**: For each symbol, the AST Compiler returns a scope list (e.g., `['LocalKnowledgeHub', 'sync_document']`).
* **Line Coordinates**: The compiler records exact starting and ending line indexes (`start_line`, `end_line`) for each parsed scope node, allowing agents to perform contiguous edits targeting specific classes or functions without mutating adjacent code blocks.
