# Error Handling
**Engineering Bible — Coding Standards — Document 6 of 7**
**Version 1.0** · *Classified: For One Person Only* · *July 2026*

---

## Document Metadata

* **Purpose**: Define the authoritative rules for exception design, error propagation, failure-path typing, user-facing error messages, and timeout enforcement across all Python code in the Personal AI OS monorepo. Silent failures violate the *Trust Through Transparency* foundational belief — this document prevents them.
* **Scope**: All `.py` files in `core/src/`, `core/tests/`, and `skills/`.
* **Audience**: Software Engineers, AI coding agents, and Code Reviewers.
* **Related Documents**:
  * [python_standards.md](python_standards.md) — Syntax context for exception clause formatting (companion document).
  * [logging_standards.md](logging_standards.md) — Where to log errors (companion document).
  * [engineering_ethics.md](../engineering_ethics.md) — Honesty obligation that motivates explicit error propagation.
  * [philosophy.md §2.3](../philosophy.md) — *Trust Through Transparency* belief this document operationalises.
  * [05_SECURITY_GUIDELINES.md](file:///Users/anzarakhtar/aios/docs/05_SECURITY_GUIDELINES.md) — Security implications of error handling (path traversal, injection).
  * [08_CODING_STANDARDS.md §3](file:///Users/anzarakhtar/aios/docs/08_CODING_STANDARDS.md) — Summary-level error handling rules; this document is the expansion.
* **Stability**: High.

---

> [!IMPORTANT]
> **Silence is not safety.** A swallowed exception is a hidden failure. Every error path in this system must be explicitly handled, logged, and either reported to the user or returned as a typed failure. The bare `except:` clause is a **blocking defect**.

---

## 1. Exception Design

### 1.1 Exception Hierarchy

The project maintains a **domain exception hierarchy** rooted at `AiosError`. All project-specific exceptions inherit from domain-specific base classes.

```
AiosError (base)
├── ServiceError
│   ├── MemoryServiceError
│   ├── ModelServiceError
│   └── EventBusError
├── ProviderError
│   ├── ProviderTimeoutError
│   ├── ProviderAuthError
│   └── ProviderRateLimitError
├── SkillError
│   ├── SkillLoadError
│   └── SkillExecutionError
├── SecurityError
│   ├── PathTraversalError
│   └── CommandInjectionError
└── ConfigurationError
```

**Rule**: Custom exceptions must inherit from the appropriate domain base class — never directly from `Exception` or `BaseException` unless adding a new domain root (requires ADR).

### 1.2 Exception Class Definition

```python
class MemoryServiceError(ServiceError):
    """Raised when the memory service cannot complete an operation.

    Attributes:
        operation: The operation that failed (e.g., 'store', 'retrieve').
        key: The memory key involved, if applicable.
    """

    def __init__(
        self,
        message: str,
        operation: str = "",
        key: str = "",
    ) -> None:
        super().__init__(message)
        self.operation = operation
        self.key = key
```

**Rules for exception classes:**
* Name must end in `Error`.
* Must carry a docstring explaining when it is raised.
* May carry structured attributes for programmatic handling.
* Must not contain business logic — exceptions are data carriers, not handlers.

### 1.3 When to Define a Custom Exception

Define a custom exception when:
- The caller needs to catch this error type specifically (distinct from other errors).
- The error carries structured data beyond a message string.
- The error represents a domain concept, not a generic Python failure.

Use built-in exceptions when:
- The error maps cleanly to a Python built-in: `ValueError`, `TypeError`, `FileNotFoundError`, `KeyError`.
- The built-in exception is unambiguous in the context where it is raised.

```python
# ✅ Use ValueError for invalid argument values
def set_tier(self, tier: int) -> None:
    if tier not in (0, 1, 2):
        raise ValueError(f"Invalid tier: {tier!r}. Must be 0, 1, or 2.")

# ✅ Use custom exception for domain failures
def store_entry(self, entry: MemoryEntry) -> bool:
    try:
        self._db.execute(INSERT_SQL, entry.to_row())
    except sqlite3.OperationalError as err:
        raise MemoryServiceError(
            f"Cannot store entry: {err}",
            operation="store",
            key=entry.key,
        ) from err
```

---

## 2. Catching Exceptions

### 2.1 Never Use Bare `except:`

The bare `except:` clause catches **everything**, including `KeyboardInterrupt`, `SystemExit`, and `GeneratorExit`. It is unconditionally banned.

```python
# ❌ BANNED — catches KeyboardInterrupt and SystemExit
try:
    process()
except:
    pass

# ❌ BANNED — still too broad; swallows all errors
try:
    process()
except Exception:
    pass

# ✅ Correct — catch the specific exception you expect
try:
    process()
except MemoryServiceError as err:
    logger.error("Memory operation failed: %s", err)
    return False
```

### 2.2 Catch the Most Specific Exception

Always catch the narrowest exception type that covers the expected failure:

```python
# ✅ Specific
try:
    value = config[key]
except KeyError:
    return default_value

# ❌ Too broad
try:
    value = config[key]
except Exception:
    return default_value
```

When multiple specific exceptions must be handled the same way, use a tuple:

```python
try:
    response = await provider.complete(prompt)
except (ProviderTimeoutError, ProviderRateLimitError) as err:
    logger.warning("Provider unavailable: %s", err)
    return fallback_response()
```

### 2.3 Never Swallow Exceptions Silently

Every `except` block must do at least one of:
1. **Log the error** at an appropriate level (see [logging_standards.md](logging_standards.md)).
2. **Re-raise** the original or a wrapping exception.
3. **Return a typed failure** value that the caller can inspect.

```python
# ❌ Silent swallow — this hides bugs
try:
    entry = self._find_entry(key)
except MemoryServiceError:
    pass

# ✅ Option 1: Log and return failure value
try:
    entry = self._find_entry(key)
except MemoryServiceError as err:
    logger.error("Failed to find entry %r: %s", key, err)
    return None

# ✅ Option 2: Re-raise with context
try:
    entry = self._find_entry(key)
except MemoryServiceError as err:
    raise MemoryServiceError(
        f"Cannot resolve context for key {key!r}",
        operation="find",
        key=key,
    ) from err
```

### 2.4 Exception Chaining (`from err`)

When re-raising or wrapping an exception, always use `raise NewError(...) from original_err`. This preserves the full traceback chain.

```python
# ✅ Chain preserved
try:
    self._db.execute(sql)
except sqlite3.OperationalError as err:
    raise MemoryServiceError("Database write failed") from err

# ❌ Chain lost — original traceback is hidden
try:
    self._db.execute(sql)
except sqlite3.OperationalError:
    raise MemoryServiceError("Database write failed")
```

---

## 3. Failure-Path Typing

### 3.1 Return Type Patterns for Expected Failures

When a function may legitimately not produce a result (not a bug — a valid empty state), use `T | None`:

```python
def find_entry(self, key: str) -> MemoryEntry | None:
    """Return the entry or None if the key is absent."""
    ...
```

When a function may fail and the caller needs to distinguish success from failure:

```python
from dataclasses import dataclass

@dataclass
class OperationResult:
    success: bool
    value: str = ""
    error: str = ""

def store_entry(self, entry: MemoryEntry) -> OperationResult:
    ...
```

### 3.2 Never Use Exception for Control Flow

Exceptions signal unexpected, abnormal conditions — not expected branching:

```python
# ❌ Exception for expected branching
def get_user_preference(key: str) -> str:
    try:
        return self._prefs[key]
    except KeyError:
        return DEFAULT_PREFS[key]   # This is normal — use .get() instead

# ✅ Use dict.get() for expected absence
def get_user_preference(key: str) -> str:
    return self._prefs.get(key, DEFAULT_PREFS[key])
```

### 3.3 `assert` in Production Code

`assert` statements are disabled when Python runs with `-O` (optimise flag). They must not be used for runtime validation in production paths.

```python
# ❌ Disabled in production
assert tier in (0, 1, 2), "Invalid tier"

# ✅ Raises in all execution modes
if tier not in (0, 1, 2):
    raise ValueError(f"Invalid tier: {tier!r}")
```

`assert` is acceptable **in test code only**, where it is the pytest assertion mechanism.

---

## 4. Timeout Enforcement

Every I/O operation — network, database, file, subprocess — must carry an explicit timeout. Hanging operations violate the **Fast** Guiding Principle.

### 4.1 Required Timeout Locations

| I/O Type | How to Set Timeout |
|----------|-------------------|
| HTTP / provider API calls | `httpx.AsyncClient(timeout=30.0)` or per-request `timeout=` parameter |
| `asyncio` coroutines | `asyncio.wait_for(coro, timeout=30.0)` |
| SQLite operations | `sqlite3.connect(path, timeout=5.0)` |
| Subprocess calls | `subprocess.run([...], timeout=10, shell=False)` |
| Redis operations | `redis.Redis(socket_timeout=5.0)` |

### 4.2 Timeout Constants

Timeouts must be named constants, never inline magic numbers:

```python
# At module level
DB_CONNECT_TIMEOUT_SECONDS: float = 5.0
PROVIDER_API_TIMEOUT_SECONDS: float = 30.0
SUBPROCESS_TIMEOUT_SECONDS: float = 10.0

# In usage
conn = sqlite3.connect(db_path, timeout=DB_CONNECT_TIMEOUT_SECONDS)
result = subprocess.run(cmd, timeout=SUBPROCESS_TIMEOUT_SECONDS, shell=False)
```

### 4.3 Timeout Exception Handling

```python
try:
    result = await asyncio.wait_for(
        provider.complete(prompt),
        timeout=PROVIDER_API_TIMEOUT_SECONDS,
    )
except asyncio.TimeoutError:
    logger.warning(
        "Provider %r timed out after %.1fs",
        provider.name,
        PROVIDER_API_TIMEOUT_SECONDS,
    )
    raise ProviderTimeoutError(
        f"Provider {provider.name!r} did not respond within "
        f"{PROVIDER_API_TIMEOUT_SECONDS}s"
    )
```

---

## 5. User-Facing Error Messages

### 5.1 Separation of Concerns

| Audience | Content | Location |
|----------|---------|----------|
| User (CLI output) | Short, action-oriented message without stack trace | `cli.py` display layer |
| Log file | Full context: operation, parameters, exception chain | `logging` call in service layer |

```python
# ✅ Service layer — log full context
def store_entry(self, entry: MemoryEntry) -> bool:
    try:
        ...
    except sqlite3.OperationalError as err:
        logger.error(
            "store_entry failed for key=%r tier=%d: %s",
            entry.key, entry.tier, err,
            exc_info=True,
        )
        raise MemoryServiceError("Cannot store entry") from err

# ✅ CLI layer — user-friendly message only
try:
    memory_service.store_entry(entry)
except MemoryServiceError:
    print("⚠  Memory storage unavailable. Entry was not saved.")
    # Stack trace is in the log, not the terminal
```

### 5.2 User Message Guidelines

* **Be specific about what failed**, not why (internal details are not user concerns).
* **Suggest a recovery action** where possible: "Check your network connection", "Run `aios memory repair`".
* **Never expose**: stack traces, file paths, internal variable values, SQL queries.
* **Use consistent prefix symbols**: `⚠` for warnings, `✗` for errors, `✓` for success.

```python
# ✅ User-facing message
"⚠  Provider 'openai' is unavailable. Switching to local model."
"✗  Cannot read config file. Run: aios config init"

# ❌ Internal details exposed to user
"sqlite3.OperationalError: database is locked at /Users/anzarakhtar/aios/..."
"KeyError: 'max_context_tokens' in config dict"
```

---

## 6. Context Managers and Resource Cleanup

All resources that require cleanup (database connections, file handles, network sockets) must be managed with context managers.

### 6.1 Use `with` for All Resources

```python
# ✅ Context manager — cleanup guaranteed even on exception
with sqlite3.connect(db_path, timeout=DB_CONNECT_TIMEOUT_SECONDS) as conn:
    conn.execute(sql, params)

# ❌ Manual cleanup — skipped if exception is raised
conn = sqlite3.connect(db_path)
conn.execute(sql, params)
conn.close()  # never reached if execute() raises
```

### 6.2 `contextlib.suppress` — Restricted Use

`contextlib.suppress` may only be used for genuinely ignorable exceptions where no logging is needed. It must carry a comment explaining why the error is safe to suppress.

```python
from contextlib import suppress

# ✅ Acceptable — file may not exist on first run; this is expected
with suppress(FileNotFoundError):
    old_cache_path.unlink()  # cleanup; absence is not an error
```

Never use `suppress` for `Exception` or for errors that indicate a logic bug.

---

## 7. Error Handling Checklist

Before committing any Python change, verify:

- [ ] No bare `except:` or `except Exception: pass` clauses
- [ ] Every caught exception is logged, re-raised, or returned as a typed failure
- [ ] All exception re-raises use `raise NewError(...) from original_err`
- [ ] All custom exceptions inherit from the domain hierarchy (not `Exception` directly)
- [ ] All I/O operations carry explicit timeouts using named constants
- [ ] User-facing messages contain no internal implementation details
- [ ] No `assert` used for runtime validation in production code
- [ ] All resources use context managers (`with` blocks)

---

*Engineering Bible Coding Standards · Personal AI OS · Sprint 8 M2 · Governed by [engineering_principles.md](../engineering_principles.md)*
