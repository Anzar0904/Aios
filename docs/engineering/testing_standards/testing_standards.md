# Testing Playbook & Framework Standards
**Engineering Bible — Milestone 4**
**Version 1.0** · *Classified: For One Person Only* · *July 2026*

---

## 1. Testing Philosophy: Contract-First Reliability

The Personal AI OS uses a **Contract-First** approach to quality. Since this OS is designed to run locally and handle files and models without user supervision, code changes must not break system contracts.

### Core Testing Rules
1. **Assert Against Public Interfaces**: Tests must verify public service contracts (such as event emissions, return values, and registry keys) rather than private helper methods. Tests should survive refactoring that preserves overall behavior.
2. **Fast & Network-Free Execution**: Tests must run locally. They are prohibited from making network calls or relying on external API connections. The entire test suite must execute in under **5 seconds**.
3. **No Muted Failures**: Bypassing assertions or skipping tests without a corresponding issue is prohibited. If a test fails, it represents either a code regression or a changed requirement—both of which require code correction, not test avoidance.

---

## 2. The Test Pyramid

Verification is structured around three main tiers to balance speed and coverage:

```
                   +---------------------------------------+
                   |                 E2E                   |
                   |                (~5%)                  |
                   +───────────────────┬───────────────────+
                                       │
                                       ▼
                   +---------------------------------------+
                   |             INTEGRATION               |
                   |               (~25%)                  |
                   +───────────────────┬───────────────────+
                                       │
                                       ▼
                   +---------------------------------------+
                   |                UNIT                   |
                   |               (~70%)                  |
                   +---------------------------------------+
```

### 1. Unit Tests (~70%)
* **Target**: Single functions, classes, and logic paths (e.g. `test_event_bus.py`, `test_context.py`).
* **Isolation**: All dependencies are mocked. Zero filesystem mutations, network requests, or subprocesses.

### 2. Integration Tests (~25%)
* **Target**: Boundaries where services interact (e.g. `test_providers.py` routing, `test_session.py` cache flushes).
* **Isolation**: Limits mock scopes to external factors (like vendor model APIs or host terminal terminals).

### 3. End-to-End (E2E) Tests (~5%)
* **Target**: Full execution paths (e.g., executing the CLI REPL loop, processing inputs, and asserting on terminal outputs).
* **Isolation**: Fully isolated using temporary workspace directories and mocked AI provider endpoints.

---

## 3. Pre-Release Verification Gates

Before code changes are committed, they must pass the following checks:

```
 [Code Edit] ➔ [ruff Linter Gate] ➔ [Fast pytest Suite] ➔ [Coverage Check] ➔ [Release Ready]
```

* **Linter Gate**: Run `ruff check ./core` and `ruff format --check ./core` to ensure formatting compliance.
* **Pytest Verification**: Run `PYTHONPATH=. pytest` to ensure all tests pass.
* **Coverage Verification**: Run `PYTHONPATH=. pytest --cov=core` to verify that coverage meets the **85%** requirement.
* **No Unstaged Secrets**: Confirm that API keys and personal files are not present in git history logs.

---

*Engineering Bible Testing Standards · Personal AI OS · Sprint 8 M4 · Governed by [06_TESTING_GUIDELINES.md](file:///Users/anzarakhtar/aios/docs/06_TESTING_GUIDELINES.md)*
