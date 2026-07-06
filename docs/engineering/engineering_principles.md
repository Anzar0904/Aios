# Engineering Principles
**Engineering Bible Foundation — Document 3 of 5**
**Version 1.0** · *Classified: For One Person Only* · *July 2026*

---

## Document Metadata

* **Purpose**: Define the five operational engineering laws that govern every coding session, every AI-assisted contribution, and every structural decision in the Personal AI OS. These laws are not stylistic preferences — they are hard constraints whose violation must be detected, flagged, and corrected before any change is considered done.
* **Scope**: Applies to all code in the monorepo: `core/`, `skills/`, `config/`, `tests/`, `docs/`. No module is exempt.
* **Audience**: Software Engineers, AI coding agents, and Technical Reviewers.
* **Related Documents**:
  * [00_PROJECT_VISION.md §5](file:///Users/anzarakhtar/aios/docs/00_PROJECT_VISION.md) — Constitutional source of the Guiding Principles from which these laws are derived.
  * [philosophy.md](philosophy.md) — Philosophical foundation this document operationalises.
  * [Engineering_Constitution.md §1](file:///Users/anzarakhtar/aios/Engineering_Constitution.md) — Original canonical statement of these principles.
  * [01_ENGINEERING_GUIDELINES.md §1](file:///Users/anzarakhtar/aios/docs/01_ENGINEERING_GUIDELINES.md) — SDLC enforcement of these laws.
  * [design_goals.md](design_goals.md) — System-level design properties derived from these principles.
* **Stability**: High. These five laws are the stable core of the Engineering Bible. Extensions are permitted; removals require a full constitutional review.

---

> [!IMPORTANT]
> **These five laws have a precedence hierarchy.**
> When two laws appear to conflict, resolve using this order:
> 1. Boring by Default
> 2. Optimize for Deletion
> 3. One Reason to Change
> 4. Working Software Over Perfect Architecture
> 5. No Speculative Generality
>
> In practice, genuine conflicts are rare. Most apparent conflicts are design smells indicating the feature itself needs rethinking.

---

## 1. Boring by Default

> *Choose the most proven, widely-documented technology over the newest one.*

### Rationale

A single-user system has no team to absorb the risk of exotic tooling. Boring technology is:
- Well-documented — critical when the primary contributor is an AI agent with no persistent memory.
- Stable — critical for a system intended to run unattended for a decade.
- Debuggable — standard libraries produce standard error messages that any AI agent can interpret correctly.

This principle directly operationalises the **Simple** and **Fast** Guiding Principles from [philosophy.md §3](philosophy.md).

### Operational Rules

| Rule | Constraint | Where Enforced |
|------|-----------|----------------|
| Standard library first | If `json`, `sqlite3`, `pathlib`, `asyncio`, or `tomli` solves the problem within ~100 lines, write it — do not add a dependency. | [01_ENGINEERING_GUIDELINES.md §2.1](file:///Users/anzarakhtar/aios/docs/01_ENGINEERING_GUIDELINES.md) |
| Stable over new | Libraries must have an active release history (commits/releases within 18 months). | [01_ENGINEERING_GUIDELINES.md §2.1](file:///Users/anzarakhtar/aios/docs/01_ENGINEERING_GUIDELINES.md) |
| Small over large | Prefer a single-purpose library (`httpx`) over a framework (`requests[security]`, agentic middleware). | [01_ENGINEERING_GUIDELINES.md §2.1](file:///Users/anzarakhtar/aios/docs/01_ENGINEERING_GUIDELINES.md) |
| Exotic requires ADR | Any non-standard paradigm (async frameworks, reactive patterns, DSLs) requires a formal entry in [10_DECISION_LOG.md](file:///Users/anzarakhtar/aios/docs/10_DECISION_LOG.md). | [01_ENGINEERING_GUIDELINES.md §2.3](file:///Users/anzarakhtar/aios/docs/01_ENGINEERING_GUIDELINES.md) |
| Pin exact versions | All dependencies use exact version pinning in `pyproject.toml`. No `^`, `~`, `>=`, or `latest`. | [01_ENGINEERING_GUIDELINES.md §2.2](file:///Users/anzarakhtar/aios/docs/01_ENGINEERING_GUIDELINES.md) |

### Violation Signal

> *"This library is newer and more elegant."*

"Elegant" and "new" are not valid justifications. If the same outcome can be achieved with a standard library or a stable alternative, the newer option is rejected.

---

## 2. Optimize for Deletion

> *Every module must be easy to delete and replace, not just easy to add to.*

### Rationale

The Constitutional acknowledgment that "today's best model is tomorrow's second-best" is not a statement about AI providers alone — it applies to every component. Databases, event buses, CLI frameworks, and skill implementations will be superseded. A system that makes deletion painful accumulates dead weight.

This principle directly operationalises the **Modular** and **Extensible** Guiding Principles from [philosophy.md §3](philosophy.md).

### Operational Rules

| Rule | Constraint | Where Enforced |
|------|-----------|----------------|
| Single public boundary | Every module exposes a defined set of public functions/classes. Nothing outside the module accesses internals. | [Engineering_Constitution.md §3](file:///Users/anzarakhtar/aios/Engineering_Constitution.md) |
| No sibling coupling | Modules do not depend on each other's private submodules. Shared logic is extracted into a dedicated module. | [Engineering_Constitution.md §3](file:///Users/anzarakhtar/aios/Engineering_Constitution.md) |
| Adapter isolation | All AI model access is behind an adapter interface — never called directly from business logic. | [Engineering_Constitution.md §3](file:///Users/anzarakhtar/aios/Engineering_Constitution.md) |
| Contract communication | Modules communicate through explicit data contracts, not shared global state. | [02_ARCHITECTURE_GUIDELINES.md §3](file:///Users/anzarakhtar/aios/docs/02_ARCHITECTURE_GUIDELINES.md) |
| Module README | Every module has a one-paragraph README stating its purpose, public interface, and explicit non-responsibilities ("what it does NOT do"). | [Engineering_Constitution.md §3](file:///Users/anzarakhtar/aios/Engineering_Constitution.md) |

### Deletion Test

Before considering a module complete, ask: *"Can I delete this entire directory and replace it with a different implementation of the same interface without touching any other file?"*

If the answer is no, the module's boundaries are wrong.

---

## 3. One Reason to Change

> *Each file, function, or module should have exactly one responsibility.*

### Rationale

Mixed responsibilities are the primary source of AI-introduced regressions. When a file handles both serialisation and domain logic, a change intended to fix a storage bug silently modifies business behaviour. In a system where contributors have no shared memory across sessions, this risk is compounded.

This principle directly operationalises the **Simple** and **Minimal** Guiding Principles from [philosophy.md §3](philosophy.md), and maps to the Single Responsibility Principle (SRP).

### Operational Rules

| Rule | Constraint | Where Enforced |
|------|-----------|----------------|
| Class-domain isolation | Class definitions focus on a single domain. `ConversationStore` handles serialisation; `ConversationManager` coordinates active instances — they are never merged. | [01_ENGINEERING_GUIDELINES.md §1.3](file:///Users/anzarakhtar/aios/docs/01_ENGINEERING_GUIDELINES.md) |
| Script separation | Presentation loops (`cli.py`) are never mixed with bootstrap logic (`bootstrap.py`) or domain logic (`kernel.py`). | [01_ENGINEERING_GUIDELINES.md §1.3](file:///Users/anzarakhtar/aios/docs/01_ENGINEERING_GUIDELINES.md) |
| File size limit | No file exceeds **400 lines**. Exceeding this limit is a mandatory split trigger, not a guideline. | [Engineering_Constitution.md §2](file:///Users/anzarakhtar/aios/Engineering_Constitution.md) |
| Complexity cap | Cyclomatic complexity per function is capped at **10**. Functions beyond this are extracted. | [Engineering_Constitution.md §6](file:///Users/anzarakhtar/aios/Engineering_Constitution.md) |
| Parameter limit | No function takes more than **4 parameters**. Beyond four, pass a single structured object. | [Engineering_Constitution.md §6](file:///Users/anzarakhtar/aios/Engineering_Constitution.md) |

### Violation Signal

> *"I need to modify this file for two different reasons this sprint."*

If a file is being modified for two unrelated reasons, it has multiple responsibilities. Split before the second change is committed.

---

## 4. Working Software Over Perfect Architecture

> *Ship the simplest version that works, then refactor under real usage.*

### Rationale

This is a system for one user, evolving over a decade. Premature architecture built for requirements that don't yet exist will be wrong in ways that cannot be predicted. Real usage reveals the correct interfaces; speculative architecture hides them.

This principle directly operationalises the **Minimal** and **Fast** Guiding Principles from [philosophy.md §3](philosophy.md), and mirrors the Agile Manifesto value it is named after.

### Operational Rules

| Rule | Constraint | Where Enforced |
|------|-----------|----------------|
| Simplest version first | Build the simplest implementation that passes the test suite and meets the documented requirement. | [01_ENGINEERING_GUIDELINES.md §1.4](file:///Users/anzarakhtar/aios/docs/01_ENGINEERING_GUIDELINES.md) |
| No premature abstraction | Do not create abstract interface layers for components that have only one concrete implementation today. | [01_ENGINEERING_GUIDELINES.md §1.4](file:///Users/anzarakhtar/aios/docs/01_ENGINEERING_GUIDELINES.md) |
| Refactor under tests | Refactoring is only permitted when the module has test coverage. Run the suite before starting; all tests must remain green throughout. | [01_ENGINEERING_GUIDELINES.md §3.2](file:///Users/anzarakhtar/aios/docs/01_ENGINEERING_GUIDELINES.md) |
| Refactor trigger | Refactor when tests become hard to write (coupling signal) or when duplication appears across modules — not on a schedule. | [01_ENGINEERING_GUIDELINES.md §3.1](file:///Users/anzarakhtar/aios/docs/01_ENGINEERING_GUIDELINES.md) |
| Isolated refactors | Refactoring commits are dedicated commits. Mixing refactoring with features or fixes is prohibited. | [Engineering_Constitution.md §15](file:///Users/anzarakhtar/aios/Engineering_Constitution.md) |

### Violation Signal

> *"Let me design the full generic interface before writing the first implementation."*

If there is no second concrete implementation to justify the abstraction, the interface is premature. Write the concrete implementation first.

---

## 5. No Speculative Generality

> *Do not build for a future requirement that does not exist yet.*

### Rationale

Every speculative abstraction, unused parameter, and placeholder function is immediate maintenance overhead. It confuses AI reasoning pathways (the agent must determine whether placeholder code is intentional or vestigial), inflates test surface area, and violates the **Minimal** Guiding Principle directly.

This principle directly operationalises the **Minimal** Guiding Principle from [philosophy.md §3](philosophy.md).

### Operational Rules

| Rule | Constraint | Where Enforced |
|------|-----------|----------------|
| No placeholder stubs | No stub methods, dummy routes, or unused wrapper APIs are added under the assumption they will be needed later. | [01_ENGINEERING_GUIDELINES.md §1.5](file:///Users/anzarakhtar/aios/docs/01_ENGINEERING_GUIDELINES.md) |
| Active requirement gate | Every function parameter, class method, and environment variable must serve a current, active sprint requirement. | [01_ENGINEERING_GUIDELINES.md §1.5](file:///Users/anzarakhtar/aios/docs/01_ENGINEERING_GUIDELINES.md) |
| No dead code | Dead code is deleted, never commented out. Version control is the archive. | [Engineering_Constitution.md §6](file:///Users/anzarakhtar/aios/Engineering_Constitution.md) |
| No magic literals | Every literal with domain meaning is a named constant. Magic numbers and magic strings are prohibited. | [Engineering_Constitution.md §6](file:///Users/anzarakhtar/aios/Engineering_Constitution.md) |
| Out-of-scope blocking | If a feature is not part of the active sprint or active roadmap milestone, code for it must not be written or merged. | [01_ENGINEERING_GUIDELINES.md §1.5](file:///Users/anzarakhtar/aios/docs/01_ENGINEERING_GUIDELINES.md) |

### Violation Signal

> *"I'll add this parameter now — we'll probably need it eventually."*

"Probably" is not a requirement. The parameter is not written until the requirement is confirmed and active.

---

## 6. Definition of Done — Principle Checklist

A change is considered done with respect to the five engineering principles only when all of the following are true:

- [ ] No new dependency was introduced without a formal ADR in [10_DECISION_LOG.md](file:///Users/anzarakhtar/aios/docs/10_DECISION_LOG.md) (**Boring by Default**).
- [ ] Every module touched can be deleted and replaced without touching other modules (**Optimize for Deletion**).
- [ ] No file exceeds 400 lines; no function exceeds complexity 10 or 4 parameters (**One Reason to Change**).
- [ ] No abstract interface was created without at least two concrete implementations to justify it (**Working Software Over Perfection**).
- [ ] No placeholder, stub, dead code, or magic literal remains in any touched file (**No Speculative Generality**).

The full Definition of Done checklist — covering compilation, testing, security, documentation, and version control — is maintained in [01_ENGINEERING_GUIDELINES.md §4](file:///Users/anzarakhtar/aios/docs/01_ENGINEERING_GUIDELINES.md).

---

## 7. Principle Precedence Reference

```
┌──────────────────────────────────────────────────────────────────────┐
│                    PRINCIPLE PRECEDENCE CHAIN                        │
├────┬──────────────────────────────┬──────────────────────────────────┤
│ P1 │ Boring by Default            │ Governs technology selection      │
│ P2 │ Optimize for Deletion        │ Governs module boundary design    │
│ P3 │ One Reason to Change         │ Governs file and function scope   │
│ P4 │ Working Software Over        │ Governs delivery and iteration    │
│    │ Perfect Architecture         │                                   │
│ P5 │ No Speculative Generality    │ Governs scope and dead code       │
└────┴──────────────────────────────┴──────────────────────────────────┘
```

When a Guiding Principle from [philosophy.md §3](philosophy.md) and an operational engineering law from this document appear to conflict, the Guiding Principle wins. This is consistent with the constitutional hierarchy established in [Engineering_Constitution.md](file:///Users/anzarakhtar/aios/Engineering_Constitution.md).

---

*Engineering Principles · Engineering Bible Foundation · Sprint 8 M1 · Derived from [Engineering_Constitution.md §1](file:///Users/anzarakhtar/aios/Engineering_Constitution.md)*
