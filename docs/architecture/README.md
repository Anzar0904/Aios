# Architecture Documentation

> This section covers the system design, kernel specification, and architectural evolution of the Personal AI OS.

---

## Core Architecture

| Document | Purpose |
|---|---|
| [KERNEL_SPECIFICATION.md](KERNEL_SPECIFICATION.md) | AI OS Kernel: runtime loop, event model, lifecycle contracts |
| [CORE_ARCHITECTURE.md](CORE_ARCHITECTURE.md) | Core package: layers, module boundaries, service registry |
| [BRAIN.md](BRAIN.md) | Brain orchestrator: reasoning pipeline and context assembly |
| [INTELLIGENCE_ENGINE.md](INTELLIGENCE_ENGINE.md) | Intelligence engine: model routing, provider selection, embeddings |
| [ACTION_ENGINE.md](ACTION_ENGINE.md) | Action engine: tool dispatch, skill execution, output formatting |
| [TASK_EXECUTOR.md](TASK_EXECUTOR.md) | Task executor: planning loop, approval gates, retries |
| [CONVERSATIONS.md](CONVERSATIONS.md) | Conversation model: session management and turn structure |

## Design Specifications

| Document | Purpose |
|---|---|
| [ARCHITECTURE_GUIDELINES.md](ARCHITECTURE_GUIDELINES.md) | Boundary decoupling rules and Dependency Inversion policy |
| [SYSTEM_DESIGN.md](SYSTEM_DESIGN.md) | Component diagrams, sequence maps, and event pipelines |
| [ARCHITECTURE_EVOLUTION_REPORT.md](ARCHITECTURE_EVOLUTION_REPORT.md) | Brain, Planner, and Selector v2 scaling strategy decisions |

---

## Related Sections
- [Services →](../services/README.md)
- [Database →](../database/README.md)
- [Runtime →](../runtime/README.md)
- [ADRs →](../adr/README.md)
