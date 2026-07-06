# Architectural Layering Standards
**Engineering Bible — Milestone 3**
**Version 1.0** · *Classified: For One Person Only* · *July 2026*

---

## 1. The 5-Tier Layered Architecture

To prevent structural decay and ensure that code remains testable and modular for over a decade, the Personal AI OS is strictly organized into five distinct vertical layers.

```
       +-------------------------------------------------+
       |         LAYER 1: USER INTERFACE / REPL          |
       |  (cli.py, parsing inputs, displaying output)    |
       +-----------------------+-------------------------+
                               |
                               v
       +-------------------------------------------------+
       |         LAYER 2: KERNEL ORCHESTRATION           |
       |  (kernel.py, registry.py, configuration load)   |
       +-----------------------+-------------------------+
                               |
                               v
       +-------------------------------------------------+
       |            LAYER 3: SERVICE LAYER               |
       | (Abstract service contracts & concrete services) |
       +-----------------------+-------------------------+
                               |
                               v
       +-------------------------------------------------+
       |          LAYER 4: EXECUTION ENGINES             |
       |    (Brain, TaskExecutor, ActionEngine, plans)    |
       +-----------------------+-------------------------+
                               |
                               v
       +-------------------------------------------------+
       |         LAYER 5: EXTENSION & PLUGINS            |
       |    (skills/, tool submodules, model endpoints)  |
       +-------------------------------------------------+
```

---

## 2. Layer Definitions & Responsibilities

### Layer 1: User Interface / REPL Layer
* **Files**: `cli.py`
* **Purpose**: Capture interactive user input, resolve raw queries into intents, format execution results, and render terminal interfaces.
* **Responsibilities**:
  * Loop continuously to capture keystrokes and line inputs.
  * Delegate natural language validation and parsing to the Intent Resolver.
  * Render outputs, error messages, and progress widgets using markdown formatting.
* **Constraint**: Contains zero business logic, file mutations, or direct model client interactions.

### Layer 2: Kernel Orchestration Layer
* **Files**: `kernel.py`, `registry.py`, `config.py`
* **Purpose**: Coordinates runtime process state, loads environmental preferences, and bootstraps core registry systems.
* **Responsibilities**:
  * Load system configurations from `config/config.toml` at startup.
  * Track and update runtime status (`HALTED` ➔ `BOOTING` ➔ `READY` ➔ `BUSY` ➔ `SHUTTING_DOWN`).
  * Enforce service startup and teardown lifecycles.
* **Constraint**: The Kernel must never import execution engines, skill packages, or database repositories directly.

### Layer 3: Service Layer
* **Files**: `core/src/aios/services/` (Contracts like `event_bus.py`, implementations like `event_bus_impl.py`).
* **Purpose**: Defines system interfaces and provides long-lived stateful services (e.g., event dispatching, session managers, context checkers).
* **Responsibilities**:
  * Expose stable abstract interface boundaries (e.g. `EventBusService`, `SessionService`, `MemoryService`).
  * Implement service behaviors behind strict interface contracts (e.g. `LocalEventBus`, `LocalSessionService`).
* **Constraint**: All service-to-service communication must route through registered interfaces in the `ServiceRegistry`.

### Layer 4: Execution Engine Layer
* **Files**: `core/src/aios/brain/`, `core/src/aios/services/action/`, `core/src/aios/services/task/`
* **Purpose**: Provides orchestrators that resolve complex goals, compile plans, and execute mutating steps.
* **Responsibilities**:
  * Brain: Decompose natural language requests into structured execution commands.
  * Task Executor: Run sequences of command steps and write outputs to `.aios_tasks/`.
  * Action Engine: Perform safe, atomic, reversible filesystem modifications.
* **Constraint**: Engines must be stateless per request and rely on the Service Layer for persisting execution logs, cache buffers, and dialog states.

### Layer 5: Extension & Plugins Layer
* **Files**: `skills/`, tool integrations, model vendor APIs.
* **Purpose**: Houses domain-specific logic, automated commands, third-party system integrations, and raw model provider connections.
* **Responsibilities**:
  * Declare skills via metadata manifests (`skill.toml`) and command hook registrations (`commands.py`).
  * Wrap third-party developer platforms (e.g., GitHub, n8n) and host prompts under `prompts/`.
* **Constraint**: Plugins must never alter core kernel configurations. They must interact with system resources purely through whitelisted command boundaries and service contracts.

---

## 3. Strict Boundary & Dependency Rules

To prevent coupling and circular imports, the following dependency direction rules must be enforced:

1. **Dependency Direction (Inward-Only)**: Lower layers are completely unaware of higher layers. Higher layers may import contracts and resolve types from lower layers, but lower layers must never import files from higher layers.
2. **Interface-Only Imports**: Cross-layer interactions must depend on abstract service contracts (from Layer 3) rather than concrete implementations. For example, Layer 4 (`Brain`) imports `ModelService` from Layer 3, not `LocalModelService` from Layer 3 or vendor libraries from Layer 5.
3. **No Direct Instantiation**: Code inside Layers 1, 3, 4, and 5 must never instantiate other services directly. All instantiation, wiring, and lifetime configurations are isolated in the Composition Root (`bootstrap.py`).

---

*Engineering Bible Architecture Standards · Personal AI OS · Sprint 8 M3 · Governed by [02_ARCHITECTURE_GUIDELINES.md](file:///Users/anzarakhtar/aios/docs/02_ARCHITECTURE_GUIDELINES.md)*
