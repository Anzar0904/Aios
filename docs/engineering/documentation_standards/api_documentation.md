# API Documentation & Docstring Standards
**Engineering Bible — Milestone 5**
**Version 1.0** · *Classified: For One Person Only* · *July 2026*

---

## 1. Type Hinting Requirements

To ensure type safety and aid IDE auto-completion, all public Python modules, class definitions, and service interfaces must be fully type-hinted.

### Type Hinting Rules
* **No `Any` Types**: The use of the `Any` type annotation is prohibited. Use specific types, union types (`str | int`), generic types (`TypeVar`), or abstract interfaces.
* **Constructor Type Hints**: Constructors (`__init__`) must include type hints for all parameters and return `None`.
* **Public Method Annotations**: Every public method must declare types for all arguments and return values.

---

## 2. Google-Style Docstrings

The Personal AI OS codebase uses **Google-style docstrings** for inline Python documentation. Docstrings are required on all public modules, classes, and methods.

### 1. Class Docstrings
Class docstrings must describe the class's purpose, its main responsibilities, and list its public properties.

```python
class LocalMemoryService(MemoryService):
    """
    Manages the collection, lifecycle, and storage of user memory records.

    Attributes:
        workspace_root: Absolute filesystem path to the current project.
        cache_duration: Timeout duration in seconds for cache flushes.
    """
```

### 2. Method & Function Docstrings
Method docstrings must include:
* A concise summary of the method's behavior.
* **Args**: Names, types, and descriptions of all parameters.
* **Returns**: The type and description of the return value.
* **Raises**: A list of exceptions the method may throw and the conditions that trigger them.

```python
def execute_intent(self, intent: Intent) -> IntentResult:
    """
    Executes a structured Intent by delegating to the Agent Runtime.

    Args:
        intent: The parsed and validated Intent object.

    Returns:
        An IntentResult containing execution status and response messages.

    Raises:
        RuntimeError: If the Kernel is not in the READY or BUSY state.
        ValueError: If the Intent validation checks fail.
    """
```

---

## 3. Module-Level Docstrings

Every Python file must begin with a module-level docstring summarizing its purpose, public API classes, and dependencies.

```python
"""
Event Bus Implementation Module.

This module provides the concrete `LocalEventBus` implementation, managing
synchronous, strongly-typed messaging between core services.

Classes:
    LocalEventBus: A lightweight in-memory event bus service.
"""
```

---

*Engineering Bible Documentation Standards · Personal AI OS · Sprint 8 M5 · Governed by [07_DOCUMENTATION_GUIDELINES.md](file:///Users/anzarakhtar/aios/docs/07_DOCUMENTATION_GUIDELINES.md)*
