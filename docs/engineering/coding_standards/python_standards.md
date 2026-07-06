# Python Standards
**Engineering Bible — Coding Standards — Document 1 of 7**
**Version 1.0** · *Classified: For One Person Only* · *July 2026*

---

## Document Metadata

* **Purpose**: Define the authoritative Python syntax, formatting, type-annotation, docstring, and complexity rules for all source files in the Personal AI OS monorepo. Every rule in this document is machine-checkable and enforced by Ruff on every commit.
* **Scope**: All `.py` files under `core/src/`, `core/tests/`, and `skills/`. Configuration files (`pyproject.toml`, `*.toml`) follow their own schema conventions.
* **Audience**: Software Engineers, AI coding agents, and Code Reviewers.
* **Related Documents**:
  * [engineering_principles.md](../engineering_principles.md) — Five operational laws that motivate these standards.
  * [naming_conventions.md](naming_conventions.md) — Identifier naming rules (companion document).
  * [error_handling.md](error_handling.md) — Exception and failure-path rules (companion document).
  * [logging_standards.md](logging_standards.md) — Structured logging rules (companion document).
  * [08_CODING_STANDARDS.md](file:///Users/anzarakhtar/aios/docs/08_CODING_STANDARDS.md) — Summary reference; this document is the authoritative expansion.
  * [01_ENGINEERING_GUIDELINES.md](file:///Users/anzarakhtar/aios/docs/01_ENGINEERING_GUIDELINES.md) — SDLC gates and Definition of Done.
  * [06_TESTING_GUIDELINES.md](file:///Users/anzarakhtar/aios/docs/06_TESTING_GUIDELINES.md) — Test code follows these same standards.
* **Stability**: High. Changes require a `docs:` commit; significant relaxations require an ADR in [10_DECISION_LOG.md](file:///Users/anzarakhtar/aios/docs/10_DECISION_LOG.md).

---

> [!IMPORTANT]
> These are **hard constraints**, not style suggestions. Any pull request or AI-generated change that violates them must be rejected and corrected before merge.

---

## 1. Language Version & Runtime Target

| Property | Value |
|----------|-------|
| Python version | **3.12** (minimum, enforced in `pyproject.toml`) |
| Ruff target | `py312` |
| Async style | `asyncio` only — no third-party event loops (`trio`, `uvloop`) without an ADR |
| Type system | `typing` stdlib + PEP 695 type aliases where appropriate |

```toml
# pyproject.toml (canonical configuration)
[project]
requires-python = ">=3.12"

[tool.ruff]
target-version = "py312"
line-length = 100
```

---

## 2. Formatting Rules

All formatting is enforced by **`ruff format`**. Manual formatting is prohibited — the formatter is the single source of truth.

### 2.1 Line Length

* **Maximum**: 100 characters per line.
* **Exception**: Docstrings may wrap at 100 characters; URLs inside docstrings are never broken.
* Comments must also fit within 100 characters. Restructure the sentence rather than exceed the limit.

### 2.2 Indentation

* **4 spaces** — never tabs.
* Continuation lines use 4-space hanging indents or aligned-to-opening-delimiter, whichever `ruff format` produces.

### 2.3 Quotes

* **Double quotes** for all strings (`quote-style = "double"` in `pyproject.toml`).
* F-strings follow the same double-quote rule; nested quotes inside the expression use single quotes.
* Raw strings (`r"..."`) and byte strings (`b"..."`) also use double quotes.

```python
# ✅ Correct
message = "Operation completed"
path = f"File {file_name!r} not found"

# ❌ Incorrect
message = 'Operation completed'
```

### 2.4 Blank Lines

| Location | Rule |
|----------|------|
| Between top-level definitions (class, function) | 2 blank lines |
| Between methods inside a class | 1 blank line |
| After class body open / before first method | 0 blank lines |
| At the end of a file | 1 newline character (no trailing blank lines) |

### 2.5 Trailing Whitespace & EOF

* No trailing whitespace on any line.
* Every file ends with exactly one `\n`.
* Enforced by `ruff format` and `.gitattributes` `text=auto`.

---

## 3. Type Annotations

All public functions, methods, and module-level variables **must** carry complete type annotations. Private helpers are strongly encouraged.

### 3.1 Required Annotation Locations

```python
# ✅ Public function — all parameters + return type annotated
def resolve_provider(model_id: str, offline: bool = False) -> str:
    ...

# ✅ Class attribute declared in __init__
class MemoryEntry:
    def __init__(self, content: str, tier: int) -> None:
        self.content: str = content
        self.tier: int = tier
```

### 3.2 Prohibited Patterns

```python
# ❌ Any — banned except in adapter shims with an explicit comment justifying it
def process(data: Any) -> Any: ...

# ❌ Missing return type
def get_name(self):
    return self._name

# ❌ Using `list`, `dict`, `tuple` without subscript in Python 3.9+ style
def items() -> list:   # wrong — use list[str] or List[str]
    ...
```

### 3.3 Optional & Union

* Use `X | Y` (PEP 604) union syntax in Python 3.10+ style — not `Union[X, Y]`.
* Use `X | None` instead of `Optional[X]`.

```python
# ✅
def find_entry(key: str) -> MemoryEntry | None: ...

# ❌
def find_entry(key: str) -> Optional[MemoryEntry]: ...
```

### 3.4 TypedDict & Dataclasses

* Prefer `dataclasses.dataclass` for structured data objects over raw `dict`.
* Use `TypedDict` only for external API payloads where the shape is dictated by a third party.
* All dataclass fields must have type annotations and default values where sensible.

```python
from dataclasses import dataclass, field

@dataclass
class ProviderMetrics:
    success_rate: float = 1.0
    avg_latency_ms: float = 0.0
    error_count: int = 0
    tags: list[str] = field(default_factory=list)
```

---

## 4. Docstrings

All public modules, classes, and functions require **Google-style docstrings**. Private functions (`_name`) are encouraged but not mandatory.

### 4.1 Module Docstring

```python
"""Memory service interface contract.

This module defines the abstract MemoryService protocol and the MemoryEntry
dataclass. Concrete implementations must not be imported here.

Related:
    docs/02_ARCHITECTURE_GUIDELINES.md — service contract rules.
"""
```

### 4.2 Class Docstring

```python
class LocalMemoryService:
    """SQLite-backed implementation of the MemoryService protocol.

    Stores memory entries in three tiers: permanent, long-lived, and
    short-lived. Short-lived entries are pruned at system shutdown.

    Attributes:
        db_path: Absolute path to the SQLite database file.
        max_short_lived_days: Retention window for short-lived entries.
    """
```

### 4.3 Function Docstring

```python
def store_entry(self, entry: MemoryEntry) -> bool:
    """Persist a memory entry to the appropriate tier table.

    Args:
        entry: The MemoryEntry to persist. The tier field determines
            which table receives the insert.

    Returns:
        True if the write succeeded; False if the database rejected it.

    Raises:
        MemoryServiceError: If the database connection is unavailable.
    """
```

### 4.4 One-Line Docstrings

For trivially simple functions a one-liner is acceptable:

```python
def is_expired(entry: MemoryEntry) -> bool:
    """Return True if the entry's TTL has elapsed."""
    ...
```

---

## 5. Complexity & Size Budgets

These limits are enforced by Ruff lint rules and reviewed at PR time.

| Metric | Limit | Enforcement |
|--------|-------|-------------|
| File length | **400 lines** | PR review gate |
| Function cyclomatic complexity | **10** | `ruff check` (rule C901) |
| Function length | **50 lines** | PR review gate |
| Parameters per function | **4** | `ruff check` (rule PLR0913); use a dataclass beyond 4 |
| Class public methods | **12** | PR review gate; split into sub-services if exceeded |
| Nesting depth | **4 levels** | PR review gate |

### 5.1 File Split Trigger

When a file approaches 350 lines, the contributor must plan the split *before* it crosses 400. Acceptable splits:

1. Extract a helper into `_internal/` within the same package.
2. Promote a concept into its own module with a defined public boundary.
3. Extract a shared utility into `core/src/aios/utils/`.

### 5.2 Dead Code Policy

* Commented-out code (`# old_function()`) must be deleted, not left in place.
* Code that cannot be reached (`if False:`, unreachable branches after `return`) must be deleted immediately.
* `# TODO` comments must reference a sprint milestone (`# TODO Sprint 9 M2`) or be deleted within the same session.

---

## 6. Ruff Configuration Reference

The canonical Ruff configuration lives in `pyproject.toml` at the monorepo root.

```toml
[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "F",   # pyflakes
    "B",   # flake8-bugbear
    "I",   # isort
    "N",   # pep8-naming
]
ignore = []

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

### 6.1 Running Ruff

```bash
# Format all source files
ruff format core/src/ core/tests/ skills/

# Lint and auto-fix safe issues
ruff check --fix core/src/ core/tests/ skills/

# CI-safe check (no mutations, exit 1 on violations)
ruff format --check core/src/ && ruff check core/src/
```

### 6.2 Adding New Lint Rules

Any addition to `[tool.ruff.lint] select` requires:
1. All existing violations corrected in the same commit.
2. A note in [10_DECISION_LOG.md](file:///Users/anzarakhtar/aios/docs/10_DECISION_LOG.md) if the rule affects more than 10 files.

---

## 7. Python Anti-Patterns — Banned List

The following patterns are unconditionally prohibited. Ruff catches most of them; reviewers catch the rest.

| Pattern | Reason | Alternative |
|---------|--------|-------------|
| `except:` bare clause | Silences all errors including `KeyboardInterrupt` | `except SpecificError:` |
| `except Exception as e: pass` | Swallows errors silently | Log and re-raise or return an error result |
| `global variable` mutation | Creates hidden state coupling | Pass state explicitly via parameters |
| `eval()` / `exec()` | Arbitrary code execution risk | Use `ast.literal_eval` for data; parse explicitly for logic |
| `import *` wildcard | Pollutes namespace, breaks static analysis | Explicit named imports |
| Mutable default arguments | Shared state across calls | `field(default_factory=list)` or `= None` with guard |
| `print()` for diagnostics | Bypasses log routing | `logging.getLogger(__name__)` — see [logging_standards.md](logging_standards.md) |
| Bare `assert` in production code | Disabled by `-O` flag | Raise explicit exceptions |
| `time.sleep()` in async context | Blocks the event loop | `await asyncio.sleep()` |
| Nested function definitions > 2 levels | Obscures call paths | Extract to module-level or class methods |

---

## 8. Encoding & File Headers

* All Python files use **UTF-8** encoding. No encoding declaration (`# -*- coding: utf-8 -*-`) is needed for Python 3.
* No shebang lines (`#!/usr/bin/env python`) except for top-level CLI entry scripts.
* No auto-generated file banners (timestamps, author names) — version control provides authorship history.

---

## 9. Compliance Checklist

Before committing any Python change, verify:

- [ ] `ruff format --check` passes with zero diff
- [ ] `ruff check` returns zero violations
- [ ] All public functions have type annotations and Google-style docstrings
- [ ] No file exceeds 400 lines
- [ ] No function exceeds complexity 10 or 50 lines
- [ ] No parameter list exceeds 4 items (use dataclass if needed)
- [ ] No dead code, commented-out blocks, or bare `except` clauses remain
- [ ] No `print()` statements used for diagnostics

---

*Engineering Bible Coding Standards · Personal AI OS · Sprint 8 M2 · Governed by [engineering_principles.md](../engineering_principles.md)*
