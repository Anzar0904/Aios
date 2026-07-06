# Coding Standards
**Engineering Bible — Milestone 2**
**Version 1.0** · *Classified: For One Person Only* · *July 2026*

> [!IMPORTANT]
> This directory is the **Coding Standards** layer of the Engineering Bible.
> It translates the five operational laws in [engineering_principles.md](../engineering_principles.md)
> into concrete, machine-checkable rules that govern every line of code in the monorepo.
> If any rule here conflicts with the Foundation layer, the Foundation wins.

---

## Purpose

`docs/engineering/coding_standards/` answers the question every contributor must be able to answer before writing a single line:

> **What are the exact rules I must follow for this kind of code?**

These are not stylistic suggestions — they are hard constraints. Violations are blocking defects.

---

## Document Map

```
docs/engineering/coding_standards/
├── README.md                  ← This file — navigation hub
├── python_standards.md        ← Formatting, type hints, docstrings, complexity budgets
├── naming_conventions.md      ← Identifier naming for every entity type
├── project_structure.md       ← Directory layout, nesting limits, file placement
├── import_rules.md            ← Import ordering, boundary enforcement, circular imports
├── dependency_rules.md        ← Dependency admission, pinning, and security evaluation
├── error_handling.md          ← Exception design, propagation, timeouts, user messages
└── logging_standards.md       ← Logger acquisition, levels, formatting, redaction
```

---

## Reading Order

| Step | Document | When to Read |
|------|----------|--------------|
| 1 | [python_standards.md](python_standards.md) | Before writing any Python code |
| 2 | [naming_conventions.md](naming_conventions.md) | Before naming any identifier |
| 3 | [project_structure.md](project_structure.md) | Before creating any new file or directory |
| 4 | [import_rules.md](import_rules.md) | Before writing any `import` statement |
| 5 | [dependency_rules.md](dependency_rules.md) | Before adding any entry to `pyproject.toml` |
| 6 | [error_handling.md](error_handling.md) | Before writing any `try`/`except` block or failure path |
| 7 | [logging_standards.md](logging_standards.md) | Before writing any log call |

AI coding agents **must** read the relevant document from this list before implementing the corresponding code construct.

---

## Quick Reference — Hard Constraints

These rules admit no exceptions without an ADR in [10_DECISION_LOG.md](file:///Users/anzarakhtar/aios/docs/10_DECISION_LOG.md):

| Constraint | Rule |
|-----------|------|
| File length | ≤ 400 lines |
| Function complexity | ≤ 10 cyclomatic complexity |
| Function parameters | ≤ 4 (use dataclass beyond 4) |
| Line length | ≤ 100 characters |
| Import style | Explicit named imports only — no wildcards |
| Dependency pinning | Exact version — no ranges |
| Exception catching | Specific types only — no bare `except:` |
| Logging | `logging.getLogger(__name__)` — no `print()` |
| I/O operations | Explicit timeout always required |
| Secrets in logs | Never — API keys and personal data are redacted |

---

## Relationship to the Engineering Bible Foundation

```
docs/engineering/           ← Foundation (Milestone 1)
     │
     └── coding_standards/  ← YOU ARE HERE (Milestone 2)
              │
              ├── Implements ──▶  engineering_principles.md (all five laws)
              ├── Enforces  ──▶  philosophy.md §2.3 (Trust Through Transparency)
              └── Enables   ──▶  docs/08_CODING_STANDARDS.md (summary reference)
```

---

## Relationship to the Broader Documentation Suite

| Document | Relationship |
|----------|-------------|
| [08_CODING_STANDARDS.md](file:///Users/anzarakhtar/aios/docs/08_CODING_STANDARDS.md) | Summary reference; this directory is the canonical expansion |
| [01_ENGINEERING_GUIDELINES.md](file:///Users/anzarakhtar/aios/docs/01_ENGINEERING_GUIDELINES.md) | SDLC gates that these standards feed into |
| [02_ARCHITECTURE_GUIDELINES.md](file:///Users/anzarakhtar/aios/docs/02_ARCHITECTURE_GUIDELINES.md) | Service boundary contracts enforced by import_rules.md |
| [05_SECURITY_GUIDELINES.md](file:///Users/anzarakhtar/aios/docs/05_SECURITY_GUIDELINES.md) | Security constraints reflected in error_handling.md and logging_standards.md |
| [06_TESTING_GUIDELINES.md](file:///Users/anzarakhtar/aios/docs/06_TESTING_GUIDELINES.md) | Test code follows all these same standards |
| [10_DECISION_LOG.md](file:///Users/anzarakhtar/aios/docs/10_DECISION_LOG.md) | Where exceptions to these standards are formally recorded |

---

## Versioning & Stability Contract

| Property | Rule |
|----------|------|
| Version | All files in this directory share the Engineering Bible version |
| Mutations | Changes committed in a dedicated `docs:` commit, never mixed with feature work |
| Deprecation | No rule may be removed without a replacement — only superseded |
| AI Authorship | AI-generated commits carry `Co-authored-by: AI-agent <assistant@personal-ai-os.local>` |

---

*Engineering Bible Coding Standards · Personal AI OS · Sprint 8 M2 · Governed by [engineering_principles.md](../engineering_principles.md)*
