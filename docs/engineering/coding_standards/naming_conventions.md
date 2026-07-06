# Naming Conventions
**Engineering Bible — Coding Standards — Document 2 of 7**
**Version 1.0** · *Classified: For One Person Only* · *July 2026*

---

## Document Metadata

* **Purpose**: Define the canonical naming rules for every identifier in the monorepo — modules, packages, classes, functions, variables, constants, type aliases, and CLI commands — so that any AI agent or human contributor can name any new entity without ambiguity.
* **Scope**: All Python source files (`core/src/`, `core/tests/`, `skills/`), configuration keys, CLI command identifiers, and documentation file names.
* **Audience**: Software Engineers, AI coding agents, and Code Reviewers.
* **Related Documents**:
  * [python_standards.md](python_standards.md) — Syntax and formatting rules (companion document).
  * [project_structure.md](project_structure.md) — File and directory naming rules (companion document).
  * [engineering_principles.md](../engineering_principles.md) — SRP motivates single-concept names.
  * [08_CODING_STANDARDS.md](file:///Users/anzarakhtar/aios/docs/08_CODING_STANDARDS.md) — Summary-level naming rules; this document is the authoritative expansion.
* **Stability**: High. Rename-only refactors must update all references in the same commit.

---

> [!IMPORTANT]
> Names are contracts. A rename that breaks an import, CLI command, or documented interface must include migration of every reference in the same commit.

---

## 1. Case Convention Table

This is the master reference. When in doubt, consult this table first.

| Entity | Convention | Example |
|--------|-----------|---------|
| Package / directory | `snake_case` | `memory_service/`, `skill_manager/` |
| Module / `.py` file | `snake_case` | `local_memory_service.py`, `intent_resolver.py` |
| Class | `PascalCase` | `LocalMemoryService`, `OmniRouteSelector` |
| Exception class | `PascalCase` + `Error` suffix | `MemoryServiceError`, `ProviderTimeoutError` |
| Protocol / ABC | `PascalCase` | `MemoryService`, `ModelProvider` |
| TypedDict | `PascalCase` | `ProviderConfig`, `MemoryEntryDict` |
| Dataclass | `PascalCase` | `MemoryEntry`, `SkillMetadata` |
| Type alias | `PascalCase` | `ProviderName = str`, `TierLevel = int` |
| Public function / method | `snake_case` | `store_entry()`, `resolve_provider()` |
| Private function / method | `_snake_case` | `_build_context()`, `_validate_path()` |
| Dunder method | `__snake_case__` | `__init__()`, `__repr__()` |
| Instance variable | `snake_case` | `self.db_path`, `self.max_retries` |
| Private instance variable | `_snake_case` | `self._connection`, `self._cache` |
| Local variable | `snake_case` | `entry_id`, `response_text` |
| Constant (module-level) | `UPPER_SNAKE_CASE` | `MAX_RETRIES`, `DEFAULT_TIMEOUT_SECONDS` |
| Boolean variable / parameter | `snake_case` with verb prefix | `is_ready`, `has_cache`, `can_write`, `should_retry` |
| CLI command | `kebab-case` | `memory-search`, `skill-list` |
| Config key (TOML) | `snake_case` | `offline_mode`, `max_context_tokens` |
| Environment variable | `UPPER_SNAKE_CASE` | `OPENAI_API_KEY`, `AIOS_WORKSPACE_ROOT` |
| Test function | `test_` prefix + `snake_case` | `test_store_entry_persists_to_db()` |
| Test class | `Test` prefix + `PascalCase` | `TestLocalMemoryService` |
| Fixture | `snake_case` | `memory_service_fixture`, `tmp_db_path` |

---

## 2. Naming Rules by Category

### 2.1 Classes

**Rule 1 — Name the concept, not the implementation.**

```python
# ✅ Names the domain concept
class MemoryService:       # abstract protocol
class LocalMemoryService:  # concrete SQLite implementation

# ❌ Names the technology
class SQLiteMemory:        # leaks implementation detail into the name
```

**Rule 2 — Exception classes carry the `Error` suffix.**

```python
# ✅
class ProviderTimeoutError(RuntimeError): ...
class MemoryServiceError(Exception): ...

# ❌
class ProviderTimeout(RuntimeError): ...  # ambiguous — is this a value or exception?
class BadMemory(Exception): ...           # too vague
```

**Rule 3 — Abstract base classes and protocols use the pure concept name.**

Concrete implementations prefix with the location/technology:

```python
class MemoryService(Protocol):        # abstract
class LocalMemoryService:             # SQLite, local
class RedisMemoryService:             # Redis, distributed (future)
```

### 2.2 Functions & Methods

**Rule 1 — Name functions as verb phrases that describe their effect.**

```python
# ✅ Verb + subject pattern
def store_entry(entry: MemoryEntry) -> bool: ...
def resolve_provider(model_id: str) -> str: ...
def prune_expired_entries() -> int: ...

# ❌ Noun-only names (describe data, not action)
def entries() -> list[MemoryEntry]: ...
def provider(model_id: str) -> str: ...
```

**Rule 2 — Query functions use `get_`, `find_`, `fetch_`, or `list_` prefixes.**

| Prefix | Meaning | Returns |
|--------|---------|---------|
| `get_` | Retrieve a known, required item | The item or raises if missing |
| `find_` | Search for an optional item | Item or `None` |
| `fetch_` | Load from I/O (network / disk) | Item or raises `IOError` variant |
| `list_` | Return a collection | `list[T]` (never a generator) |

```python
def get_entry(key: str) -> MemoryEntry: ...       # raises MemoryServiceError if missing
def find_entry(key: str) -> MemoryEntry | None: ...  # returns None if absent
def fetch_provider_metrics() -> ProviderMetrics: ...  # network/disk I/O
def list_skills() -> list[SkillMetadata]: ...     # returns full list
```

**Rule 3 — Mutation functions use `create_`, `update_`, `delete_`, `store_`, `clear_` prefixes.**

```python
def create_conversation(title: str) -> ConversationRecord: ...
def update_entry(key: str, content: str) -> bool: ...
def delete_expired_sessions() -> int: ...
```

**Rule 4 — Boolean functions use question-form verb prefixes.**

| Prefix | Example |
|--------|---------|
| `is_` | `is_expired()`, `is_connected()` |
| `has_` | `has_cache()`, `has_permission()` |
| `can_` | `can_write()`, `can_connect()` |
| `should_` | `should_retry()`, `should_prune()` |

```python
# ✅
def is_expired(entry: MemoryEntry) -> bool: ...
def can_write(path: Path) -> bool: ...

# ❌
def expired(entry: MemoryEntry) -> bool: ...   # no verb prefix — reads as noun
def writable(path: Path) -> bool: ...          # ambiguous — property or method?
```

**Rule 5 — Private helpers use `_` prefix and are not exported from the module.**

```python
def _validate_tier(tier: int) -> None: ...
def _build_insert_query(entry: MemoryEntry) -> str: ...
```

### 2.3 Variables

**Rule 1 — Names must be self-documenting; abbreviations are forbidden except the canonical allowlist.**

**Canonical abbreviation allowlist:**

| Abbreviation | Stands for | Context |
|-------------|-----------|---------|
| `id` | identifier | Any entity identifier |
| `url` | Uniform Resource Locator | Network addresses |
| `config` | configuration | Configuration objects |
| `db` | database | Database connection/path |
| `ctx` | context | Context container objects |
| `msg` | message | Log messages, error strings |
| `err` | error | Exception variable in `except` blocks |
| `tmp` | temporary | Short-lived intermediate values |

Everything else must be written out fully.

```python
# ✅ Clear, full names
entry_content = entry.content
max_retries = config.get("max_retries")
conversation_id = record.id

# ❌ Opaque abbreviations
ec = entry.content      # what is ec?
mr = config.get("mr")   # undecipherable
cid = record.id         # not in allowlist
```

**Rule 2 — Loop variables follow the same naming rules as any other variable.**

```python
# ✅
for entry in expired_entries:
    delete_entry(entry.key)

# ❌ — meaningless single-letter variable
for e in expired_entries:
    delete(e.key)

# Exception: mathematical or well-understood index patterns
for i, entry in enumerate(entries):   # 'i' as index — acceptable
    ...
```

**Rule 3 — Boolean variables always carry a question-form name.**

```python
# ✅
is_offline = config.offline_mode
has_pending_writes = len(write_queue) > 0

# ❌
offline = config.offline_mode   # reads as noun, not predicate
pending = len(write_queue) > 0  # ambiguous
```

### 2.4 Constants

Module-level constants use `UPPER_SNAKE_CASE` and are declared at the top of the module, after imports.

```python
# ✅ Module-level constant block
MAX_RETRIES: int = 3
DEFAULT_TIMEOUT_SECONDS: float = 30.0
SHORT_LIVED_TTL_DAYS: int = 7
PERMANENT_TIER: int = 0
LONG_LIVED_TIER: int = 1
SHORT_LIVED_TIER: int = 2
```

Constants must be typed. Magic numbers inside functions must be extracted to module-level constants with descriptive names.

```python
# ❌ Magic number
if len(history) > 10:   # what is 10?

# ✅ Named constant
MAX_HISTORY_TURNS: int = 10
if len(history) > MAX_HISTORY_TURNS:
```

### 2.5 Type Aliases

```python
# PascalCase for all type aliases
ProviderName = str
TierLevel = int
ConversationId = str
MemoryKey = str
```

### 2.6 Test Identifiers

Test functions must encode the subject, scenario, and expected outcome:

```
test_{subject}_{scenario}_{expected_outcome}
```

```python
# ✅
def test_store_entry_when_db_unavailable_raises_memory_service_error(): ...
def test_find_entry_when_key_absent_returns_none(): ...
def test_prune_expired_entries_returns_count_of_deleted_rows(): ...

# ❌ — vague or missing context
def test_store(): ...
def test_memory(): ...
def test_it_works(): ...
```

---

## 3. Module & Package Naming

### 3.1 Module Names

* `snake_case`, all lowercase.
* Names describe the module's single responsibility — not its implementation technology.
* No generic names: `utils.py`, `helpers.py`, `common.py`, `misc.py` are **banned**.

| Banned Name | Replacement Strategy |
|-------------|---------------------|
| `utils.py` | `path_utils.py`, `text_formatter.py`, `time_helpers.py` |
| `helpers.py` | Name by the concept the helpers serve |
| `common.py` | Extract to the module that owns the shared logic |
| `base.py` | Name by the abstraction: `memory_service.py`, `model_provider.py` |

### 3.2 Package Names

* `snake_case`, all lowercase, no hyphens.
* Packages must reflect a domain boundary, not a technical tier.

```
# ✅ Domain-driven packages
core/src/aios/
    memory/          # memory domain
    providers/       # model provider domain
    skills/          # skill system domain
    brain/           # reasoning orchestration domain

# ❌ Technical-tier packages
core/src/aios/
    database/        # too broad — what database, for what?
    handlers/        # no domain concept
    managers/        # no domain concept
```

---

## 4. CLI Command & Config Key Naming

### 4.1 CLI Commands

CLI commands use `kebab-case`. They describe an action and subject:

```
{verb}-{subject}
memory-search
skill-list
task-create
provider-status
```

Sub-commands extend the pattern:
```
memory search "keyword"
memory clear --tier short-lived
skill enable github
```

### 4.2 Config Keys (TOML)

All keys in `config/config.toml` use `snake_case`:

```toml
[model]
default_provider = "openai"
offline_mode = false
max_context_tokens = 16000

[memory]
short_lived_ttl_days = 7
max_permanent_entries = 5000
```

### 4.3 Environment Variables

All environment variables use `UPPER_SNAKE_CASE` with an `AIOS_` prefix for project-specific variables:

```bash
# External API keys — no prefix
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Project-specific variables — AIOS_ prefix
AIOS_WORKSPACE_ROOT=/Users/anzarakhtar/aios
AIOS_OFFLINE_MODE=false
AIOS_LOG_LEVEL=INFO
```

---

## 5. Documentation & File Naming

| File type | Convention | Example |
|-----------|-----------|---------|
| Markdown docs in `docs/` | `NN_TITLE_CASE.md` or `kebab-case.md` | `01_ENGINEERING_GUIDELINES.md` |
| Engineering Bible docs | `snake_case.md` | `python_standards.md`, `naming_conventions.md` |
| ADR documents | `NNN-kebab-description.md` | `001-use-sqlite-for-memory.md` |
| Test files | `test_{module_name}.py` | `test_local_memory_service.py` |
| Config files | `snake_case.toml` / `snake_case.json` | `config.toml`, `skill_registry.json` |

---

## 6. Anti-Pattern Reference

| Anti-Pattern | Example | Rule Violated |
|-------------|---------|--------------|
| Single-letter variable | `x`, `n`, `d` (except `i`, `j` for indices) | 2.3 Rule 1 |
| Unprefixed boolean | `offline`, `valid`, `ready` | 2.3 Rule 3 |
| Generic module name | `utils.py`, `helpers.py` | 3.1 |
| Technology-leaking class name | `SQLiteStore`, `RedisCache` | 2.1 Rule 1 |
| Noun-only function name | `entries()`, `provider()` | 2.2 Rule 1 |
| Unapproved abbreviation | `conv_id`, `proc`, `mgr` | 2.3 Rule 1 |
| Magic number literal | `if retries > 3` | 2.4 |
| Vague test name | `test_memory()` | 2.6 |

---

*Engineering Bible Coding Standards · Personal AI OS · Sprint 8 M2 · Governed by [engineering_principles.md](../engineering_principles.md)*
