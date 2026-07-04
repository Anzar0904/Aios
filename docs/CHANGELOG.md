# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.5.0] — 2026-07-04
### Added
* **Documentation Foundation**: Fully wrote and structured system-wide guidelines including:
  * `00_PROJECT_VISION.md` (Constitutional core, success metrics, and non-goals).
  * `01_ENGINEERING_GUIDELINES.md` (DoD guidelines and version pinning rules).
  * `02_ARCHITECTURE_GUIDELINES.md` (Kernel-service Decoupling and Composition Roots).
  * `03_IMPLEMENTATION_GUIDELINES.md` (Playbooks for skills, tools, and command registries).
  * `04_AI_MODEL_STRATEGY.md` (OmniRoute selector maps and local-first configurations).
  * `05_SECURITY_GUIDELINES.md` (Path traversal preventions and subprocess command whitelisting).
  * `06_TESTING_GUIDELINES.md` (Pytest fixture setups, unit/integration splits, and coverage goals).
  * `07_DOCUMENTATION_GUIDELINES.md` (Markdown format boundaries and docstrings rules).
  * `08_CODING_STANDARDS.md` (PEP8 style parameters, cyclomatic complexity limits, and file line budgets).
  * `09_ROADMAP.md` (Development phases and v0.6-v2.0 milestone schedules).
  * `10_DECISION_LOG.md` (Architecture Decision Records registry logging 16 key choices).
  * `11_CONTRIBUTING.md` (Git branching strategy and AI contributor guidelines).
  * `12_PRD.md` (Product personas, user workflows, and MVP scoping).
  * `13_DRD.md` (Visual design system tokens, typography rules, and CLI console layouts).
  * `14_TECH_STACK.md` (Core languages, package management, and future UI components).
  * `15_SYSTEM_DESIGN.md` (Component designs, sequence flows, and bootstrap charts).
  * `16_ENGINEERING_BIBLE.md` (Unified technical textbook manual).
  * `17_KNOWLEDGE_BASE.md` (System data schemas and terminology dictionaries).
  * `18_INTERVIEW_GUIDE.md` (Architecture review Q&As and behavioral scenarios).
  * `19_GLOSSARY.md` (Official vocabulary reference definitions).
  * `20_OPERATIONS_MANUAL.md` (Installation setups, backups, diagnostics tables, and recoveries).
  * `AI_CONTEXT.md` (AI-optimized token-efficient context index entry point).
  * `INDEX.md` (Documentation homepage directory map).
  * `PROJECT_STATUS.md` (Live project phase dashboard).

---

## [0.4.0] — 2026-06-15
### Added
* **Skill System Implementation**: Added modular capacity loaders under `skills/` directories.
* **Commands Registration**: Built `CommandRegistry` to map and dynamically discover CLI arguments.
* **Refactored**: Decoupled commands from direct kernel execution loops.

---

## [0.3.0] — 2026-05-28
### Added
* **Provider Manager**: Built the abstract `ModelService` adapter layer.
* **Model Selector**: Integrated the OmniRoute model selector to dynamically choose provider endpoints.
* **Fallback Executions**: Implemented fallback execution routing to Ollama/LM Studio local runtimes on connection timeout failures.

---

## [0.2.0] — 2026-04-10
### Added
* **GitHub Skill**: Integrated standard read-only and status git subcommands tools.
* **Path Traversal Checks**: Created the initial `validate_workspace_path` containment validator checks.

---

## [0.1.0] — 2026-03-01
### Added
* **Brain Orchestrator**: Initial repository setup. Implemented the basic prompt planning engine.
* **Interactive CLI REPL**: Configured `cli.py` shell console loop.
