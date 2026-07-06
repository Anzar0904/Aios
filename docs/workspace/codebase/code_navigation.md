# Code Navigation Specification
**Sprint 10 · Milestone 3** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define technical interfaces and query strategies for static code navigation capabilities.
* **Scope**: Governs definition lookups, reference scans, implementation resolution, and outline mapping.
* **Audience**: AI Prompt Engineers, System Architects, and Integration Developers.
* **Related Documents**:
  * [workspace/capabilities.md](file:///Users/anzarakhtar/aios/docs/workspace/capabilities.md) - Capabilities domains.
  * [workspace/codebase/symbol_index.md](file:///Users/anzarakhtar/aios/docs/workspace/symbol_index.md) - Database symbol indexes.

---

## 1. Static Code Navigation Engine

The **Code Navigation Engine** resolves typical editor-level search queries without running runtime compiler processes, querying the local relational database and AST symbol catalogs.

```
                    [User: Query Navigation] (e.g. Find Definition of Symbol X)
                               |
              +----------------+----------------+
              v                                 v
     [Query Redis Cache]               [Query Database Index]
   - Return definition if match       - Query codebase_symbols table
                                      - Match imports path if relative
                                                |
                                                v
                                    [Return Target Coordinates]
                                     - File path
                                     - Start and End lines
```

---

## 2. Navigation Capabilities

### 2.1 Go to Definition
To locate a class or function definition:
1. Parse the importing file's AST to locate the import paths.
2. If the symbol is imported locally (e.g. `from .utils import parse`), resolve the relative path.
3. Query the `codebase_symbols` table for a row matching the resolved path and symbol name.
4. Return the absolute file path and line coordinates (`start_line`, `end_line`).

### 2.2 Find References
To find all usage locations of a given class or function:
1. Scan the static import database to locate all files that import the target symbol.
2. In those files, scan the raw token text to locate exact occurrences of the symbol name.
3. Filter out occurrences that fall inside comments or docstrings, returning line-matching snippets.

### 2.3 List Implementations
For object-oriented languages:
1. Scan the `codebase_symbols` inheritance data.
2. Find all class records where the `base_inheritances` list contains the target interface or superclass name.
3. Return the coordinates for all child classes.

### 2.4 File Outline Maps
Generates outline scopes for a target file:
* Returns a hierarchical array of symbols found in the file, sorted by line number.
* Formats signatures and docstrings, allowing agents to instantly understand the structure of a file before modifying it.
