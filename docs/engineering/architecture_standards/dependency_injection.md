# Dependency Injection & Registry Standards
**Engineering Bible — Milestone 3**
**Version 1.0** · *Classified: For One Person Only* · *July 2026*

---

## 1. Composition Root (`bootstrap.py`)

All object instantiation, constructor wiring, and service registration are isolated within a single, dedicated module: the **Composition Root** located at [bootstrap.py](file:///Users/anzarakhtar/aios/core/src/aios/bootstrap.py).

### Composition Root Rules
* **No Inline Service Instantiation**: Direct instantiations of services or managers outside `bootstrap.py` are strictly prohibited. Classes must not instantiate their dependencies using `self.dependency = ConcreteService()`.
* **Centralized Configuration Loading**: The Composition Root parses system configuration (`config.toml`) at boot time and injects configuration sections (such as model configuration, path boundaries, or feature toggles) directly into constructor parameters.
* **Single Location for Mocking**: During testing, the test harness replicates the Composition Root's wiring patterns but replaces production service instances with mock implementations (e.g. `MockAgent`, `MockMemoryService`). This isolates test setups without modifying production code.

---

## 2. Service Registry (`registry.py`)

The `ServiceRegistry` acts as the runtime service broker of the Personal AI OS. It enables decoupled access to core systems while maintaining structural boundaries.

### Registry Rules
* **Interface-Based Registration**: Concrete service implementations (e.g. `LocalEventBus`, `LocalMemoryService`) must be registered using their abstract interface type as the lookup key.
  
  ```python
  # CORRECT registration pattern in bootstrap.py
  registry.register(EventBusService, LocalEventBus())
  ```
  
  ```python
  # INCORRECT registration pattern (violates contract decoupling)
  registry.register(LocalEventBus, LocalEventBus())
  ```

* **Lookup Contracts**: Callers must retrieve services using the abstract interface class, never the concrete service implementation.
  
  ```python
  # CORRECT lookup inside systems
  event_bus = registry.get(EventBusService)
  ```
  
  ```python
  # INCORRECT lookup (breaks decoupling)
  event_bus = registry.get(LocalEventBus)
  ```

* **No Duplicate Registrations**: Registering multiple instances under the same service interface type is prohibited and must trigger a `ValueError`.
* **Runtime Validation**: The registry validates that the registered instance is a subclass of `ServiceLifecycle` and matches the registered interface type.

---

## 3. Constructor Injection Standards

All services, executors, and coordinators must receive their dependencies explicitly via their constructors.

### Injection Standards
1. **Abstract Types**: Parameter annotations must declare the abstract interface class rather than a concrete class.
2. **Immutability**: Injected dependencies must be stored in read-only private fields (annotated with leading underscores in Python) and should not be modified after initialization.
3. **Mocking Support**: Constructors must accept all dependencies as parameters, facilitating clean unit testing without invoking global state or setup decorators.

### Constructor Injection Example

```python
from aios.services.event_bus import EventBusService
from aios.services.memory import MemoryService
from aios.services.base import ServiceLifecycle

class LocalAgentManager(ServiceLifecycle):
    def __init__(self, event_bus: EventBusService, memory: MemoryService) -> None:
        """
        Dependencies are injected via the constructor using abstract types.
        No local instantiation or global state access.
        """
        self._event_bus = event_bus
        self._memory = memory
```

---

*Engineering Bible Architecture Standards · Personal AI OS · Sprint 8 M3 · Governed by [02_ARCHITECTURE_GUIDELINES.md](file:///Users/anzarakhtar/aios/docs/02_ARCHITECTURE_GUIDELINES.md)*
