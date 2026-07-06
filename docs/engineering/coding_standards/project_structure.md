# Project Structure
**Engineering Bible — Coding Standards — Document 3 of 7**
**Version 1.0** · *Classified: For One Person Only* · *July 2026*

---

## Document Metadata

* **Purpose**: Define the canonical directory layout, package boundaries, nesting depth limits, and file placement rules for the Personal AI OS monorepo. This document ensures that any AI agent or new contributor can locate any file and know exactly where to place new work without asking.
* **Scope**: The entire monorepo rooted at `/Users/anzarakhtar/aios/`.
* **Audience**: Software Engineers, AI coding agents, Technical Architects, and Code Reviewers.
* **Related Documents**:
  * [naming_conventions.md](naming_conventions.md) — File and directory naming rules (companion document).
  * [import_rules.md](import_rules.md) — Import boundary rules derived from this structure (companion document).
  * [02_ARCHITECTURE_GUIDELINES.md](file:///Users/anzarakhtar/aios/docs/02_ARCHITECTURE_GUIDELINES.md) — Service boundary contracts.
  * [03_IMPLEMENTATION_GUIDELINES.md](file:///Users/anzarakhtar/aios/docs/03_IMPLEMENTATION_GUIDELINES.md) — Skill and tool implementation playbooks.
  * [01_ENGINEERING_GUIDELINES.md](file:///Users/anzarakhtar/aios/docs/01_ENGINEERING_GUIDELINES.md) — SDLC gates; max nesting depth is an SDLC constraint.
* **Stability**: High. Layout changes require an ADR in [10_DECISION_LOG.md](file:///Users/anzarakhtar/aios/docs/10_DECISION_LOG.md) and a global import update.

---

> [!IMPORTANT]
> **The structure is law.** Placing files outside the prescribed locations, creating undocumented top-level directories, or nesting deeper than 3 levels from the repo root (without an ADR) are blocking violations.

---

## 1. Monorepo Root Layout

```
/Users/anzarakhtar/aios/          ← Monorepo root
│
├── core/                         ← Python application package
├── skills/                       ← External skill packages
├── docs/                         ← All documentation
├── config/                       ← Runtime configuration
├── prompts/                      ← LLM prompt templates
├── templates/                    ← Output and report templates
├── diagrams/                     ← Architecture diagrams (source files)
├── assets/                       ← Static assets (icons, images)
├── examples/                     ← Usage examples and demos
│
├── pyproject.toml                ← Monorepo build + tool configuration
├── README.md                     ← Project entry point
├── Engineering_Constitution.md   ← Constitutional root document
└── .gitignore
```

**Root-level rules:**

* No `.py` source files at the monorepo root (only config and documentation).
* No new top-level directories without an ADR.
* No `src/` at the repo root — source lives in `core/src/`.

---

## 2. Core Package Layout

```
core/
├── src/
│   └── aios/                     ← Top-level Python package
│       ├── __init__.py
│       ├── bootstrap.py          ← Composition Root (DI wiring)
│       ├── kernel.py             ← Kernel Orchestrator
│       ├── cli.py                ← REPL entry point
│       ├── config.py             ← Configuration loader
│       ├── registry.py           ← Service registry
│       │
│       ├── brain/                ← Brain Orchestration Engine
│       │   ├── __init__.py
│       │   ├── orchestrator.py
│       │   ├── context_builder.py
│       │   ├── intent_resolver.py
│       │   └── action_engine.py
│       │
│       ├── services/             ← Abstract + concrete service implementations
│       │   ├── __init__.py
│       │   ├── memory_service.py       ← Abstract protocol
│       │   ├── local_memory_service.py ← SQLite implementation
│       │   ├── model_service.py        ← Abstract protocol
│       │   └── event_bus_service.py
│       │
│       ├── providers/            ← LLM provider adapters
│       │   ├── __init__.py
│       │   ├── openai_provider.py
│       │   ├── anthropic_provider.py
│       │   └── ollama_provider.py
│       │
│       ├── skills/               ← Skill system (manager + metadata)
│       │   ├── __init__.py
│       │   ├── skill_manager.py
│       │   └── metadata.py
│       │
│       ├── source_control/       ← Git integration
│       │   ├── __init__.py
│       │   └── git_service.py
│       │
│       ├── n8n/                  ← Workflow automation integration
│       │   └── ...
│       │
│       └── docgen/               ← Documentation generation utilities
│           └── ...
│
├── tests/                        ← All test files (mirrors src/aios/ structure)
│   ├── conftest.py
│   ├── test_kernel.py
│   ├── test_local_memory_service.py
│   └── ...
│
└── pyproject.toml                ← Package-local tool config (if needed)
```

### 2.1 Nesting Depth Limit

**Maximum 3 levels** from the repo root for source directories:

```
core/src/aios/                 ← Level 1 (package root)
core/src/aios/brain/           ← Level 2 (sub-package)
core/src/aios/brain/_internal/ ← Level 3 (private helpers) ← MAXIMUM
```

A directory at Level 4 is a signal that the package needs to be broken into its own top-level package or the design is over-engineered.

### 2.2 File Placement Rules

| File type | Correct location |
|-----------|----------------|
| Abstract protocol / ABC | `core/src/aios/services/{name}_service.py` |
| Concrete implementation | `core/src/aios/services/local_{name}_service.py` |
| CLI command handler | `core/src/aios/cli.py` (handler) + `core/src/aios/brain/` (logic) |
| Kernel Orchestrator | `core/src/aios/kernel.py` — never split |
| Composition Root (DI) | `core/src/aios/bootstrap.py` — never split |
| Configuration loader | `core/src/aios/config.py` |
| Test for module `X` | `core/tests/test_{X}.py` |
| Shared test fixtures | `core/tests/conftest.py` |
| Shared utility function | `core/src/aios/utils/{domain}_utils.py` |

### 2.3 Private Internal Modules

Modules not meant for external import within the package use an `_internal/` subdirectory:

```
core/src/aios/brain/
├── __init__.py           ← exports: OrchestratorBrain
├── orchestrator.py       ← public implementation
└── _internal/
    ├── __init__.py
    ├── context_window.py ← internal helper
    └── plan_formatter.py ← internal helper
```

`_internal/` modules must never be imported outside their parent package.

---

## 3. Skills Package Layout

Skills are standalone Python packages that the `SkillManager` discovers at runtime.

```
skills/
├── github/                   ← GitHub skill package
│   ├── skill.toml            ← Skill manifest (required)
│   ├── __init__.py
│   ├── commands.py           ← Command registration hooks
│   ├── github_service.py     ← Core skill logic
│   └── prompts/              ← Prompt templates for this skill
│       ├── summarise.md
│       └── review.md
│
├── research/                 ← Research skill package
│   ├── skill.toml
│   ├── __init__.py
│   ├── commands.py
│   └── research_service.py
│
└── ...
```

### 3.1 Skill Manifest (`skill.toml`)

Every skill package **must** have a `skill.toml` at its root:

```toml
[skill]
name = "github"
version = "1.0.0"
description = "GitHub repository and pull request intelligence"
author = "AI OS Core Team"
requires_tools = ["git"]
entry_point = "commands"
```

### 3.2 Skill Isolation Rules

* Skills must not import from `core/src/aios/` internal modules. They receive services via the `ServiceRegistry` injected at boot.
* Skills must not share code directly — extract to a `skills/shared/` utility package if sharing is required.
* Each skill directory is a self-contained Python package with its own `__init__.py`.

---

## 4. Documentation Layout (`docs/`)

```
docs/
│
├── INDEX.md                  ← Documentation homepage + navigation
├── README.md                 ← Docs overview
├── AI_CONTEXT.md             ← Token-efficient AI entry point
│
├── 00_PROJECT_VISION.md      ← Constitutional root
├── 01_ENGINEERING_GUIDELINES.md
├── 02_ARCHITECTURE_GUIDELINES.md
├── ...                       ← NN_TITLE.md numbered sequence
│
├── engineering/              ← Engineering Bible Foundation (Sprint 8)
│   ├── README.md             ← Navigation hub
│   ├── vision.md
│   ├── philosophy.md
│   ├── engineering_principles.md
│   ├── design_goals.md
│   ├── engineering_ethics.md
│   └── coding_standards/     ← Coding Standards (Sprint 8 M2)
│       ├── README.md
│       ├── python_standards.md
│       ├── naming_conventions.md
│       ├── project_structure.md   ← THIS FILE
│       ├── import_rules.md
│       ├── dependency_rules.md
│       ├── error_handling.md
│       └── logging_standards.md
│
├── adr/                      ← Architecture Decision Records
│   └── NNN-description.md
│
├── architecture/             ← Architecture diagrams + specs
├── diagrams/                 ← Mermaid source diagrams
├── guides/                   ← How-to guides
├── milestones/               ← Sprint milestone reports
└── ...
```

### 4.1 Documentation File Rules

* Numbered root docs (`NN_TITLE.md`) never move — their URL paths are permanent references.
* Engineering Bible sub-documents (`docs/engineering/**`) use `snake_case.md`.
* ADRs follow `docs/adr/NNN-kebab-description.md`.
* Sprint milestone reports go in `docs/milestones/SPRINT_N_MN_REPORT.md`.

---

## 5. Configuration Layout (`config/`)

```
config/
├── config.toml               ← Runtime configuration (primary)
├── config.example.toml       ← Committed example with all keys documented
└── secrets.example.toml      ← Example secrets file (never commit actual secrets)
```

* `config.toml` is loaded by `core/src/aios/config.py` at boot.
* Secrets (API keys) are injected via environment variables — never stored in `config.toml`.
* `config.example.toml` documents every available key with type, default, and description comments.

---

## 6. Test Layout (`core/tests/`)

```
core/tests/
├── conftest.py               ← Shared fixtures (db paths, mock services)
├── test_kernel.py            ← One test file per source module
├── test_local_memory_service.py
├── test_intent_resolver.py
├── test_omni_route_selector.py
└── ...
```

### 6.1 Test File Rules

| Rule | Detail |
|------|--------|
| One test file per source module | `test_{module_name}.py` mirrors `{module_name}.py` |
| No subdirectories in `core/tests/` | All tests are flat — no `tests/unit/`, `tests/integration/` splits |
| Shared fixtures only in `conftest.py` | No fixture duplication across test files |
| No production imports from tests into production | Tests import from `core/src/aios/`; never the reverse |

### 6.2 Test File Naming

```
test_{module_name}.py

# Examples:
test_local_memory_service.py    # tests for local_memory_service.py
test_omni_route_selector.py     # tests for omni_route_selector.py
test_kernel.py                  # tests for kernel.py
```

---

## 7. Prohibited Patterns

| Pattern | Why Prohibited |
|---------|---------------|
| `.py` files at repo root | Source belongs in `core/src/aios/` |
| `utils.py` or `helpers.py` | Generic names — name by responsibility |
| Nesting beyond 3 levels | Signals over-engineering; requires ADR |
| `tests/` inside `core/src/` | Tests live in `core/tests/`, never alongside source |
| Skill importing from `core/src/aios/` internals | Breaks skill isolation; use service injection |
| New top-level directory without ADR | Structural changes require documented rationale |
| Secrets in `config/config.toml` | Security violation — use environment variables |
| Duplicated logic across skills | Extract to `skills/shared/` |

---

## 8. Adding New Modules — Decision Tree

```
New Python module needed?
        │
        ├─ Is it domain logic for the AI OS kernel?
        │   └─ Yes → core/src/aios/{domain}/
        │
        ├─ Is it a standalone user-facing capability?
        │   └─ Yes → skills/{skill_name}/
        │
        ├─ Is it shared infrastructure used by multiple domains?
        │   └─ Yes → core/src/aios/utils/{domain}_utils.py
        │
        ├─ Is it a test?
        │   └─ Yes → core/tests/test_{module_name}.py
        │
        └─ Is it documentation?
            └─ Yes → docs/engineering/coding_standards/ or docs/{NN_TITLE}.md
```

---

*Engineering Bible Coding Standards · Personal AI OS · Sprint 8 M2 · Governed by [engineering_principles.md](../engineering_principles.md)*
