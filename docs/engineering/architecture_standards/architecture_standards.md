# Architecture Standards
**Engineering Bible — Milestone 3**
**Version 1.0** · *Classified: For One Person Only* · *July 2026*

> [!IMPORTANT]
> This directory defines the **Architecture Standards** of the Personal AI OS.
> It details the architectural paradigms, structural design guidelines, and system boundaries that govern the codebase.
> If any rule here conflicts with the Engineering Bible Foundation layer, the Foundation wins.

---

## Purpose

`docs/engineering/architecture_standards/` establishes the definitive guidelines for designing, structuring, and connecting software modules in the Personal AI OS. It answers:

> **How must I structure, layer, wire, and execute components in this system?**

Adherence to these standards is mandatory to preserve the system's long-term modularity, extensibility, and maintainability.

---

## Document Map

```
docs/engineering/architecture_standards/
├── architecture_standards.md   ← This file — navigation hub
├── layering.md                 ← Structural boundaries & layer constraints
├── dependency_injection.md     ← Constructor wiring & registry guidelines
├── service_lifecycle.md        ← Service state transitions & lifecycle hooks
├── event_bus.md                ← Strongly-typed event pub/sub contracts
├── provider_architecture.md    ← Model services & OmniRoute strategies
├── skill_architecture.md       ← Plugins, command registry & discovery rules
├── runtime_architecture.md     ← State machine, agent runtime & rollback rules
└── memory_architecture.md      ← Tiered storage, Qdrant vectors & Redis cache
```

---

## Reading Order

| Step | Document | When to Read |
|------|----------|--------------|
| 1 | [layering.md](layering.md) | Before designing or modifying a package structure |
| 2 | [dependency_injection.md](dependency_injection.md) | Before writing constructors or registering services |
| 3 | [service_lifecycle.md](service_lifecycle.md) | Before implementing service initialization or teardown |
| 4 | [event_bus.md](event_bus.md) | Before defining new events or subscriber callbacks |
| 5 | [provider_architecture.md](provider_architecture.md) | Before integrating new models or provider options |
| 6 | [skill_architecture.md](skill_architecture.md) | Before implementing skills, command registries, or custom prompts |
| 7 | [runtime_architecture.md](runtime_architecture.md) | Before modifying runtime tasks, orchestrators, or rollback states |
| 8 | [memory_architecture.md](memory_architecture.md) | Before updating memory persistence, vector search, or caches |

---

## Quick Reference — Architectural Hard Constraints

These rules admit no exceptions without a formal ADR in [10_DECISION_LOG.md](file:///Users/anzarakhtar/aios/docs/10_DECISION_LOG.md):

| Constraint | Architectural Rule |
|------------|---------------------|
| **Core Decoupling** | Internal core engines must never import extension skills or tools directly. |
| **Interface Dependencies** | Callers must depend on abstract service contracts, never on concrete `Local*` classes. |
| **Object Instantiation** | All dependencies must be wired inside the Composition Root (`bootstrap.py`) — direct service instantiations inside domain logic are prohibited. |
| **Lifecycle Compliance** | Every service must implement `ServiceLifecycle` and comply with its defined state transitions. |
| **Messaging Type-Safety** | All communication over the Event Bus must utilize registered, frozen `Event` dataclasses. |
| **Provider Decoupling** | Skills and engines are prohibited from importing vendor client SDKs directly; all LLM operations route through `ModelService`. |
| **Reversible Mutations** | File edits must be backed up by the `RollbackCoordinator` before execution, allowing full reversibility. |
| **High-Risk Operations** | Commands with risk ratings of `HIGH` must trigger an approval gate before executing. |
| **Tiered Caching** | Hot data resides in Redis; cold data persists to PostgreSQL/Qdrant. |

---

## Relationship to the Engineering Bible Foundation

```
docs/engineering/               ← Foundation (Milestone 1)
     │
     ├── coding_standards/      ← Coding Standards (Milestone 2)
     │
     └── architecture_standards/ ← YOU ARE HERE (Milestone 3)
              │
              ├── Implements ──▶  design_goals.md (modular boundaries)
              ├── Enforces   ──▶  02_ARCHITECTURE_GUIDELINES.md (DIP enforcement)
              └── Validates  ──▶  03_IMPLEMENTATION_GUIDELINES.md (skill registration)
```

---

## Versioning & Stability Contract

| Property | Rule |
|----------|------|
| **Version** | All files in this directory share the same version as the Engineering Bible |
| **Mutations** | Changes must be committed in a dedicated `docs:` commit, never mixed with feature work |
| **Deprecation** | No architectural pattern may be altered or retired without an ADR |
| **AI Authorship** | AI-generated commits carry `Co-authored-by: AI-agent <assistant@personal-ai-os.local>` |

---

*Engineering Bible Architecture Standards · Personal AI OS · Sprint 8 M3 · Governed by [02_ARCHITECTURE_GUIDELINES.md](file:///Users/anzarakhtar/aios/docs/02_ARCHITECTURE_GUIDELINES.md)*
