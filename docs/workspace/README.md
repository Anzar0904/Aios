# Development Workspace Intelligence — Documentation Hub
**Sprint 10 · Milestone 1 (Foundation)** · Version 1.0 · July 2026

---

> [!IMPORTANT]
> This directory defines the **Development Workspace Intelligence Foundation** for the Personal AI OS.
> All documents in this section are subordinate to and derived from
> [00_PROJECT_VISION.md](file:///Users/anzarakhtar/aios/docs/00_PROJECT_VISION.md) (the OS Constitution) and 
> [16_ENGINEERING_BIBLE.md](file:///Users/anzarakhtar/aios/docs/16_ENGINEERING_BIBLE.md) (the Engineering Bible).
>
> In accordance with the system's design laws, this module operates strictly under a local-first, offline-first paradigm, keeping the AI OS kernel as the central execution and reasoning core while safely reading, mapping, and orchestrating the developer's local repositories, terminals, and workspace toolchains.

---

## Purpose

`docs/workspace/` is the canonical home for the architectural specifications, functional capabilities, integration strategies, security models, and development roadmap of the Workspace Intelligence subsystem.

This subsystem provides the AI OS with a comprehensive, real-time semantic understanding of the local development environment—including active repositories, file AST structures, active terminal streams, IDE setups, build configurations, package managers, and executing local tasks. It enables agents to act as competent pair programmers and systems executors while preserving the integrity of the workspace.

---

## Document Map

```
docs/workspace/
├── README.md                    ← This file — navigation hub
├── workspace_intelligence.md    ← Conceptual vision and product framework
├── architecture.md              ← Structural components, classes, and observers
├── capabilities.md              ← Repositories, files, compilers, terminals, and LSP mappings
├── integration_strategy.md      ← Filesystem watchers, code symbol chunking, and memory sync
├── security_model.md            ← Path containment, credentials isolation, and command guards
├── roadmap.md                   ← Sprint 10 milestones, timeline, and risk matrix
├── project_discovery/           ← Milestone 2: Project discovery, classification, and VCS boundaries
├── codebase/                    ← Milestone 3: Filesystem, AST, symbol DB, and code health
├── source_control/              ← Milestone 4: Git status, commits DAG, conflicts, and metrics
├── development_tools/           ← Milestone 5: IDE RPC, LSP proxies, DAP debuggers, and builds
├── orchestration/               ← Milestone 6: Multi-repo planning, context, and resource scheduling
└── certification/               ← Milestone 7: Compliance audits and Workspace Health dashboard
```

---

## Reading Order

| Step | Document / Directory | When to Read |
|------|----------------------|--------------|
| 1 | [`workspace_intelligence.md`](file:///Users/anzarakhtar/aios/docs/workspace/workspace_intelligence.md) | First — Establish the conceptual vision, design tenets, and system paradigms. |
| 2 | [`architecture.md`](file:///Users/anzarakhtar/aios/docs/workspace/architecture.md) | Before reviewing or implementing class models, background watchers, or process orchestration. |
| 3 | [`capabilities.md`](file:///Users/anzarakhtar/aios/docs/workspace/capabilities.md) | Before designing editor/IDE integrations, compiler parsers, or terminal stream monitors. |
| 4 | [`integration_strategy.md`](file:///Users/anzarakhtar/aios/docs/workspace/integration_strategy.md) | Before coding filesystem adapters, code chunkers, or vector memory indices. |
| 5 | [`security_model.md`](file:///Users/anzarakhtar/aios/docs/workspace/security_model.md) | Mandatory reading before implementing workspace execution tools, shell containment, or token validation. |
| 6 | [`roadmap.md`](file:///Users/anzarakhtar/aios/docs/workspace/roadmap.md) | To review sprint tasks, milestones, and mitigation plans. |
| 7 | [Project Discovery Hub →](file:///Users/anzarakhtar/aios/docs/workspace/project_discovery/README.md) | To explore repository boundary scans and classification heuristics. |
| 8 | [Codebase Hub →](file:///Users/anzarakhtar/aios/docs/workspace/codebase/README.md) | To explore AST compiling, Qdrant indexing, and static navigation. |
| 9 | [Source Control Hub →](file:///Users/anzarakhtar/aios/docs/workspace/source_control/README.md) | To explore commit DAGs, merge conflict mapping, and symbol history. |
| 10 | [Development Tools Hub →](file:///Users/anzarakhtar/aios/docs/workspace/development_tools/README.md) | To explore IDE RPC protocols, LSP/DAP adapters, and package manager support. |
| 11 | [Orchestration Hub →](file:///Users/anzarakhtar/aios/docs/workspace/orchestration/README.md) | To explore multi-project execution planning, context sizing, and scheduling. |
| 12 | [Certification Hub →](file:///Users/anzarakhtar/aios/docs/workspace/certification/README.md) | To review final compliance logs, scorecards, and engineering grades. |

---

## Core System Integration

The Development Workspace Intelligence subsystem directly integrates with several existing services defined in the [Engineering Bible](file:///Users/anzarakhtar/aios/docs/16_ENGINEERING_BIBLE.md):

* **Knowledge Hub Service**: Expands the `KnowledgeHubService` to index and search code symbols, file boundaries, and build graphs locally.
* **Tiered Memory System**: Maps AST-parsed code structures and repository indices into local vector storage (Qdrant) inside the `workspace_memory` collection to enable context-aware semantic retrieval.
* **Action Engine & Task Executor**: Equips the local executor with tool definitions for safe file writes, git operations, and terminal orchestrations.
* **Approval Engine**: Validates destructive commands (e.g. branch deletion, package installations, production deployments) via the local consensus loop before execution.
