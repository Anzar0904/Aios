# 08 — Coding Standards

## Document Metadata
* **Purpose**: Define strict coding standards, syntax styling, file complexity constraints, naming conventions, and validation setups to ensure long-term readability.
* **Scope**: Governs all Python source files inside the `core/` and `skills/` monorepo workspaces.
* **Audience**: Software Developers, Code Reviewers, and Linting Agents.
* **Related Documents**:
  * [00_PROJECT_VISION.md](file:///Users/anzarakhtar/aios/docs/00_PROJECT_VISION.md) - The constitutional root.
  * [01_ENGINEERING_GUIDELINES.md](file:///Users/anzarakhtar/aios/docs/01_ENGINEERING_GUIDELINES.md) - High-level developer principles.
  * [06_TESTING_GUIDELINES.md](file:///Users/anzarakhtar/aios/docs/06_TESTING_GUIDELINES.md) - Guidelines for verifying quality.
* **Future Extensions**: Automated Ruff pre-commit hook scripts will be registered here once configured.

---

## Document Outline

### 1. Naming Conventions
* **Case Consistency Rules**: `snake_case` for functions/variables, `PascalCase` for classes/types, and `UPPERCASE` for constants.
* **Descriptive Intent Over Implementation**: Writing names based on behavior rather than database queries or data caching.
* **Boolean Polarity**: Naming booleans as questions (e.g., `is_ready`, `has_cache`, `can_write`).
* **Abbreviation Restrictions**: Banning obscure acronyms, allowing only `id`, `url`, and `config`.

### 2. Complexity and Size Budgets
* **File Length Limit (400 Lines)**: Strict policy requiring module split before files exceed 400 lines.
* **Function Cyclomatic Complexity Capping**: Limiting cyclomatic complexity to a maximum of 10.
* **Parameter Budget**: Restricting function parameters to a maximum of 4 (requiring structured objects/dataclasses beyond 4).
* **Dead Code Cleanup**: Enforcing immediate deletion of unused code blocks rather than commenting them out.

### 3. Error Handling Syntax
* **Explicit Exceptions**: Prohibition of bare `except:` or `catch(e)` clauses.
* **Timeout Requirements**: Enforcing explicit timeout parameters on all network, database, and file I/O operations.
* **User-Facing vs. Log Context**: Rules for separating localized error strings from detailed debug stack traces.
* **Result Typings**: Modeling expected failure states explicitly (e.g., using `Optional` or custom status flags).

### 4. Code Formatting & Linting
* **Tooling Configuration**: Standardizing formatting on Ruff (`ruff format` and `ruff check`).
* **Import Ordering Guidelines**: Grouping standard library imports, third-party libraries, and local module imports.
* **Inline Documentation (Docstrings)**: Requiring Google-style docstrings for all public modules, functions, and classes.
