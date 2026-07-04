# 10 — Decision Log (Architecture Decision Records)
**Version 1.0** · *Classified: For One Person Only* · *July 2026*

---

## Document Metadata
* **Purpose**: Define the Architecture Decision Record (ADR) process, lifecycle templates, and house the repository of historical architectural decisions made for the Personal AI OS.
* **Scope**: Governs all structural changes, dependency integrations, and core execution designs.
* **Audience**: Systems Architects, Lead Engineers, and AI coding agents.
* **Related Documents**:
  * [00_PROJECT_VISION.md](file:///Users/anzarakhtar/aios/docs/00_PROJECT_VISION.md) - Constitutional guiding principles.
  * [01_ENGINEERING_GUIDELINES.md](file:///Users/anzarakhtar/aios/docs/01_ENGINEERING_GUIDELINES.md) - Requirements for logging dependencies.
  * [02_ARCHITECTURE_GUIDELINES.md](file:///Users/anzarakhtar/aios/docs/02_ARCHITECTURE_GUIDELINES.md) - System composition roots.
* **Future Extensions**: New ADRs will be appended chronologically as design reviews require architectural changes.

---

## 1. The ADR Process & Lifecycle

### 1.1 Purpose of ADRs
Architecture Decision Records (ADRs) document the technical reasoning behind major structural design decisions. Code base comments and files explain *what* the system does, but only an ADR captures the context, problem, trade-offs, and consequences that explain *why* the design was selected. This prevents technical regression and re-debating settled designs.

### 1.2 Decision Lifecycle & Status Definitions
An ADR transitions through four distinct phases:

```
[Proposed] ➔ [Accepted] ➔ [Superseded] / [Deprecated]
```

* **Proposed**: The decision is logged and undergoing active evaluation or user alignment.
* **Accepted**: The decision has been approved and implemented in the repository.
* **Superseded**: A new ADR has replaced this decision with an alternative approach.
* **Deprecated**: The feature or pattern has been removed from the system.

### 1.3 ADR Template
```markdown
### ADR-XXXX: [Short Descriptive Title]
* **Status**: [Proposed | Accepted | Superseded | Deprecated]
* **Date**: [YYYY-MM-DD]
* **Context**: *What is the situation? What are the constraints?*
* **Problem**: *What is the specific issue we need to solve?*
* **Decision**: *What design, library, or pattern did we select?*
* **Alternatives Considered**: *List alternatives and why they were rejected.*
* **Trade-offs**: *Pros and Cons of the selected decision.*
* **Consequences**: *What is the impact on the codebase, tests, and future complexity?*
* **Related Documents**: *Relative links to specifications.*
* **Future Review**: *When or under what conditions should we re-evaluate this?*
```

---

## 2. Archive of Architectural Decisions

### ADR-0001: Local-First Architecture
* **Status**: Accepted
* **Date**: 2026-07-04
* **Context**: Personal AI OS manages sensitive data, workspace files, and career objectives.
* **Problem**: Cloud-first setups expose personal information to third parties and create internet latency.
* **Decision**: Make the system local-first. All configurations, memories, and task logs execute on the owner's machine.
* **Alternatives Considered**: Hosting the core on a VPS, SaaS server setups.
* **Trade-offs**: Local storage eliminates network latency but restricts operations to a single device.
* **Consequences**: Strict privacy boundaries are maintained; offline operations require local model setups (Ollama).

---

### ADR-0002: Not a Chatbot
* **Status**: Accepted
* **Date**: 2026-07-04
* **Context**: Chat interfaces default to verbose, conversational filler.
* **Problem**: General assistants dilute technical precision and encourage passive interaction.
* **Decision**: The system is an Operating System interface. Standard execution maps to CLI commands, and replies omit conversational preambles.
* **Alternatives Considered**: Standard chatbot GUI shell.
* **Trade-offs**: Fast keyboard execution requires memorizing command inputs.
* **Consequences**: Aligns with the *Minimal* and *Fast* guiding principles.

---

### ADR-0003: Selection of Python as Core Language
* **Status**: Accepted
* **Date**: 2026-07-04
* **Context**: The OS requires integrations with diverse LLMs, filesystems, and shell subprocesses.
* **Problem**: Writing low-level integrations in Rust or C++ slows down initial prototyping.
* **Decision**: Standardize on Python 3.10+ as the core language.
* **Alternatives Considered**: Go, TypeScript, Rust.
* **Trade-offs**: Python is slower than compiled languages but provides a rich package ecosystem.
* **Consequences**: Instant setups and access to python AI tools.

---

### ADR-0004: Brain Orchestration Design
* **Status**: Accepted
* **Date**: 2026-07-04
* **Context**: Natural language queries must map to complex, multi-step execution flows.
* **Problem**: Plain command mapping fails when objectives are unstructured (e.g., "Summarize recent changes").
* **Decision**: Deploy a central **Brain** component to plan objectives, select models, and call tools.
* **Alternatives Considered**: Hardcoded command routing scripts.
* **Trade-offs**: Adds LLM query latency but enables unstructured task automation.
* **Consequences**: Decoupled tool execution.

---

### ADR-0005: Modular Skill System
* **Status**: Accepted
* **Date**: 2026-07-04
* **Context**: The OS capabilities must expand dynamically without touching the kernel.
* **Problem**: Monolithic command registrations lead to tight coupling.
* **Decision**: Package capabilities into **Skills** (toml config, commands registry, prompts, custom agents).
* **Alternatives Considered**: Centralized core command file.
* **Trade-offs**: Skills require explicit metadata manifests, but keep modules isolated.
* **Consequences**: Skills are easy to delete and replace.

---

### ADR-0006: Provider Abstraction
* **Status**: Accepted
* **Date**: 2026-07-04
* **Context**: AI models and endpoints update rapidly.
* **Problem**: Calling OpenAI or Anthropic SDKs directly from skills couples business logic to provider APIs.
* **Decision**: Place all LLM calls behind the abstract `ModelService` interface.
* **Alternatives Considered**: Inline client calls in skill files.
* **Trade-offs**: Requires writing custom adapters for each provider.
* **Consequences**: Swapping models requires zero core logic changes.

---

### ADR-0007: OmniRoute Integration
* **Status**: Accepted
* **Date**: 2026-07-04
* **Context**: Request tokens can vary from light conversational inputs to massive file trees.
* **Problem**: Standard routing limits performance or inflates API costs.
* **Decision**: Use **OmniRoute** selector logic to evaluate token count, success rates, and offline variables before routing.
* **Alternatives Considered**: Simple static defaults configuration.
* **Trade-offs**: Adds selector code paths, but optimizes token billing.
* **Consequences**: Fallback chains execute automatically.

---

### ADR-0008: Dependency Injection (DI) Adoption
* **Status**: Accepted
* **Date**: 2026-07-04
* **Context**: Services must interact without direct import coupling.
* **Problem**: Global state dependencies make writing tests and mocking components difficult.
* **Decision**: Enforce constructor injection for all service dependencies.
* **Alternatives Considered**: Global singletons.
* **Trade-offs**: Constructors require explicit parameters, but dependencies are clear.
* **Consequences**: Allows clean pytest mocking.

---

### ADR-0009: Centralized Composition Root
* **Status**: Accepted
* **Date**: 2026-07-04
* **Context**: Construction of concrete classes can drift if scattered.
* **Problem**: Scattering imports of concrete services (e.g. `LocalEventBus`) violates Dependency Inversion.
* **Decision**: Wire the entire service graph inside `bootstrap.py`.
* **Alternatives Considered**: Scattered class instantiations inside core files.
* **Trade-offs**: Wires all components at boot, but keeps instantiation in one file.
* **Consequences**: System graphs are verified at startup.

---

### ADR-0010: Protected Core Policy
* **Status**: Accepted
* **Date**: 2026-07-04
* **Context**: Multiple agents and third-party plugins contribute changes.
* **Problem**: Editing core orchestrators (Kernel, Event Bus) to solve minor features leads to system regressions.
* **Decision**: Restrict core directories to a **Protected Core** status.
* **Alternatives Considered**: Open access to all repository locations.
* **Trade-offs**: Requires formal approvals for core changes, but prevents logic drift.
* **Consequences**: Protects stability.

---

### ADR-0011: Action Engine Approval Gates
* **Status**: Accepted
* **Date**: 2026-07-04
* **Context**: Mutating filesystem actions carry risk.
* **Problem**: Rogue LLM calls can accidentally delete or corrupt directory trees.
* **Decision**: Require explicit user approvals for all mutating file modifications and git updates.
* **Alternatives Considered**: Fully autonomous edits with zero prompts.
* **Trade-offs**: Interrupts workflows, but prevents catastrophic data loss.
* **Consequences**: High-risk actions block safely.

---

### ADR-0012: Separation of Task Executor
* **Status**: Accepted
* **Date**: 2026-07-04
* **Context**: Tasks represent logical plans; actions represent raw filesystem changes.
* **Problem**: Mixing task logic (progress, steps resume) with safety logic (backups, approvals) creates complex code.
* **Decision**: Isolate `TaskExecutor` from the `ActionEngine`.
* **Alternatives Considered**: Combined execution engine.
* **Trade-offs**: Adds routing layers but separates task state from transactional rollback logic.
* **Consequences**: Safe pipeline execution.

---

### ADR-0013: Conversation Engine Flat File Storage
* **Status**: Accepted
* **Date**: 2026-07-04
* **Context**: Dialogue threads must persist across system reboots.
* **Problem**: Complex relational databases require setup and migration overhead.
* **Decision**: Store conversation logs as local JSON files under `.aios_conversations/`.
* **Alternatives Considered**: PostgreSQL, local SQLite.
* **Trade-offs**: Flat files are slow on huge query counts, but easy to back up and track.
* **Consequences**: Simplified data model.

---

### ADR-0014: Tiered Memory Storage
* **Status**: Accepted
* **Date**: 2026-07-04
* **Context**: Systems must retain user achievements, active projects, and daily tasks.
* **Problem**: Retaining all dialogue records degrades model context windows.
* **Decision**: Implement tiered storage (Permanent, Long-Lived, Short-Lived) with background pruning cron jobs.
* **Alternatives Considered**: Persisting all logs indefinitely.
* **Trade-offs**: Requires background logic, but optimizes token efficiency.
* **Consequences**: Long-term context remains relevant.

---

### ADR-0015: Documentation as Source of Truth
* **Status**: Accepted
* **Date**: 2026-07-04
* **Context**: AI agents write code across separate, stateless sessions.
* **Problem**: Drifting code rules cause regression bugs.
* **Decision**: Make project guidelines and design specs the authoritative source of truth.
* **Alternatives Considered**: Relying on code comments or memory caches.
* **Trade-offs**: Requires writing documentation first, but keeps AI agents aligned.
* **Consequences**: Development velocity remains stable.

---

### ADR-0016: Extension Over Modification
* **Status**: Accepted
* **Date**: 2026-07-04
* **Context**: System capabilities will expand over a decade.
* **Problem**: Modifying existing functions to support features violates Open-Closed principles.
* **Decision**: Enforce extending behaviors via subclassing interfaces or subscribing to the Event Bus rather than editing core code.
* **Alternatives Considered**: In-place codebase alterations.
* **Trade-offs**: Requires structured designs, but keeps components decoupled.
* **Consequences**: Long-term codebase remains clean.
