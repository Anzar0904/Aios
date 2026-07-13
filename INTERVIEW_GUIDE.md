# 18 — Interview Guide (Technical Q&A Handbook)
**Version 1.0** · *Classified: For One Person Only* · *July 2026*

---

## Document Metadata
* **Purpose**: Provide a comprehensive technical preparation guide, architectural Q&A, and system design handbook for presenting and reviewing the Personal AI OS.
* **Scope**: Covers all architectural paradigms, model strategies, memory tiers, security gates, and technology selections.
* **Audience**: Technical Architects, Presenters, Interview Candidates, and AI agents.
* **Related Documents**:
  * [00_PROJECT_VISION.md](file:///Users/anzarakhtar/aios/docs/00_PROJECT_VISION.md) - Constitutional visions and objectives.
  * [02_ARCHITECTURE_GUIDELINES.md](file:///Users/anzarakhtar/aios/docs/02_ARCHITECTURE_GUIDELINES.md) - System composition roots.
  * [15_SYSTEM_DESIGN.md](file:///Users/anzarakhtar/aios/docs/15_SYSTEM_DESIGN.md) - Context and container design flows.
* **Future Extensions**: This handbook will be expanded with mock scenario guides as daemon implementations and multi-agent systems are deployed.

---

## 1. Core Pitch & Project Overview

### 1.1 The Elevator Pitch
> "Personal AI OS is a local-first, privacy-focused operating system designed to serve as a persistent extension of a single user's mind. Unlike generic chat interfaces that treat every session as a clean slate and expose private code to external servers, this system consolidates software development, research, and project workflows behind a secure orchestration kernel. It utilizes a tiered, context-aware memory database that synchronizes with the active local workspace, and enforces strict, transaction-based action approval gates. It represents a decade-long bet on reclaiming human attention by automating boring workflows while keeping the user in control of all design judgment."

---

## 2. Architectural Q&A Registry

### Topic 1: Kernel vs. Skill Decoupling
* **Common Interview Question**: *"Why did you separate the Kernel from specific capabilities? Why not just build direct command handlers inside the main execution loop?"*
* **Expected Answer**: The Kernel acts as a dumb-on-purpose orchestrator. It manages service lifecycles (boot, ready, teardown) and abstract routing contracts via a `ServiceRegistry` but possesses zero domain knowledge. Capabilities are packaged as standalone, modular **Skills** discovered dynamically.
* **Why Chosen**: Swapping a model, updating a skill command, or adding a provider must require zero changes to core kernel files.
* **Alternatives Considered**: Monolithic command files.
* **Trade-offs**: Decoupled skills require explicit Toml configuration schemas, which slightly increases configuration overhead.
* **Follow-up Questions**: *"How do skills communicate back to the system context?"* (Answer: They query the Context Service interface injected at boot).
* **Common Mistakes to Avoid**: Describing the Kernel as "intelligent" or saying it directly runs terminal scripts.

---

### Topic 2: Dependency Inversion & Composition Root
* **Common Interview Question**: *"Why did you avoid static imports for concrete services? How is the application graph wired?"*
* **Expected Answer**: To achieve full compliance with Dependency Inversion. Core components depend strictly on abstract service interfaces defined under `aios.services`. Instantiation is isolated to a single centralized Composition Root in `bootstrap.py`.
* **Why Chosen**: Prevents tight coupling, avoids global variables, and enables clean class mocking in tests.
* **Alternatives Considered**: Singleton patterns, service location decorators.
* **Trade-offs**: Requires explicit constructor parameter definitions on all service declarations.
* **Follow-up Questions**: *"What happens if a service registration fails at boot?"* (Answer: The Composition Root aborts, and the Kernel shuts down cleanly).
* **Common Mistakes to Avoid**: Saying that concrete classes are imported globally.

---

### Topic 3: The Event Bus Architecture
* **Common Interview Question**: *"Why is the Local Event Bus synchronous and local-first?"*
* **Expected Answer**: To keep the system simple-by-default. Synchronous delivery inside a single process eliminates the need for background threads, task queues, or retry managers.
* **Why Chosen**: Minimizes execution overhead and latency.
* **Alternatives Considered**: Celery, Redis channels, asyncio event loops.
* **Trade-offs**: If a subscriber callback performs a slow, blocking task, it freezes the bus.
* **Follow-up Questions**: *"How do you isolate handler failures?"* (Answer: The bus catches handler exceptions and logs them without interrupting remaining subscribers).
* **Common Mistakes to Avoid**: Describing the event bus as a persistent message broker or database stream.

---

### Topic 4: Memory Tiering
* **Common Interview Question**: *"How does the system prevent model context windows from bloating?"*
* **Expected Answer**: The Memory Engine segregates user data into Permanent (never expires), Long-Lived (1-3 years), and Short-Lived (days/weeks) tiers. Short-term logs are pruned, and long-term history is compressed when dialogue turns exceed 10.
* **Why Chosen**: Optimizes prompt token billing and keeps context payloads highly relevant.
* **Alternatives Considered**: Loading full conversation history.
* **Trade-offs**: Requires running background summarization tasks.
* **Follow-up Questions**: *"How does the system query memory?"* (Answer: It filters memory blocks matching the active workspace context).
* **Common Mistakes to Avoid**: Saying memory is just raw text search.

---

### Topic 5: Action Engine Transaction Safety
* **Common Interview Question**: *"How do you guarantee that autonomous code modifications do not corrupt local repositories?"*
* **Expected Answer**: The Action Engine decomposes tasks into steps (WRITE, MODIFY, DELETE) and validates risk weights. Mutating actions cache target file contents before executing change. If a step fails, the `RollbackCoordinator` restores backups in reverse order.
* **Why Chosen**: Protects workspace integrity.
* **Alternatives Considered**: Direct bash script executions.
* **Trade-offs**: Backup caching slightly increases file I/O operations.
* **Follow-up Questions**: *"When does the engine require approvals?"* (Answer: High-risk steps block until explicit confirmation).
* **Common Mistakes to Avoid**: Saying rollbacks are handled by Git commits.

---

## 3. Subsystem Architecture Deep Dives

### 3.1 Security & Tool Sandboxing
* **Question**: *"How do you prevent path traversal exploits via prompts?"*
* **Answer**: All file paths are resolved using `.resolve()` to normalize relative directories (e.g. `../`) and dereference symbolic links. The canonical path is checked using `.is_relative_to(workspace_root)` to ensure it lies inside the active workspace. System errors are redacted before returning them to the model.

### 3.2 Performance Optimization
* **Question**: *"What are the bottlenecks, and how are they monitored?"*
* **Answer**: The primary bottleneck is LLM token generation latency. The system optimizes this by enforcing strict prompt management, caching long-term summaries, and utilizing the local-first OmniRoute selector to route lightweight queries to faster local engines.

---

## 4. Behavioral Scenario Reviews

### Scenario 1: Swapping Model Providers
* **Context**: The primary provider (e.g. Anthropic) undergoes a server outage.
* **Expected Action**: Under OmniRoute, the provider selector catches the connection exception, records a failure, and routes subsequent requests to alternative endpoints (e.g., OpenRouter or local Ollama instances) automatically.

### Scenario 2: Dealing with Legacy Code
* **Context**: Adding features to files that cross size or complexity boundaries.
* **Expected Action**: Adhere to the *Definition of Done*. Split monolithic modules before files exceed 400 lines, extract sub-functions to keep cyclomatic complexity under 10, and write corresponding tests.
