# Logging Standards
**Engineering Bible — Coding Standards — Document 7 of 7**
**Version 1.0** · *Classified: For One Person Only* · *July 2026*

---

## Document Metadata

* **Purpose**: Define the authoritative rules for logger acquisition, log level usage, message formatting, structured context, sensitive data redaction, and log file management across the entire Personal AI OS monorepo. Logs are the primary observability instrument for a local-first, single-user system.
* **Scope**: All `.py` files in `core/src/`, `core/tests/`, and `skills/`.
* **Audience**: Software Engineers, AI coding agents, and Systems Operators.
* **Related Documents**:
  * [error_handling.md](error_handling.md) — Where errors are caught and when to log them (companion document).
  * [python_standards.md](python_standards.md) — Formatting context (companion document).
  * [philosophy.md §2.3](../philosophy.md) — *Trust Through Transparency* motivates structured, honest logging.
  * [engineering_ethics.md §3](../engineering_ethics.md) — Privacy obligations that govern what must never be logged.
  * [05_SECURITY_GUIDELINES.md §4](file:///Users/anzarakhtar/aios/docs/05_SECURITY_GUIDELINES.md) — Security constraints on log content.
  * [20_OPERATIONS_MANUAL.md](file:///Users/anzarakhtar/aios/docs/20_OPERATIONS_MANUAL.md) — Log file locations and rotation procedures.
* **Stability**: High.

---

> [!IMPORTANT]
> **`print()` is banned as a diagnostic tool.** Any `print()` call used for debugging or operational status output in `core/src/aios/` is a **blocking defect**. Use `logging.getLogger(__name__)` exclusively.

---

## 1. Logger Acquisition

### 1.1 Canonical Pattern

Every module that needs logging acquires a logger using `__name__` as the logger name. This creates a logger hierarchy that mirrors the package structure.

```python
import logging

logger = logging.getLogger(__name__)
```

**Rules:**
* Declare the logger at **module level** — one logger per module.
* Never pass a string literal other than `__name__` as the logger name.
* Never use the root logger (`logging.getLogger()` with no argument) in application code.
* Never use `logging.basicConfig()` inside library modules — only in `bootstrap.py`.

```python
# ✅ Correct — module-level, uses __name__
# core/src/aios/services/local_memory_service.py
import logging

logger = logging.getLogger(__name__)
# Effective name: "aios.services.local_memory_service"

class LocalMemoryService:
    def store_entry(self, entry: MemoryEntry) -> bool:
        logger.debug("Storing entry key=%r tier=%d", entry.key, entry.tier)
        ...

# ❌ Banned — hardcoded name breaks hierarchy
logger = logging.getLogger("memory")

# ❌ Banned — root logger pollutes all libraries
logger = logging.getLogger()

# ❌ Banned — diagnostic print
print(f"Storing entry {entry.key}")
```

### 1.2 Logger Hierarchy

The `__name__`-based hierarchy allows fine-grained control from `config.toml`:

```
aios                                    ← root application logger
aios.services                           ← all service modules
aios.services.local_memory_service      ← specific module
aios.brain                              ← all brain modules
aios.brain.orchestrator                 ← specific module
aios.providers.openai_provider          ← specific provider
```

This means `logging.getLogger("aios.services").setLevel(logging.DEBUG)` enables debug output for all service modules without touching other packages.

---

## 2. Log Levels

### 2.1 Level Definitions

| Level | Use When | Example |
|-------|---------|---------|
| `DEBUG` | Fine-grained diagnostic information useful during development; verbose but safe to enable | `"Fetched %d entries from tier=%d"` |
| `INFO` | Significant lifecycle events the operator wants to see in normal operation | `"MemoryService initialised, db=%r"` |
| `WARNING` | Unexpected situation that did not prevent the operation; the system compensated | `"Provider 'openai' rate-limited; retrying in %.1fs"` |
| `ERROR` | Operation failed; the system could not recover automatically | `"Failed to store entry key=%r: %s"` |
| `CRITICAL` | System cannot continue; manual intervention required | `"Database file corrupted; shutting down"` |

### 2.2 Level Selection Rules

```python
# ✅ DEBUG — internal state, counts, resolved values
logger.debug("Context assembled: tokens=%d entries=%d", total_tokens, entry_count)
logger.debug("OmniRoute selected provider=%r latency_ms=%.1f", name, latency)

# ✅ INFO — lifecycle events
logger.info("Kernel started. workspace=%r offline_mode=%s", workspace, offline)
logger.info("Skill %r loaded with %d commands", skill_name, cmd_count)

# ✅ WARNING — degraded but operational
logger.warning("Short-lived memory approaching capacity (%d/%d entries)", current, max_entries)
logger.warning("Provider %r unavailable; falling back to %r", primary, fallback)

# ✅ ERROR — operation failure
logger.error("store_entry failed for key=%r: %s", entry.key, err, exc_info=True)
logger.error("Config file not found at %r; using defaults", config_path)

# ✅ CRITICAL — unrecoverable
logger.critical("Cannot open database %r — system cannot start: %s", db_path, err)
```

### 2.3 `exc_info` Parameter

Always pass `exc_info=True` when logging an exception to include the full traceback in the log:

```python
try:
    result = db.execute(sql)
except sqlite3.OperationalError as err:
    logger.error("Query failed: %s", err, exc_info=True)
    raise MemoryServiceError("Database query failed") from err
```

Use `exc_info=True` at `ERROR` and `CRITICAL` levels. It is optional at `WARNING` if the traceback would be noise.

---

## 3. Message Formatting

### 3.1 Use `%`-style Formatting — Never f-strings

The `logging` module uses lazy `%`-style formatting: the string is only formatted if the log record is actually emitted. F-strings are evaluated eagerly, even if the log level is too low to emit the record.

```python
# ✅ Lazy — formatted only if emitted
logger.debug("Processing entry key=%r tier=%d", entry.key, entry.tier)

# ❌ Eager — always formats, even when DEBUG is disabled
logger.debug(f"Processing entry key={entry.key!r} tier={entry.tier}")
```

### 3.2 Message Structure

Every log message must be:

1. **Structured** — key=value pairs for machine-readable fields.
2. **Concise** — one line, one fact.
3. **Context-rich** — include the identifying values needed to diagnose the event.

```
"{verb} {subject}: {key1}={val1} {key2}={val2}"

# Examples:
"Stored entry: key=%r tier=%d size_bytes=%d"
"Provider request failed: provider=%r attempt=%d/%d error=%s"
"Skill loaded: name=%r version=%r commands=%d"
```

### 3.3 `%r` vs `%s`

| Format | When to Use |
|--------|------------|
| `%r` | Use for values that should be quoted in the output: strings, paths, names, keys |
| `%s` | Use for values that render naturally: integers, floats, booleans, exceptions |
| `%d` | Integer values |
| `%.1f` | Float values with controlled precision |

```python
# ✅
logger.info("Loading config from %r", config_path)        # path quoted
logger.debug("tier=%d tokens=%d provider=%r", tier, n, p) # mixed
logger.warning("Retry %d/%d for %r", attempt, max_r, url) # url quoted
```

---

## 4. Structured Context (Extra Fields)

For events that need machine-queryable fields (e.g., for future log aggregation), use the `extra` parameter to attach structured context to the log record:

```python
logger.info(
    "Provider request completed",
    extra={
        "provider": provider.name,
        "model": model_id,
        "latency_ms": round(elapsed * 1000, 1),
        "tokens_used": response.usage.total_tokens,
    },
)
```

`extra` fields are stored on the `LogRecord` and are available to custom `Formatter` implementations. They must not conflict with built-in `LogRecord` attributes (`name`, `levelname`, `message`, `asctime`, etc.).

---

## 5. Privacy & Sensitive Data Redaction

This section is **non-negotiable**. Violation is both a coding defect and an ethics violation — see [engineering_ethics.md §3](../engineering_ethics.md).

### 5.1 What Must Never Appear in Logs

| Data Category | Examples | Rule |
|---------------|---------|------|
| API keys / secrets | `OPENAI_API_KEY`, bearer tokens | Never log, even at DEBUG |
| User passwords / PINs | Authentication credentials | Never log |
| Full file content | User documents, personal notes | Log file name only; never content |
| Conversation content | Full LLM prompt or response text | Log token count only; never text |
| Personal identifiable info | Names, emails embedded in data | Log anonymised IDs only |
| Filesystem absolute paths of user data | `/Users/anzarakhtar/personal/` | Log relative paths or hash |

### 5.2 Safe Logging Patterns

```python
# ✅ Log the key name, not the key value
logger.debug("API key loaded for provider=%r", provider_name)
# ❌ Never:
logger.debug("API key: %r", api_key)

# ✅ Log token count, not conversation content
logger.info("LLM response received: tokens=%d provider=%r", token_count, provider)
# ❌ Never:
logger.debug("LLM response: %r", response.content)

# ✅ Log file name and size; not content
logger.info("Memory entry stored: key=%r size_bytes=%d", key, len(content))
# ❌ Never:
logger.debug("Entry content: %r", content)
```

### 5.3 Redaction Utility

When a value may or may not be sensitive depending on context, use the redaction helper:

```python
def _redact(value: str, show_chars: int = 4) -> str:
    """Return a redacted version showing only the last N characters."""
    if len(value) <= show_chars:
        return "***"
    return f"***{value[-show_chars:]}"

# Usage:
logger.debug("API key suffix: %s", _redact(api_key))
# Output: "API key suffix: ...k9Xz"
```

---

## 6. Logger Configuration (Bootstrap)

Logger configuration is performed **only** in `bootstrap.py` (the Composition Root). Library modules must never configure handlers, formatters, or levels — they only call `logging.getLogger(__name__)`.

### 6.1 Canonical Bootstrap Configuration

```python
# core/src/aios/bootstrap.py

import logging
import logging.handlers
from pathlib import Path

def configure_logging(log_dir: Path, level: str = "INFO") -> None:
    """Configure the application-wide logging stack.

    Args:
        log_dir: Directory where log files are written.
        level: Minimum log level for the console handler.
    """
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "aios.log"

    root_logger = logging.getLogger("aios")
    root_logger.setLevel(logging.DEBUG)  # capture all; handlers filter

    # Console handler — INFO and above
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, level.upper(), logging.INFO))
    console_handler.setFormatter(logging.Formatter(
        fmt="%(levelname)-8s %(name)s — %(message)s"
    ))

    # Rotating file handler — DEBUG and above; 5 MB × 3 backups
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(
        fmt="%(asctime)s %(levelname)-8s %(name)s — %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    ))

    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
```

### 6.2 Log File Location

| File | Location | Rotation |
|------|----------|---------|
| `aios.log` | `~/.aios/logs/aios.log` | 5 MB, 3 backups |

Log files are local-only. They must never be transmitted to external services.

### 6.3 Log Level from Configuration

The console log level is driven by `config.toml`:

```toml
[logging]
level = "INFO"   # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

`DEBUG` is the development default; `INFO` is the production default. The file handler always logs at `DEBUG` regardless of the config setting.

---

## 7. Test Logging

In test code, avoid configuring the logging system. Use `caplog` (pytest's built-in log capture fixture) to assert on log output:

```python
import logging

def test_store_entry_logs_error_on_db_failure(caplog, memory_service):
    with caplog.at_level(logging.ERROR, logger="aios.services.local_memory_service"):
        memory_service.store_entry(broken_entry)

    assert "store_entry failed" in caplog.text
    assert broken_entry.key in caplog.text
```

Do not call `logging.basicConfig()` or add handlers in test files.

---

## 8. Logging Anti-Pattern Reference

| Anti-Pattern | Why Prohibited | Correct Alternative |
|-------------|---------------|-------------------|
| `print()` for diagnostics | Bypasses log routing; no level, no hierarchy | `logger.debug()` or `logger.info()` |
| `logging.getLogger("hardcoded.name")` | Breaks hierarchy; not refactor-safe | `logging.getLogger(__name__)` |
| F-string in log message | Eagerly evaluated even when level is off | `%`-style lazy formatting |
| Logging API keys or secrets | Privacy violation + security risk | Log key name/presence only |
| Logging full user content | Privacy violation | Log token count or content hash |
| `logging.basicConfig()` in library code | Pollutes root logger for all consumers | Configure only in `bootstrap.py` |
| `logger = logging.getLogger()` root logger | Affects third-party library logging | `logging.getLogger(__name__)` |
| Catching + logging + swallowing | Hides the failure from callers | Log + re-raise or return typed failure |

---

## 9. Logging Compliance Checklist

Before committing any Python change, verify:

- [ ] No `print()` calls used for diagnostic output in `core/src/aios/`
- [ ] All loggers use `logging.getLogger(__name__)`
- [ ] Log messages use `%`-style formatting, not f-strings
- [ ] No API keys, secrets, or personal data appear in any log call
- [ ] No full conversation content or file content is logged
- [ ] `exc_info=True` is passed at `ERROR`/`CRITICAL` level exception log calls
- [ ] Logger configuration is only in `bootstrap.py` — no `basicConfig()` in modules
- [ ] Log level choices match the level definition table (§2.1)

---

*Engineering Bible Coding Standards · Personal AI OS · Sprint 8 M2 · Governed by [engineering_principles.md](../engineering_principles.md)*
