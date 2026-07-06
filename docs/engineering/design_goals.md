# Design Goals
**Engineering Bible Foundation — Document 4 of 5**
**Version 1.0** · *Classified: For One Person Only* · *July 2026*

---

## Document Metadata

* **Purpose**: Define the non-negotiable system-level design properties that every component, interface, and service of the Personal AI OS must preserve at all times. These are properties the system must *have*, not features it must *do* — they are the invariants that make everything else trustworthy.
* **Scope**: Applies to all subsystems: Core Kernel, Service Layer, Execution Engines, Skill Packages, Memory System, Provider Adapters, CLI, and Configuration. A design property that is violated in any one subsystem is violated for the entire system.
* **Audience**: Systems Architects, Senior Engineers, and AI coding agents designing or extending services.
* **Related Documents**:
  * [00_PROJECT_VISION.md §5](file:///Users/anzarakhtar/aios/docs/00_PROJECT_VISION.md) — Guiding Principles that underpin these design properties.
  * [philosophy.md §3](philosophy.md) — Engineering interpretation of each Guiding Principle.
  * [engineering_principles.md](engineering_principles.md) — Operational laws this document extends into system architecture.
  * [02_ARCHITECTURE_GUIDELINES.md](file:///Users/anzarakhtar/aios/docs/02_ARCHITECTURE_GUIDELINES.md) — Architectural patterns that implement these properties.
  * [05_SECURITY_GUIDELINES.md](file:///Users/anzarakhtar/aios/docs/05_SECURITY_GUIDELINES.md) — Security and privacy enforcement of design goals DG-04, DG-06, DG-07.
  * [16_ENGINEERING_BIBLE.md](file:///Users/anzarakhtar/aios/docs/16_ENGINEERING_BIBLE.md) — Subsystem-level implementation of these properties.
* **Stability**: High. These properties are invariants. They should be added to only with a formal ADR. They should never be removed.

---

## Design Goal Index

| ID | Property | Guiding Principle | Primary Enforcement |
|----|----------|------------------|---------------------|
| DG-01 | [Replaceability](#dg-01-replaceability) | Modular | [02_ARCHITECTURE_GUIDELINES.md](file:///Users/anzarakhtar/aios/docs/02_ARCHITECTURE_GUIDELINES.md) |
| DG-02 | [Local-First Execution](#dg-02-local-first-execution) | Private | [05_SECURITY_GUIDELINES.md](file:///Users/anzarakhtar/aios/docs/05_SECURITY_GUIDELINES.md) |
| DG-03 | [Sub-200ms CLI Responsiveness](#dg-03-sub-200ms-cli-responsiveness) | Fast | [15_SYSTEM_DESIGN.md](file:///Users/anzarakhtar/aios/docs/15_SYSTEM_DESIGN.md) |
| DG-04 | [Explicit Data Boundaries](#dg-04-explicit-data-boundaries) | Private + Secure | [05_SECURITY_GUIDELINES.md](file:///Users/anzarakhtar/aios/docs/05_SECURITY_GUIDELINES.md) |
| DG-05 | [Tiered Memory Integrity](#dg-05-tiered-memory-integrity) | Intelligent | [16_ENGINEERING_BIBLE.md](file:///Users/anzarakhtar/aios/docs/16_ENGINEERING_BIBLE.md) |
| DG-06 | [Zero Silent Failures](#dg-06-zero-silent-failures) | Honest | [Engineering_Constitution.md](file:///Users/anzarakhtar/aios/Engineering_Constitution.md) |
| DG-07 | [Human-Gated Destructive Actions](#dg-07-human-gated-destructive-actions) | Secure + Honest | [05_SECURITY_GUIDELINES.md](file:///Users/anzarakhtar/aios/docs/05_SECURITY_GUIDELINES.md) |
| DG-08 | [Single-User Optimisation](#dg-08-single-user-optimisation) | Personal | [00_PROJECT_VISION.md](file:///Users/anzarakhtar/aios/docs/00_PROJECT_VISION.md) |
| DG-09 | [Contributor Orientability](#dg-09-contributor-orientability) | Simple | [07_DOCUMENTATION_GUIDELINES.md](file:///Users/anzarakhtar/aios/docs/07_DOCUMENTATION_GUIDELINES.md) |
| DG-10 | [Reversibility](#dg-10-reversibility) | Secure + Modular | [03_IMPLEMENTATION_GUIDELINES.md](file:///Users/anzarakhtar/aios/docs/03_IMPLEMENTATION_GUIDELINES.md) |

---

## DG-01: Replaceability

> *Any component must be removable and replaceable without touching other components.*

### What This Means

The system is built on the explicit assumption that every component will eventually be superseded. A better LLM provider will emerge. A faster database will become available. A more ergonomic CLI framework will be released. Replaceability is what keeps these transitions low-risk.

### Measurable Criterion

**Swapping any single service (LLM provider, database, event bus, CLI renderer) must require changes to exactly one adapter file and zero files outside that adapter.**

### Architecture Enforcement

* All orchestration code communicates through abstract contracts in `aios.services` — never through concrete implementations.
* The `ServiceRegistry` (`registry.py`) is the only location where concrete implementations are bound to abstract contracts.
* The Composition Root (`bootstrap.py`) is the only location where the service graph is wired.
* See: [02_ARCHITECTURE_GUIDELINES.md §3](file:///Users/anzarakhtar/aios/docs/02_ARCHITECTURE_GUIDELINES.md) — Interface-First Design and Composition Root.

### Violation Signal

A PR that swaps a service requires changes to `kernel.py`, `brain.py`, or any skill file. This indicates the abstraction boundary has been violated.

---

## DG-02: Local-First Execution

> *Local execution is the default. Remote calls are the exception, not the baseline.*

### What This Means

The system's core functions — memory retrieval, command execution, context assembly, and skill routing — must work without any network connection. Remote API calls to LLM providers are an optimisation over local execution, not a hard dependency.

### Measurable Criterion

**With `offline_mode = True` in `config/config.toml`, 100% of non-LLM system functions execute successfully. LLM calls route to locally-running providers (Ollama, LM Studio) without error.**

### Architecture Enforcement

* `offline_mode = True` blocks all remote API calls at the OmniRoute selector level.
* Memory reads, filesystem operations, git commands, and skill registry loading have zero network dependencies.
* Local provider endpoints (Ollama, LM Studio) are configured as the fallback in [04_AI_MODEL_STRATEGY.md](file:///Users/anzarakhtar/aios/docs/04_AI_MODEL_STRATEGY.md).

### Violation Signal

A module that imports an HTTP client at the module level (not inside a conditional code path guarded by `offline_mode`) has violated this goal.

---

## DG-03: Sub-200ms CLI Responsiveness

> *The time from user keystroke to first system output must not exceed 200ms on the critical path (excluding LLM generation time).*

### What This Means

Latency is the primary friction killer in a keyboard-driven system. The critical path — CLI input → Intent resolution → Kernel routing → Response dispatch — must not accumulate blocking I/O, synchronous model calls, or unguarded network requests.

### Measurable Criterion

**p95 latency for the CLI → Kernel → Response path is ≤ 200ms, measured at the `cli.py` level, excluding LLM token generation time.**

### Architecture Enforcement

* All external calls (API, database, filesystem) have explicit timeouts. See [Engineering_Constitution.md §7](file:///Users/anzarakhtar/aios/Engineering_Constitution.md).
* No blocking synchronous I/O on the main execution path without a performance justification documented in [10_DECISION_LOG.md](file:///Users/anzarakhtar/aios/docs/10_DECISION_LOG.md).
* Kernel boot and skill loading are measured in CI against the 200ms baseline.

### Violation Signal

A new import or initialisation step in `bootstrap.py` or `cli.py` that adds unconstrained I/O to the startup sequence.

---

## DG-04: Explicit Data Boundaries

> *Every path along which personal data travels must be explicitly documented, authorised, and auditable.*

### What This Means

The system stores career records, private code repositories, personal reflections, and conversation history. No piece of that data may travel to an external system without:
1. A formal ADR in [10_DECISION_LOG.md](file:///Users/anzarakhtar/aios/docs/10_DECISION_LOG.md) documenting the data flow.
2. Explicit, in-session user authorisation.
3. Encryption in transit.

### Measurable Criterion

**A complete data flow audit (from input to storage to retrieval to disposal) can be traced in documentation alone, without reading source code, for every data category in the system.**

### Architecture Enforcement

* Logs contain no personal data in plaintext — IDs, hashes, or redactions only. See [Engineering_Constitution.md §8](file:///Users/anzarakhtar/aios/Engineering_Constitution.md).
* Any dependency that requires network access or personal file access is subject to the Privacy Gate in [01_ENGINEERING_GUIDELINES.md §2.3](file:///Users/anzarakhtar/aios/docs/01_ENGINEERING_GUIDELINES.md).
* External data transmissions are flagged in [05_SECURITY_GUIDELINES.md](file:///Users/anzarakhtar/aios/docs/05_SECURITY_GUIDELINES.md).

### Violation Signal

A new library that reads memory cache files or conversation logs is added without a corresponding ADR and Privacy Gate review.

---

## DG-05: Tiered Memory Integrity

> *Memory data must maintain its tier classification, expiry contract, and retrieval accuracy across all system restarts and prune cycles.*

### What This Means

The Memory System's three tiers — Permanent, Long-Lived, Short-Lived — have defined retention contracts. These contracts are invariants. A prune cycle must never promote a Short-Lived record to Permanent, and it must never delete a Permanent record.

### Measurable Criterion

**After any prune cycle, all Permanent records are intact, all expired Short-Lived records are archived (not deleted), and all Long-Lived records within their retention window are retrievable by workspace scope.**

### Architecture Enforcement

* Memory tier definitions are canonical in [00_PROJECT_VISION.md §7](file:///Users/anzarakhtar/aios/docs/00_PROJECT_VISION.md).
* Prune logic is regression-tested on every commit against the critical paths defined in [Engineering_Constitution.md §9](file:///Users/anzarakhtar/aios/Engineering_Constitution.md).
* Memory storage and retrieval logic is isolated behind the `MemoryService` interface — no direct database access from skill or brain code.

### Violation Signal

A prune operation that modifies records with `tier = "permanent"` or that silently discards records rather than archiving them.

---

## DG-06: Zero Silent Failures

> *The system must never reach a state where a failure has occurred but no signal of that failure exists in logs, output, or system state.*

### What This Means

Silent failures — swallowed exceptions, empty catch blocks, false success responses — are the most dangerous failure mode in an unattended system. They allow the system to present a healthy appearance while its state is corrupt or incomplete.

### Measurable Criterion

**Every caught exception either (a) is handled with a documented, meaningful recovery path, or (b) is re-raised with added context. No empty `except` or `catch` block exists anywhere in the codebase.**

### Architecture Enforcement

* Fail loudly in development: exceptions propagate to the surface with full context.
* Fail safely in production: structured error responses with full technical detail in logs, plain-language messages to the user.
* Every automated job logs a start event and a completion event — even on success — so silence is distinguishable from failure.
* Governed by [Engineering_Constitution.md §7](file:///Users/anzarakhtar/aios/Engineering_Constitution.md) and [Engineering_Constitution.md §8](file:///Users/anzarakhtar/aios/Engineering_Constitution.md).

### Violation Signal

Any `except:` block with only a `pass` statement, or any log entry that reads only `"error occurred"` without context.

---

## DG-07: Human-Gated Destructive Actions

> *Any operation that cannot be automatically and reliably reversed must pause execution and require explicit human confirmation before proceeding.*

### What This Means

The Action Engine classifies operations into risk levels (LOW, MEDIUM, HIGH). HIGH-risk operations — those that delete, overwrite, or modify git history — are never executed without a manual confirmation gate. This gate cannot be bypassed by any automated process, including AI-generated task plans.

### Measurable Criterion

**No HIGH-risk operation executes without a user-visible confirmation prompt displayed before execution, and a file-content backup stored before any mutation begins.**

### Architecture Enforcement

* Risk classifications are maintained in [05_SECURITY_GUIDELINES.md](file:///Users/anzarakhtar/aios/docs/05_SECURITY_GUIDELINES.md).
* The Action Engine caches file contents before writing, enabling rollback on step failure. See [16_ENGINEERING_BIBLE.md §4.5](file:///Users/anzarakhtar/aios/docs/16_ENGINEERING_BIBLE.md).
* AI agents are explicitly prohibited from bypassing confirmation gates. See [Engineering_Constitution.md §17](file:///Users/anzarakhtar/aios/Engineering_Constitution.md).

### Violation Signal

A task plan generated by the Brain that includes a `DELETE` or `git push --force` step without a preceding user confirmation event in the execution log.

---

## DG-08: Single-User Optimisation

> *Every design decision is optimised for exactly one user. Multi-tenant code paths, generic user management, and mass-market defaults are prohibited.*

### What This Means

This system is not a product. It is a tool. Multi-tenancy, role-based access control, and generic onboarding flows are not features this system will ever need. Their presence would add complexity with zero utility. Any design that introduces them — even "just in case" — violates the **Minimal** and **No Speculative Generality** constraints.

### Measurable Criterion

**No user management system, session isolation mechanism, or multi-tenant data model exists anywhere in the codebase.**

### Architecture Enforcement

* Configuration is user-specific by default — `config/config.toml` assumes one operator.
* The system has no concept of "user ID" in its service layer.
* Any PR introducing user management concepts is rejected on the basis of this design goal.

### Violation Signal

A class or function parameter named `user_id`, `tenant_id`, or `account_id` appearing in core service code.

---

## DG-09: Contributor Orientability

> *A new contributor — human or AI, with no prior session context — must be able to orient themselves and begin contributing correctly within 60 seconds of reading `AI_CONTEXT.md` and `docs/engineering/`.*

### What This Means

This is the documentation invariant. It is not a style preference. A system where the contributor cannot quickly and correctly understand the codebase will degrade through misapplied changes. Documentation is a technical control, not a courtesy.

### Measurable Criterion

**From `AI_CONTEXT.md` alone, an AI agent can identify: (1) the system's purpose, (2) the active sprint context, (3) the primary module responsible for any described capability, and (4) the relevant documentation document for any architectural question.**

### Architecture Enforcement

* Every module has a README stating purpose, public interface, and non-responsibilities. See [Engineering_Constitution.md §3](file:///Users/anzarakhtar/aios/Engineering_Constitution.md).
* Every public function has a docstring covering purpose, inputs, outputs, and failure modes. See [Engineering_Constitution.md §10](file:///Users/anzarakhtar/aios/Engineering_Constitution.md).
* Documentation is updated in the same commit as the code it describes — never as a follow-up. See [Engineering_Constitution.md §10](file:///Users/anzarakhtar/aios/Engineering_Constitution.md).

### Violation Signal

A PR that adds a new service, module, or skill without a corresponding README, updated `AI_CONTEXT.md`, or docstrings on public functions.

---

## DG-10: Reversibility

> *Every state-mutating operation must either be atomic and self-reverting on failure, or provide a documented manual recovery path.*

### What This Means

The system touches filesystems, git histories, and database records. If any operation fails mid-execution, the system must not leave the user's environment in a partially-modified state. Rollback is not a feature — it is a design constraint.

### Measurable Criterion

**For every HIGH and MEDIUM risk action executed by the Action Engine, a pre-execution backup exists in a known, documented location, and the rollback procedure for that action is tested in the regression suite.**

### Architecture Enforcement

* Action Engine caches file contents before writes, enabling per-step rollback. See [16_ENGINEERING_BIBLE.md §4.5](file:///Users/anzarakhtar/aios/docs/16_ENGINEERING_BIBLE.md).
* Database migrations are versioned and include a down-migration script.
* AI agents must not leave the system in a broken or partially-migrated state at session end. See [Engineering_Constitution.md §17](file:///Users/anzarakhtar/aios/Engineering_Constitution.md).

### Violation Signal

A multi-step mutating operation with no rollback path and no backup of the pre-operation state.

---

## Design Goal Verification Checklist

When introducing a new service, interface, or subsystem, verify:

- [ ] DG-01: Can this component be deleted and replaced without touching other files? (**Replaceability**)
- [ ] DG-02: Does this component function correctly with `offline_mode = True`? (**Local-First**)
- [ ] DG-03: Does this component add any unconstrained I/O to the critical boot or command path? (**Responsiveness**)
- [ ] DG-04: Are all personal data flows documented in an ADR and reviewed against the Privacy Gate? (**Data Boundaries**)
- [ ] DG-05: Does this component touch memory tier logic, and if so, are the tier contracts verified in tests? (**Memory Integrity**)
- [ ] DG-06: Are all error paths handled with explicit recovery or re-raise? (**Zero Silent Failures**)
- [ ] DG-07: Do all HIGH-risk operations gate on explicit human confirmation? (**Human-Gated Actions**)
- [ ] DG-08: Does this component introduce any multi-tenant concept or user management model? (**Single-User**)
- [ ] DG-09: Is there a README, updated AI_CONTEXT.md, and docstrings for all public surfaces? (**Orientability**)
- [ ] DG-10: Is there a documented rollback path for every state mutation this component performs? (**Reversibility**)

---

*Design Goals · Engineering Bible Foundation · Sprint 8 M1 · Governed by [00_PROJECT_VISION.md §5](file:///Users/anzarakhtar/aios/docs/00_PROJECT_VISION.md) and [02_ARCHITECTURE_GUIDELINES.md](file:///Users/anzarakhtar/aios/docs/02_ARCHITECTURE_GUIDELINES.md)*
