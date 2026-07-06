# Event Bus Communication Standards
**Engineering Bible — Milestone 3**
**Version 1.0** · *Classified: For One Person Only* · *July 2026*

---

## 1. Strong Event Typing & Immutability

All communication between isolated modules in the Personal AI OS is mediated by the Event Bus (`EventBusService`). The bus enforces type safety and prevents state corruption.

### Event Type Constraints
* **Inheritance**: All events must inherit from the `Event` class defined in [event_bus.py](file:///Users/anzarakhtar/aios/core/src/aios/services/event_bus.py).
* **Immutability**: Event classes must be declared as frozen dataclasses (`@dataclass(frozen=True)`). Once instantiated, event payload properties cannot be modified.
* **Keyword-Only Parameters**: To prevent parameter ordering issues, event constructors must enforce keyword-only arguments using the `kw_only=True` flag in the dataclass decorator.

```python
from dataclasses import dataclass
from aios.services.event_bus import Event

@dataclass(frozen=True, kw_only=True)
class ContextLoadedEvent(Event):
    """Event published when a Workspace Context is successfully loaded."""
    project_name: str
    project_root: str
```

---

## 2. Event Registration Boundary

To maintain messaging discipline, every event type must be registered with the bus before it can be utilized in publishes or subscriptions.

```python
# Registration in bootstrap.py or during service setup
event_bus.register_event_type(ContextLoadedEvent)
```

If an unregistered event type is published or subscribed to, the bus throws a `ValueError`. This prevents runtime messaging leaks and helps trace invalid flows.

---

## 3. Synchronous Routing & Failure Isolation

* **Lightweight Callbacks**: The Event Bus routes events synchronously to all registered subscriber callbacks in-memory. Subscribers must complete execution quickly. Long-running tasks must offload execution to a separate thread pool or a queued process.
* **Failure Isolation**: An exception raised within one subscriber callback must never interrupt other subscribers or cascade back to the event publisher. The Event Bus catches subscriber exceptions, logs the error with traceback detail using `logger.error`, and continues dispatching the event to the remaining subscribers.

---

## 4. Key System Events

The system relies on a set of core telemetry and lifecycle events:

| Event Class | Publisher | Trigger |
|-------------|-----------|---------|
| `KernelStartedEvent` | `Kernel` | Dispatched after the kernel and all services transition to the `READY` state. |
| `ContextLoadedEvent` | `ContextService` | Dispatched when a workspace context is loaded (contains paths and git branches). |
| `SessionStartedEvent` | `SessionService` | Dispatched when an interactive dialogue session starts. |
| `SessionEndedEvent` | `SessionService` | Dispatched when the active session closes or the system shuts down. |
| `ToolStartedEvent` | `ToolService` | Dispatched prior to invoking a command tool. |
| `ToolCompletedEvent` | `ToolService` | Dispatched when a tool command completes successfully. |
| `ToolFailedEvent` | `ToolService` | Dispatched when a tool encounters an error. |
| `AgentStartedEvent` | `AgentRuntimeService` | Dispatched before launching an agent executor. |
| `AgentCompletedEvent` | `AgentRuntimeService` | Dispatched when an agent completes successfully. |
| `AgentFailedEvent` | `AgentRuntimeService` | Dispatched when an agent run fails. |

---

*Engineering Bible Architecture Standards · Personal AI OS · Sprint 8 M3 · Governed by [02_ARCHITECTURE_GUIDELINES.md](file:///Users/anzarakhtar/aios/docs/02_ARCHITECTURE_GUIDELINES.md)*
