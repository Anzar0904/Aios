# Project Classification Spec
**Sprint 10 · Milestone 2** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define the heuristic rules and file triggers used to classify workspace directories into typed projects.
* **Scope**: Governs programming languages, framework stacks, build configs, and package manager signatures.
* **Audience**: AI Prompt Engineers, Integration Engineers, and QA developers.
* **Related Documents**:
  * [workspace/capabilities.md](file:///Users/anzarakhtar/aios/docs/workspace/capabilities.md) - Capabilities domains matrix.
  * [workspace/project_discovery/workspace_catalog.md](file:///Users/anzarakhtar/aios/docs/workspace/project_discovery/workspace_catalog.md) - Catalog definitions.

---

## 1. Classification Engine

The **Project Classification Engine** parses directory structures and config files to assign tags to discovered project roots. This enables the AI OS to load correct compiler context, select appropriate test runner scripts, and format CLI arguments.

```
                    [Project Directory Path]
                               |
            +------------------+------------------+
            v                                     v
   [Read File Names]                       [Parse File Contents]
  - Cargo.toml -> Rust                    - pyproject.toml -> Poetry
  - package.json -> JS/TS                 - package.json -> React/Next
  - go.mod -> Go                          - build.gradle -> Java
  - manage.py -> Django
            |                                     |
            +------------------+------------------+
                               v
               [Classify Stack & Build Context]
```

---

## 2. Classification Triggers & Heuristics

The engine evaluates projects using a multi-dimensional matrix:

### 2.1 Programming Languages
Primary project languages are determined by scanning file distributions:
* **Python**: Presence of `.py` files. Major indicator: `pyproject.toml`, `requirements.txt`, `setup.py`.
* **TypeScript / JavaScript**: Presence of `.ts`, `.tsx`, `.js`, `.jsx` files. Major indicator: `package.json`.
* **Go**: Presence of `.go` files. Major indicator: `go.mod`.
* **Rust**: Presence of `.rs` files. Major indicator: `Cargo.toml`.

### 2.2 Frameworks
Framework classifiers scan dependencies and config structures:
* **Next.js**: `package.json` contains dependency `next`, or project contains `next.config.js`.
* **React**: `package.json` contains dependency `react`.
* **Django**: Root directory contains `manage.py`, or python dependencies contain `django`.
* **FastAPI**: Python dependencies contain `fastapi`.

### 2.3 Build Systems & Package Managers
Build setups dictate command executions:
* **Cargo**: Root contains `Cargo.toml`. Package manager: `cargo` (evaluates `Cargo.lock`).
* **Npm / Yarn / Pnpm**: Root contains `package.json`. Evaluates `package-lock.json` (npm), `yarn.lock` (yarn), or `pnpm-lock.yaml` (pnpm).
* **Poetry**: Root contains `pyproject.toml` containing `[tool.poetry]` tables. Evaluates `poetry.lock`.
* **Pip**: Root contains `requirements.txt` or `setup.py`.
* **CMake / Make**: Root contains `CMakeLists.txt` or `Makefile`.
