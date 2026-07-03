# Personal AI OS

Monorepo root for the Personal AI OS.

## Repository Architecture

This repository is structured as a single monorepo with multiple workspaces for core orchestration and skill packages.

```text
/ (root)
├── config/                 # Environment configuration files
│   └── config.toml         # Active system configuration
├── core/                   # The Core OS Package
│   ├── src/
│   │   └── aios/           # Main core logic package
│   │       ├── cli.py      # CLI REPL loop (entry point)
│   │       ├── kernel.py   # Kernel orchestration engine
│   │       ├── registry.py # Service registration index
│   │       └── services/   # Service contract interfaces and stubs
│   └── tests/              # Core unit and integration tests
├── pyproject.toml          # Shared workspace tools config (Ruff, Pytest)
└── README.md
```

## Kernel Runtime Architecture

The Kernel is the orchestration core of the OS, designed with zero business logic or domain awareness. Its lifecycle consists of:
1. **HALTED**: The runtime is offline.
2. **BOOTING**: Loading configuration and registering service modules.
3. **READY**: Registered services are initialized and ready to start interactive loops or handle sessions.
4. **BUSY**: Actively executing skill requests or tool commands.
5. **SHUTTING_DOWN**: Stopping services in reverse order of registration.

### Service Registry & Decoupled Communication
Core services (`Context`, `Memory`, `Session`, `Model`, `Tool`, `EventBus`) register via the `ServiceRegistry` using abstract interface contracts. All cross-module service interactions are routed through contracts to prevent tight coupling.

### Event Bus Architecture
The Event Bus (`LocalEventBus`) facilitates lightweight, synchronous communication between services:
* **Strongly Typed**: All events inherit from `Event` with type-safe parameters, preventing unstructured dictionary parsing.
* **Registered Event Types**: Event classes must be registered via `register_event_type` before subscription or publication to keep interfaces structured.
* **Synchronous & Local-First**: No background worker processes, threads, or retries are used, in line with the boring-by-default philosophy.

### Context Service Architecture
The Context Service (`LocalContextService`) inspects the host workspace environment during boot:
* **Strongly Typed Context**: Returns `WorkspaceContext` containing the CWD, Git repo root path, active Git branch, project root, and project name.
* **Graceful Fallbacks**: If git is unavailable or the directory is not inside a git repository, the service skips git resolution without raising exceptions, falling back to the current directory as the project root.
* **Workspace Change Monitoring**: Publishes `ContextLoadedEvent` on first detection and `ContextChangedEvent` if the workspace changes during a run, facilitating dynamic adjustments.

## Running the OS

Bootstrap dependency installation using `uv` or `pip`:

```bash
# Setup virtual environment and install package in editable mode
python3 -m venv .venv
source .venv/bin/activate
pip install -e ./core pytest ruff
```

To boot the system:

```bash
aios
```

## Testing and Linting

To run unit and integration tests:
```bash
pytest
```

To verify code style and formatting:
```bash
ruff check ./core
ruff format --check ./core
```

