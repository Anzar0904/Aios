# 19 — Glossary (Official Project Vocabulary)
**Version 1.0** · *Classified: For One Person Only* · *July 2026*

---

## Document Metadata
* **Purpose**: Establish the official terminology, technical definitions, component relations, and common misunderstandings for all key vocabulary terms used in the Personal AI OS.
* **Scope**: Governs all structural terminology across codebases, configurations, and documentation files.
* **Audience**: Core Developers, Maintainers, and AI coding agents.
* **Related Documents**:
  * [00_PROJECT_VISION.md](file:///Users/anzarakhtar/aios/docs/00_PROJECT_VISION.md) - Constitutional core principles.
  * [02_ARCHITECTURE_GUIDELINES.md](file:///Users/anzarakhtar/aios/docs/02_ARCHITECTURE_GUIDELINES.md) - Component systems design boundaries.
  * [17_KNOWLEDGE_BASE.md](file:///Users/anzarakhtar/aios/docs/17_KNOWLEDGE_BASE.md) - System encyclopedia.
* **Future Extensions**: This glossary will be updated chronologically as new modules, architectural paradigms, or tools are merged into the monorepo.

---

## 1. Architecture Terms

### Kernel
* **Definition**: The orchestration engine of the OS, responsible for loading configurations and managing service lifecycles.
* **Purpose**: Decouple infrastructure orchestration from domain-specific skills.
* **Context**: Static imports are decoupled from concrete classes; interacts only via interfaces.
* **Related Components**: `ServiceRegistry`, `LocalEventBus`.
* **Related Documents**: [02_ARCHITECTURE_GUIDELINES.md](file:///Users/anzarakhtar/aios/docs/02_ARCHITECTURE_GUIDELINES.md).
* **Common Misunderstandings**: Believing the Kernel contains AI models or task planning logic. (The Kernel is dumb-on-purpose).
* **Related Terms**: `Brain`, `ServiceRegistry`.

### Brain
* **Definition**: The central intelligence coordinator that plans tasks, selects models, and routes requests to skills.
* **Purpose**: Resolve natural language objectives by orchestrating tools and context.
* **Context**: Instantiated by the Agent Runtime during query evaluation.
* **Related Components**: `ModelService`, `CommandRegistry`, `ToolService`.
* **Related Documents**: [15_SYSTEM_DESIGN.md](file:///Users/anzarakhtar/aios/docs/15_SYSTEM_DESIGN.md).
* **Common Misunderstandings**: Confusing the Brain with the Kernel. (The Brain owns intelligence; the Kernel owns runtime states).
* **Related Terms**: `Kernel`, `OmniRoute`.

### Event Bus
* **Definition**: A local, synchronous, typed channel facilitating messaging between services.
* **Purpose**: Decouple publishers from subscribers to prevent tight interface coupling.
* **Context**: Managed by `LocalEventBus` under services registration.
* **Related Components**: `Event`, `ContextLoadedEvent`.
* **Related Documents**: [02_ARCHITECTURE_GUIDELINES.md](file:///Users/anzarakhtar/aios/docs/02_ARCHITECTURE_GUIDELINES.md).
* **Common Misunderstandings**: Assuming it is a multi-threaded asynchronous queue or persistent broker (like Kafka/RabbitMQ).
* **Related Terms**: `Kernel`.

### Composition Root
* **Definition**: The single location in the codebase where the dependency graph is instantiated.
* **Purpose**: Wire all concrete services and inject dependencies through constructors.
* **Context**: Implemented exclusively in [bootstrap.py](file:///Users/anzarakhtar/aios/core/src/aios/bootstrap.py).
* **Related Components**: `ServiceRegistry`.
* **Related Documents**: [02_ARCHITECTURE_GUIDELINES.md](file:///Users/anzarakhtar/aios/docs/02_ARCHITECTURE_GUIDELINES.md).
* **Common Misunderstandings**: Spreading class initializations across multiple submodules.
* **Related Terms**: `Dependency Injection`.

### Protected Core
* **Definition**: Core directories (`kernel.py`, `brain/`, event bus, memory, action engine) restricted from dynamic alteration.
* **Purpose**: Protect codebase stability.
* **Context**: Enforced during code reviews and AI coding guidelines.
* **Related Components**: All core orchestrators.
* **Related Documents**: [03_IMPLEMENTATION_GUIDELINES.md](file:///Users/anzarakhtar/aios/docs/03_IMPLEMENTATION_GUIDELINES.md).
* **Common Misunderstandings**: Believing skills cannot register new tool functions. (Skills extend behaviors via registries).
* **Related Terms**: `Extension Over Modification`.

---

## 2. AI & Prompt Terms

### OmniRoute
* **Definition**: A dynamic model selector routing requests to providers based on cost, context window limits, and connection health.
* **Purpose**: Optimize token costs and handle provider failovers.
* **Context**: Evaluated by the `ProviderSelector` in providers execution.
* **Related Components**: `ModelService`, `ProviderRouter`.
* **Related Documents**: [04_AI_MODEL_STRATEGY.md](file:///Users/anzarakhtar/aios/docs/04_AI_MODEL_STRATEGY.md).
* **Common Misunderstandings**: Assuming it requires external routing cloud APIs. (OmniRoute runs local).
* **Related Terms**: `Model Intelligence Layer`.

### History Compression
* **Definition**: Automated context summarization triggered when dialogue turns exceed 10.
* **Purpose**: Prevent token context windows from bloating.
* **Context**: Managed by the `Conversation` service.
* **Related Components**: `ConversationSummary`.
* **Related Documents**: [04_AI_MODEL_STRATEGY.md](file:///Users/anzarakhtar/aios/docs/04_AI_MODEL_STRATEGY.md).
* **Common Misunderstandings**: Thinking it deletes the entire conversation thread. (The latest 4 turns are preserved verbatim).
* **Related Terms**: `Conversation Summary`.

---

## 3. Workflow & Development Terms

### Action
* **Definition**: A low-level filesystem or Git mutation task.
* **Purpose**: Decompose plan edits into reversible transaction steps.
* **Context**: Managed by the `ActionEngine`.
* **Related Components**: `ActionExecutor`, `RollbackCoordinator`.
* **Related Documents**: [03_IMPLEMENTATION_GUIDELINES.md](file:///Users/anzarakhtar/aios/docs/03_IMPLEMENTATION_GUIDELINES.md).
* **Common Misunderstandings**: Believing actions are run directly without risk evaluations or rollback caches.
* **Related Terms**: `Task`, `Rollback`.

### Task
* **Definition**: A high-level pipeline plan composed of registered command steps.
* **Purpose**: Decompose natural language objectives into executable CLI actions.
* **Context**: Managed by the `TaskExecutor`.
* **Related Components**: `TaskPlanner`, `ProgressTracker`.
* **Related Documents**: [03_IMPLEMENTATION_GUIDELINES.md](file:///Users/anzarakhtar/aios/docs/03_IMPLEMENTATION_GUIDELINES.md).
* **Common Misunderstandings**: Conflating tasks with low-level actions. (Tasks plan commands; actions execute mutations).
* **Related Terms**: `Action`.

### ADR (Architecture Decision Record)
* **Definition**: A document detailing the rationale behind major architectural choices.
* **Purpose**: Provide a paper trail of tradeoffs.
* **Context**: Appended to [10_DECISION_LOG.md](file:///Users/anzarakhtar/aios/docs/10_DECISION_LOG.md).
* **Related Documents**: [10_DECISION_LOG.md](file:///Users/anzarakhtar/aios/docs/10_DECISION_LOG.md).
* **Common Misunderstandings**: Believing ADRs are only written for new features. (ADRs also govern tool selections and library replacements).
* **Related Terms**: `PRD`, `DRD`.

---

## 4. Future Terms

### Visual Block
* **Definition**: A monospaced widget panel displaying real-time metrics (e.g. task progress bars, memory trees).
* **Purpose**: Provide high-density information displays.
* **Context**: Planned UI components for CLI streams and Next.js renderer dashboards.
* **Related Components**: Renderer.
* **Related Documents**: [13_DRD.md](file:///Users/anzarakhtar/aios/docs/13_DRD.md).
* **Common Misunderstandings**: Thinking visual blocks are standard, heavy web graphic cards.
* **Related Terms**: `Renderer`.
