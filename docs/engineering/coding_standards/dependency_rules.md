# Dependency Rules
**Engineering Bible — Coding Standards — Document 5 of 7**
**Version 1.0** · *Classified: For One Person Only* · *July 2026*

---

## Document Metadata

* **Purpose**: Define the policy for introducing, auditing, pinning, and retiring third-party dependencies in the Personal AI OS monorepo. Every dependency is a permanent liability; this document governs how that liability is incurred and controlled.
* **Scope**: All entries in `pyproject.toml`, `requirements*.txt`, and any tool that installs packages into the `.venv`.
* **Audience**: Software Engineers, AI coding agents, and Security Auditors.
* **Related Documents**:
  * [engineering_principles.md](../engineering_principles.md) — *Boring by Default* is the philosophical root of this policy.
  * [import_rules.md](import_rules.md) — Import boundary rules that apply once a dependency is approved (companion document).
  * [engineering_ethics.md](../engineering_ethics.md) — Supply chain ethics obligations.
  * [01_ENGINEERING_GUIDELINES.md §2](file:///Users/anzarakhtar/aios/docs/01_ENGINEERING_GUIDELINES.md) — SDLC dependency management policy.
  * [05_SECURITY_GUIDELINES.md §3](file:///Users/anzarakhtar/aios/docs/05_SECURITY_GUIDELINES.md) — Security evaluation requirements for new dependencies.
  * [10_DECISION_LOG.md](file:///Users/anzarakhtar/aios/docs/10_DECISION_LOG.md) — ADR log where dependency approvals are recorded.
* **Stability**: High. The admission criteria are non-negotiable.

---

> [!CAUTION]
> Every dependency added to this project is a **permanent liability**. It expands the attack surface, increases the maintenance burden, and risks supply chain compromise. The default answer to "should we add this dependency?" is **No**. The burden of proof falls entirely on the proposal to add, never on the objection to reject.

---

## 1. The Dependency Admission Decision Tree

Before adding any third-party package, the contributor must walk this decision tree in order. Skipping steps is not permitted.

```
Can the Python Standard Library solve this problem
within ~100 lines of readable code?
    │
    ├─ YES → Use the Standard Library. Do NOT add a dependency.
    │        (json, pathlib, sqlite3, asyncio, tomllib, subprocess,
    │         logging, typing, dataclasses, re, hashlib, datetime)
    │
    └─ NO → Does the proposed library touch personal data,
             API keys, or filesystem writes?
                │
                ├─ YES → Mandatory security review against
                │        05_SECURITY_GUIDELINES.md §3 before proceeding.
                │
                └─ NO + YES → Does an already-approved dependency
                               solve the problem with acceptable ergonomics?
                                   │
                                   ├─ YES → Use the existing dependency.
                                   │        Do NOT add a new one.
                                   │
                                   └─ NO → Write an ADR in 10_DECISION_LOG.md.
                                           Approval required before adding to
                                           pyproject.toml.
```

---

## 2. Admission Criteria

A dependency **may not be approved** unless it satisfies all five criteria:

| Criterion | Requirement |
|-----------|-------------|
| **Active maintenance** | ≥1 release or commit in the past 18 months |
| **Popularity signal** | ≥500 GitHub stars OR widely used in the Python ecosystem |
| **License compatibility** | MIT, Apache 2.0, BSD 2/3-Clause, or PSF. GPL/AGPL are prohibited without an explicit ADR. |
| **No telemetry** | Must not transmit any data to external servers by default |
| **Scoped purpose** | Must solve one specific problem — not a framework that brings 50 transitive dependencies |

### 2.1 Automatically Rejected Libraries

These categories are rejected without review:

| Category | Reason |
|----------|--------|
| ORM frameworks (SQLAlchemy, Tortoise) | `sqlite3` stdlib is sufficient for current data volumes |
| Full web frameworks (Flask, FastAPI, Django) | Out of scope for a local CLI system |
| Data science stacks (pandas, numpy) | Not a data science project |
| Logging frameworks (loguru, structlog) | `logging` stdlib handles all current needs |
| CLI frameworks (click, typer, rich > UI components) | Custom REPL is intentional; see [03_IMPLEMENTATION_GUIDELINES.md](file:///Users/anzarakhtar/aios/docs/03_IMPLEMENTATION_GUIDELINES.md) |
| Testing meta-frameworks | `pytest` is the approved and sole testing framework |

---

## 3. Approved Dependency Registry

This table lists all currently approved third-party dependencies. Any package not on this list requires an ADR before use.

| Package | Pinned Version | Purpose | ADR |
|---------|---------------|---------|-----|
| `httpx` | exact pin in `pyproject.toml` | Async HTTP client for provider API calls | ADR-001 |
| `tomli` / `tomllib` | stdlib in 3.11+ | TOML configuration parsing | Built-in |
| `openai` | exact pin | OpenAI API client | ADR-002 |
| `anthropic` | exact pin | Anthropic API client | ADR-003 |
| `qdrant-client` | exact pin | Qdrant vector store client | ADR-004 |
| `redis` | exact pin | Redis cache / coordination client | ADR-005 |
| `pytest` | exact pin | Test framework | ADR-006 |
| `pytest-asyncio` | exact pin | Async test support | ADR-006 |
| `ruff` | exact pin | Linter + formatter (dev only) | ADR-007 |

> [!NOTE]
> This table is the single source of truth for approved dependencies. The `pyproject.toml` file reflects this table; discrepancies between the two are bugs.

---

## 4. Version Pinning Policy

### 4.1 Exact Version Pins Required

All dependencies use **exact version pins**. No version ranges, no minimum bounds, no `latest`.

```toml
# ✅ Correct — exact pin
[project.optional-dependencies]
ai = [
    "openai==1.35.0",
    "anthropic==0.28.0",
    "httpx==0.27.0",
]

# ❌ Banned — range specifiers
"openai>=1.30.0"      # upper bound missing
"openai^1.35.0"       # caret — not valid in PEP 440 but signals intent
"openai~=1.35.0"      # tilde — range
"openai"              # unpinned — non-deterministic builds
```

**Rationale**: Exact pins guarantee that every build — now and in 5 years — installs the identical dependency graph. Non-deterministic builds violate the *Boring by Default* principle's stability requirement.

### 4.2 Pinning Transitive Dependencies

Direct dependencies must be pinned. Transitive dependencies are managed by `pip`'s lock mechanism. When a pinned transitive dependency creates a conflict, a `constraints.txt` file is used — not loosening the direct pins.

### 4.3 Pin Upgrade Protocol

Upgrading a pinned dependency requires:

1. A reason documented in the commit message (security patch, required feature, breaking change mitigation).
2. All tests passing after the upgrade.
3. A note in [10_DECISION_LOG.md](file:///Users/anzarakhtar/aios/docs/10_DECISION_LOG.md) if the upgrade changes behaviour.

---

## 5. Dependency Separation

### 5.1 Runtime vs Development Dependencies

```toml
[project]
dependencies = []                        # Runtime only — keep minimal

[project.optional-dependencies]
ai = [                                   # AI provider clients
    "openai==1.35.0",
    "anthropic==0.28.0",
]
vector = [                               # Vector store
    "qdrant-client==1.9.1",
]
dev = [                                  # Development-only — never installed in production
    "pytest==8.2.2",
    "pytest-asyncio==0.23.7",
    "ruff==0.4.9",
]
```

### 5.2 Rules for `dev` Dependencies

* `dev` dependencies must **never** be imported in production code (`core/src/aios/`).
* If a test helper is imported in production code, it has been incorrectly classified.
* `ruff`, `pytest`, and `mypy` are always `dev` — they must never appear in `[project.dependencies]`.

---

## 6. Security Evaluation Requirements

Before any dependency that touches **personal data, credentials, or network I/O** is approved, the following checks are mandatory:

| Check | How to Verify |
|-------|--------------|
| No hidden telemetry | Read the library's privacy policy and source; search for `requests.post`, `urllib.request`, `httpx.post` calls in library source not triggered by user action |
| Licence audit | `pip show {package}` and verify licence field |
| Known vulnerabilities | `pip audit` (or `safety check`) on the proposed version |
| Maintainer reputation | Check PyPI page, GitHub, and recent commit history |
| Offline mode compatibility | Confirm the library does not call home when `AIOS_OFFLINE_MODE=true` |

Security evaluation results must be summarised in the ADR that approves the dependency.

---

## 7. Retiring a Dependency

When a dependency is no longer needed:

1. Remove all import statements referencing it.
2. Remove it from `pyproject.toml`.
3. Run `pip uninstall {package}` and verify no import errors.
4. Record the retirement reason in [10_DECISION_LOG.md](file:///Users/anzarakhtar/aios/docs/10_DECISION_LOG.md).
5. Verify `ruff check F401` is clean after removal.

**Zombie dependencies** (listed in `pyproject.toml` but never imported) are detected by `pip-check-reqs` and must be removed within the same sprint.

---

## 8. Standard Library Preference Reference

This table lists the standard library alternatives that eliminate common dependency requests.

| Capability Needed | Standard Library Module | Notes |
|------------------|------------------------|-------|
| HTTP requests | `urllib.request` | Use `httpx` (approved) for async; `urllib` for sync scripts |
| JSON | `json` | Always prefer over `orjson`, `ujson` |
| TOML | `tomllib` (3.11+) | Built-in since Python 3.11 |
| SQLite | `sqlite3` | Covers all current storage needs |
| File paths | `pathlib.Path` | Never use raw string path manipulation |
| Async | `asyncio` | No third-party event loops |
| Typing | `typing`, `types` | No `typing-extensions` unless backporting pre-3.12 features |
| Logging | `logging` | See [logging_standards.md](logging_standards.md) |
| Subprocess | `subprocess` | `shell=False` always |
| Date/time | `datetime` | Never `arrow`, `pendulum`, or `dateutil` for basic date arithmetic |
| Data classes | `dataclasses` | Prefer over `attrs`, `pydantic` for internal models |
| Regular expressions | `re` | |
| Hash / crypto | `hashlib`, `secrets` | `secrets` for token generation; `hashlib` for digests |
| Argument parsing | `argparse` | CLI parsing in non-REPL contexts |
| Environment vars | `os.environ` | `python-dotenv` is approved for loading `.env` in dev |

---

## 9. Dependency Compliance Checklist

Before any `pyproject.toml` change, verify:

- [ ] The dependency satisfies all five admission criteria (§2)
- [ ] An ADR has been written and approved in `10_DECISION_LOG.md`
- [ ] The version is pinned exactly (no ranges)
- [ ] The dependency is in the correct optional group (`ai`, `vector`, `dev`)
- [ ] A security evaluation summary is included in the ADR
- [ ] The approved dependency registry table in this document is updated
- [ ] `pip audit` shows zero known vulnerabilities for the pinned version
- [ ] All existing tests pass with the new dependency installed

---

*Engineering Bible Coding Standards · Personal AI OS · Sprint 8 M2 · Governed by [engineering_principles.md](../engineering_principles.md)*
