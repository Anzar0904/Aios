# AI Code Generation Rules
**Engineering Bible — Milestone 6**
**Version 1.0** · *Classified: For One Person Only* · *July 2026*

---

## 1. Compliance with Coding Standards

AI-generated code must conform to the project's coding standards. The following boundaries are strictly enforced:

* **File Line Limit**: Source files must not exceed **400 lines**.
* **Complexity Budget**: Methods must maintain a cyclomatic complexity of **10 or less**.
* **Parameter Limits**: Functions and methods must accept at most **4 parameters** (use dataclasses or configuration parameters if more are needed).
* **Line Length**: Lines of code must be at most **100 characters** long.

---

## 2. Strong Type Annotations

All generated code must be fully type-hinted to improve code readability and static analysis.

### Typing Rules
* **No Bare `Any`**: The use of the `Any` type annotation is prohibited. Use Union types, generic types (`TypeVar`), or abstract interfaces.
* **Complete Method Signatures**: Public methods must declare types for all parameters and return values.
* **Class Attributes**: Class attributes must declare type hints at the class level.

---

## 3. Dependency Injection & Modular Design

AI-generated modules must follow modular design principles:
* **Constructor Injection**: Services must receive their dependencies via constructor parameters. Direct instantiations of other services inside classes are prohibited.
* **Interface Decoupling**: Classes must depend on abstract service interfaces (defined under `aios.services`), rather than concrete implementations.
* **Single Responsibility Principle (SRP)**: Each class or file must have a single responsibility. Avoid creating "manager" classes that handle multiple domains.

---

## 4. Redundancy Avoidance

AI agents must avoid duplicate implementations:
* **Standard Libraries**: Prioritize Python's standard library modules (e.g., `pathlib` for paths, `shlex` for command splitting) over custom string processing.
* **Reuse Existing Code**: Check existing utilities before writing helper functions. Reusing verified components is preferred over writing new implementations.

---

*Engineering Bible AI Development Standards · Personal AI OS · Sprint 8 M6 · Governed by [04_AI_MODEL_STRATEGY.md](file:///Users/anzarakhtar/aios/docs/04_AI_MODEL_STRATEGY.md)*
