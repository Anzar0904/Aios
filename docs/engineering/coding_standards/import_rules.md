# Import Rules
**Engineering Bible — Coding Standards — Document 4 of 7**
**Version 1.0** · *Classified: For One Person Only* · *July 2026*

---

## Document Metadata

* **Purpose**: Define the authoritative rules for import ordering, grouping, boundary enforcement, and circular-import prevention in every Python file of the Personal AI OS monorepo. Correct imports are the first line of defence against coupling.
* **Scope**: All `.py` files in `core/src/`, `core/tests/`, and `skills/`.
* **Audience**: Software Engineers, AI coding agents, and Code Reviewers.
* **Related Documents**:
  * [python_standards.md](python_standards.md) — Formatting context for imports (companion document).
  * [project_structure.md](project_structure.md) — Package structure that defines import paths (companion document).
  * [dependency_rules.md](dependency_rules.md) — Rules for what third-party packages may be imported (companion document).
  * [02_ARCHITECTURE_GUIDELINES.md](file:///Users/anzarakhtar/aios/docs/02_ARCHITECTURE_GUIDELINES.md) — Dependency Inversion contracts that these rules enforce.
  * [engineering_principles.md](../engineering_principles.md) — *Optimize for Deletion* and *One Reason to Change* motivate strict import boundaries.
* **Stability**: High. Import boundary violations are blocking defects.

---

> [!IMPORTANT]
> Import boundary violations — concrete classes crossing package boundaries, circular imports, or wildcard imports — are **blocking defects**. They must be corrected before any change is considered done.

---

## 1. Import Order (Ruff `isort` Standard)

All imports must follow this exact four-group order, separated by a single blank line. Ruff's `I` ruleset (`isort`) enforces this automatically.

```
Group 1: __future__ imports (if any)
         ↓ blank line
Group 2: Standard library imports
         ↓ blank line
Group 3: Third-party library imports
         ↓ blank line
Group 4: Local (first-party) imports
```

### 1.1 Canonical Example

```python
from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import TYPE_CHECKING

import httpx
import tomli

from aios.services.memory_service import MemoryService
from aios.services.local_memory_service import LocalMemoryService
from aios.brain.context_builder import ContextBuilder
```

### 1.2 Within Each Group

Within each group, imports are sorted **alphabetically** by module name. Ruff handles this automatically.

```python
# ✅ Alphabetical within standard library group
import asyncio
import json
import logging
import os
from pathlib import Path
from typing import TYPE_CHECKING

# ❌ Random order — Ruff will flag and auto-fix
import logging
import asyncio
from typing import TYPE_CHECKING
import os
```

### 1.3 `from` vs `import` Ordering

Within the same group, `import X` lines come before `from X import Y` lines (Ruff default):

```python
import asyncio
import json
from pathlib import Path
from typing import TYPE_CHECKING
```

---

## 2. Import Style Rules

### 2.1 Explicit Named Imports Only

Wildcard imports (`from module import *`) are **unconditionally banned** in all production and test code.

```python
# ❌ Banned
from aios.services import *
from typing import *

# ✅ Correct — explicit named imports
from aios.services.memory_service import MemoryService, MemoryEntry
from typing import TYPE_CHECKING
```

**Rationale**: Wildcard imports make static analysis impossible, pollute the local namespace, and prevent tools like Ruff and mypy from detecting unused or missing names.

### 2.2 Alias Rules

Import aliases are permitted only in two situations:

1. **Avoiding a collision** between two modules with the same leaf name.
2. **Shortening a conventionally aliased library** (`numpy as np`, `pandas as pd` — but these libraries are not used here).

```python
# ✅ Acceptable alias to avoid collision
from aios.services.memory_service import MemoryEntry as MemoryServiceEntry
from aios.brain.memory_entry import MemoryEntry as BrainMemoryEntry

# ❌ Cosmetic aliases that obscure the origin
from aios.services.memory_service import MemoryService as MS   # MS is opaque
import asyncio as aio                                          # no collision, no convention
```

### 2.3 Inline Imports

Inline (inside-function) imports are prohibited in production code except to break a genuine circular import that cannot be resolved by restructuring.

```python
# ❌ Inline import — hides a dependency
def get_provider():
    from aios.providers.openai_provider import OpenAIProvider  # hidden dep
    return OpenAIProvider()

# ✅ Top-level import
from aios.providers.openai_provider import OpenAIProvider

def get_provider() -> OpenAIProvider:
    return OpenAIProvider()
```

When an inline import is truly unavoidable (circular import), it must carry a comment explaining why:

```python
def _resolve_late():
    # Inline import: circular dependency between brain.orchestrator and
    # services.memory_service. Refactor tracked in Sprint 9 M1.
    from aios.brain.orchestrator import OrchestratorBrain
    ...
```

### 2.4 `TYPE_CHECKING` Guard

When a type annotation creates a circular import at runtime, use the `TYPE_CHECKING` guard:

```python
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aios.brain.orchestrator import OrchestratorBrain

def configure(brain: "OrchestratorBrain") -> None:
    ...
```

The `from __future__ import annotations` at the top makes all annotations strings at runtime, so the guard import is never executed.

---

## 3. Package Boundary Rules

This section defines which modules may import from which other modules. It directly enforces the **Dependency Inversion Principle** from [02_ARCHITECTURE_GUIDELINES.md](file:///Users/anzarakhtar/aios/docs/02_ARCHITECTURE_GUIDELINES.md).

### 3.1 Dependency Direction

```
Allowed import directions (→ = "may import from"):

cli.py               → kernel.py, brain/, services/ (protocols only)
kernel.py            → registry.py, services/ (protocols only), brain/
brain/               → services/ (protocols only), providers/ (protocols only)
services/ (concrete) → stdlib, third-party only
providers/ (concrete) → stdlib, third-party only
skills/              → services/ (protocols only, via registry injection)
tests/               → any module in core/src/aios/ (for testing purposes)
```

### 3.2 Prohibited Import Directions

| From | May NOT import | Reason |
|------|----------------|--------|
| `services/` concrete impls | Other concrete services | Creates tight coupling |
| `providers/` concrete adapters | `brain/` or `services/` | Provider adapters are leaves |
| `skills/{skill}` | `core/src/aios/` internal modules | Skills use service injection |
| Any module | `bootstrap.py` | Bootstrap is the composition root, not a library |
| Any module | `cli.py` internals | CLI layer is a terminal — never imported |

### 3.3 Concrete vs Abstract Import Rule

**Always import the abstract protocol, never the concrete class, from orchestrating modules:**

```python
# ✅ Kernel imports the protocol
from aios.services.memory_service import MemoryService   # abstract

# ❌ Kernel imports the concrete class — violates DIP
from aios.services.local_memory_service import LocalMemoryService
```

The concrete class is only referenced in `bootstrap.py` (the Composition Root), where all dependencies are wired.

### 3.4 Cross-Skill Imports

Skills must never import from another skill's package:

```python
# ❌ github skill importing from research skill
# skills/github/github_service.py
from skills.research.research_service import ResearchService   # BANNED

# ✅ Both skills receive shared services via injection
# skills/github/commands.py
class GitHubCommands:
    def __init__(self, registry: ServiceRegistry) -> None:
        self._memory = registry.get(MemoryService)
```

---

## 4. `__init__.py` Export Rules

### 4.1 What to Export

Each package's `__init__.py` defines the **public API** of that package. Only symbols that form the intentional public boundary should be exported.

```python
# core/src/aios/services/__init__.py
# Export only the abstract protocols — never the concrete implementations

from aios.services.memory_service import MemoryEntry, MemoryService
from aios.services.model_service import ModelService
from aios.services.event_bus_service import EventBusService

__all__ = [
    "MemoryEntry",
    "MemoryService",
    "ModelService",
    "EventBusService",
]
```

### 4.2 `__all__` Requirement

Every `__init__.py` that exports symbols **must** define `__all__`. This makes the public API explicit and allows wildcard-import linting tools to work correctly even if the ban in §2.1 is violated by mistake.

### 4.3 Empty `__init__.py`

An `__init__.py` may be empty if the package is only used as a namespace. Never add `import` statements to an empty `__init__.py` "just in case" — add them when there is a concrete consumer.

---

## 5. Circular Import Prevention

Circular imports indicate a design flaw. The resolution strategy, in order of preference:

| Step | Resolution | Example |
|------|-----------|---------|
| 1 | Extract the shared type to a third module | Move `MemoryEntry` to `memory_types.py` |
| 2 | Use `TYPE_CHECKING` guard for annotation-only imports | See §2.4 |
| 3 | Invert the dependency (introduce a protocol) | `brain/` depends on `MemoryService` not `LocalMemoryService` |
| 4 | Inline import as last resort | Documented with a refactor ticket |

Circular imports that cannot be resolved without an inline import **must** have a tracking comment referencing the sprint milestone that will fix the structural issue.

---

## 6. Ruff Enforcement

The `I` (isort) and `F` (pyflakes) rule groups enforce import compliance:

| Ruff Rule | What It Catches |
|-----------|----------------|
| `I001` | Import block is unsorted or wrongly grouped |
| `F401` | Module imported but unused |
| `F811` | Redefinition of an unused name from import |
| `F403` | `import *` wildcard used |
| `F405` | Name may be from a wildcard import |
| `E401` | Multiple imports on one line |

```bash
# Check import compliance
ruff check --select I,F401,F403,F811 core/src/ core/tests/ skills/

# Auto-fix safe import ordering issues
ruff check --fix --select I core/src/
```

---

## 7. Import Compliance Checklist

Before committing any Python change, verify:

- [ ] Imports are in the correct four-group order (stdlib → third-party → local)
- [ ] No wildcard imports (`from X import *`)
- [ ] No inline imports (except documented circular-import breaks)
- [ ] Orchestrating modules import protocols, not concrete classes
- [ ] No skill imports from another skill's package
- [ ] `__init__.py` exports are explicitly listed in `__all__`
- [ ] No unused imports (`ruff check F401` is clean)
- [ ] No circular imports (running the module does not raise `ImportError`)

---

*Engineering Bible Coding Standards · Personal AI OS · Sprint 8 M2 · Governed by [engineering_principles.md](../engineering_principles.md)*
