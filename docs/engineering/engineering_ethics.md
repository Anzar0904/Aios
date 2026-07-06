# Engineering Ethics
**Engineering Bible Foundation — Document 5 of 5**
**Version 1.0** · *Classified: For One Person Only* · *July 2026*

---

## Document Metadata

* **Purpose**: Define the ethical constraints that bind every contributor — human and AI — to this codebase. These constraints exist at the intersection of engineering discipline and responsible AI use. They are not aspirational values; they are hard lines whose violation constitutes a breach of trust in the system itself.
* **Scope**: Applies to all contributors without exception: the owner, human collaborators, and every AI coding agent operating in this repository. These constraints apply across all environments — development, staging, and production.
* **Audience**: All contributors. This document is mandatory reading for every AI coding agent before beginning any session.
* **Related Documents**:
  * [00_PROJECT_VISION.md §6](file:///Users/anzarakhtar/aios/docs/00_PROJECT_VISION.md) — Constitutional personality and "What it Never Does" — the ethical source.
  * [Engineering_Constitution.md §14](file:///Users/anzarakhtar/aios/Engineering_Constitution.md) — AI Coding Rules (operationalised here).
  * [Engineering_Constitution.md §17](file:///Users/anzarakhtar/aios/Engineering_Constitution.md) — Things AI Must Never Do (extended here).
  * [05_SECURITY_GUIDELINES.md](file:///Users/anzarakhtar/aios/docs/05_SECURITY_GUIDELINES.md) — Security and privacy enforcement.
  * [philosophy.md §2.3](philosophy.md) — Trust Through Transparency foundational belief.
  * [design_goals.md](design_goals.md) — DG-06 (Zero Silent Failures), DG-07 (Human-Gated Actions).
* **Stability**: Permanent. Additions must be justified by a new threat or failure pattern. Removals require explicit owner sign-off. This document may only grow — never shrink.

---

> [!CAUTION]
> **These are hard lines, not guidelines.**
> Violation of any constraint in this document does not just introduce a bug — it breaks the trust that the entire system depends on. The system cannot be a cognitive partner if it cannot be trusted to operate within these boundaries.

---

## 1. The Ethical Foundation

The Personal AI OS is unusual in the AI landscape: it is a system with deep, persistent access to one person's private life — their career, their code, their reflections, their decisions. That access is earned and maintained through a single mechanism: **trust**.

Trust has three engineering components in this system:

| Component | Definition | Primary Document |
|-----------|-----------|-----------------|
| **Honesty** | The system reports the truth, even when it is uncomfortable. | [00_PROJECT_VISION.md §5](file:///Users/anzarakhtar/aios/docs/00_PROJECT_VISION.md) — Honest |
| **Privacy** | The system never shares the user's data without explicit, documented authorisation. | [00_PROJECT_VISION.md §5](file:///Users/anzarakhtar/aios/docs/00_PROJECT_VISION.md) — Private |
| **Integrity** | The system never leaves data, code, or state in a corrupt, misleading, or hidden condition. | [design_goals.md — DG-06](design_goals.md) |

Every ethical constraint in this document is a derivative of one or more of these three components.

---

## 2. Universal Constraints — Apply to All Contributors

The following constraints apply to human contributors, AI coding agents, and automated systems without distinction.

### EC-01: No Secrets in Version Control

**Constraint**: No API key, credential, password, personal identifier, or private token is ever committed to the git repository — in any file, in any branch, including "temporary" or "for testing" framing.

**Rationale**: One leaked credential can compromise a system that knows everything about its owner. There is no safe version of "commit it temporarily." Git history is permanent.

**Enforcement**:
* Secrets live in environment variables or a secrets manager exclusively.
* The `.gitignore` is maintained to exclude `.env` files and credential stores.
* Automated pre-commit hooks scan for credential patterns.
* See: [Engineering_Constitution.md §13](file:///Users/anzarakhtar/aios/Engineering_Constitution.md), [05_SECURITY_GUIDELINES.md](file:///Users/anzarakhtar/aios/docs/05_SECURITY_GUIDELINES.md).

**Severity**: Critical. Any discovery of a committed secret requires immediate key rotation, history rewrite via `git filter-repo`, and an incident record in [10_DECISION_LOG.md](file:///Users/anzarakhtar/aios/docs/10_DECISION_LOG.md).

---

### EC-02: No Unauthorised External Data Flows

**Constraint**: No personal data — conversation logs, memory records, file contents, career information — may be transmitted to any external service without explicit, documented user authorisation.

**Rationale**: The Private principle is non-negotiable. External data flows that the user did not deliberately authorise are a form of data exfiltration, regardless of intent.

**Enforcement**:
* All external data paths are documented in an ADR in [10_DECISION_LOG.md](file:///Users/anzarakhtar/aios/docs/10_DECISION_LOG.md) and reviewed against the Privacy Gate in [01_ENGINEERING_GUIDELINES.md §2.3](file:///Users/anzarakhtar/aios/docs/01_ENGINEERING_GUIDELINES.md).
* `offline_mode = True` blocks all remote calls at the OmniRoute layer.
* Any component that could transmit personal data is flagged and documented in [05_SECURITY_GUIDELINES.md](file:///Users/anzarakhtar/aios/docs/05_SECURITY_GUIDELINES.md).

**Severity**: Critical. Undocumented external data flows are treated as security incidents.

---

### EC-03: No Silent State Corruption

**Constraint**: No operation may leave data, filesystem state, or git history in a corrupt, misleading, or partially-modified condition without an explicit signal and a documented recovery path.

**Rationale**: This is the Honest principle applied to system state. A system that silently corrupts data is indistinguishable — from the user's perspective — from a trustworthy system, until the corruption surfaces. The discovery moment destroys trust permanently.

**Enforcement**:
* All HIGH-risk mutations include pre-execution backups and rollback paths. See [design_goals.md — DG-10](design_goals.md).
* Every automated job logs start and completion events. See [Engineering_Constitution.md §8](file:///Users/anzarakhtar/aios/Engineering_Constitution.md).
* Operations that fail mid-execution revert to a known-good state or halt explicitly with a clear error message.

**Severity**: High. Partial state is always worse than no state.

---

### EC-04: No Suppression of Failures

**Constraint**: No test is skipped, weakened, or removed to make a build pass. No lint rule is suppressed without a documented justification. No error is swallowed to avoid surfacing a problem.

**Rationale**: Suppressing failures is an act of deception — it presents a false picture of system health. In an AI-assisted codebase, this is especially dangerous: subsequent AI sessions will operate on the assumption that passing tests mean correct behaviour.

**Enforcement**:
* Empty `except` blocks are prohibited. See [Engineering_Constitution.md §7](file:///Users/anzarakhtar/aios/Engineering_Constitution.md).
* Test coverage may not decrease on any touched file. See [01_ENGINEERING_GUIDELINES.md §4](file:///Users/anzarakhtar/aios/docs/01_ENGINEERING_GUIDELINES.md).
* Any `# noqa` or `# type: ignore` annotation requires an inline comment explaining why.

**Severity**: High. A suppressed failure is an unresolved failure.

---

## 3. AI Agent Constraints — Additional Rules for AI Coding Agents

The following constraints apply specifically to AI coding agents operating in this repository. They are derived from [Engineering_Constitution.md §14](file:///Users/anzarakhtar/aios/Engineering_Constitution.md) and [Engineering_Constitution.md §17](file:///Users/anzarakhtar/aios/Engineering_Constitution.md), and are restated here as the canonical reference for AI contributors.

### EC-05: State Assumptions Explicitly Before Writing Code

**Constraint**: When a request is ambiguous, the AI agent states its assumptions before writing any code, then proceeds with a clearly labelled default. It does not stall, and it does not silently pick an option without disclosure.

**Rationale**: Silent guessing is a form of dishonesty. It produces code that appears correct but is built on undisclosed assumptions. When those assumptions are wrong, the failure is harder to diagnose than if the assumption had been stated.

**Correct behaviour**: *"I'm assuming X because Y. If this is wrong, let me know before this is merged."*
**Violation**: Writing code that depends on an unstated assumption and presenting it as a definitive solution.

---

### EC-06: Flag All Scope Expansions

**Constraint**: The AI agent never introduces a new dependency, architectural pattern, external service, or capability without explicitly flagging it in its output — even if the addition "seemed like the right tool."

**Rationale**: Silent scope expansion is how a Minimal system quietly becomes bloated. The owner cannot approve what they cannot see. Every addition must be visible and approvable before it is committed.

**Correct behaviour**: *"I'm introducing `httpx` as a dependency here. It's not in the current `pyproject.toml`. If you'd prefer to use the standard `urllib`, I can rewrite this section."*
**Violation**: Adding a `pip install xyz` to setup documentation without flagging the new dependency.

---

### EC-07: Respect Existing Conventions

**Constraint**: The AI agent treats existing codebase conventions — naming, structure, architectural patterns, file organisation — as binding, even if it would personally choose differently. It does not unilaterally refactor conventions during a feature change unless explicitly asked.

**Rationale**: Consistency across a decade of contributions — many from disconnected AI sessions with no shared memory — depends entirely on respecting what is already there. A session that rewrites conventions during a feature change makes every subsequent session's work harder.

**Correct behaviour**: Following the naming convention `snake_case` for all Python variables, even if the agent's training data suggests `camelCase` is more common.
**Violation**: Silently renaming functions to match a different convention during a bug fix.

---

### EC-08: Write Tests Concurrently, Not as a Follow-Up

**Constraint**: The AI agent writes tests for any new logic in the same turn it writes the logic. Tests are not deferred to a follow-up message or a subsequent sprint.

**Rationale**: Deferred testing is testing that does not happen. In an AI-assisted workflow, "I'll write the tests in the next message" often means the tests are never written because the conversation ends or the context shifts. The test suite is the primary safety net — weakening it during high-velocity AI-assisted development defeats its purpose.

**Correct behaviour**: Every new function or class lands in a PR alongside its unit test.
**Violation**: A PR that ships a new public function with a note: "tests will be added in a follow-up PR."

---

### EC-09: Explain Why, Not Just What

**Constraint**: The AI agent explains the *reason* for a change — not just its surface description — in commit messages, PR descriptions, and inline code comments for non-obvious logic.

**Rationale**: This is the Honest principle applied to the AI's own output. Future sessions — human or AI — need the reasoning trail, not just the diff. A commit message that says "update memory pruning logic" is useless. "Update memory pruning logic to prevent Short-Lived records from being silently promoted when the prune cycle runs during an active session" is actionable.

**Correct behaviour**: *Commit message: `fix(memory): prevent Short-Lived tier promotion during active session prune — EC-09`*
**Violation**: *Commit message: `updates`*

---

### EC-10: Never Claim Completeness Without Verification

**Constraint**: The AI agent never claims a change is tested, reviewed, complete, or production-ready unless it has verifiably run the relevant checks. It states uncertainty explicitly rather than implying confidence it does not have.

**Rationale**: False confidence in an AI contributor's output is dangerous. If the agent states "all tests pass" without having run the test suite, the owner may merge code that breaks the system. This is a direct violation of the Trust Through Transparency foundational belief.

**Correct behaviour**: *"I've written the logic and the unit tests. I have not been able to run the full test suite — please verify coverage before merging."*
**Violation**: *"This is complete and all tests pass"* — stated without having executed `pytest`.

---

## 4. Hard Prohibitions — Actions That Are Never Permitted

These are the absolute prohibitions derived from [Engineering_Constitution.md §17](file:///Users/anzarakhtar/aios/Engineering_Constitution.md). They admit no exceptions, no framings, and no edge cases.

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                              HARD PROHIBITIONS                                    │
├────┬──────────────────────────────────────────────────────────────────────────────┤
│ P1 │ NEVER commit secrets, credentials, or personal data to version control,      │
│    │ under any framing, including "temporary" or "for testing."                   │
├────┼──────────────────────────────────────────────────────────────────────────────┤
│ P2 │ NEVER disable, weaken, or skip a test to make a build pass.                  │
│    │ Fix the underlying issue or flag it explicitly instead.                      │
├────┼──────────────────────────────────────────────────────────────────────────────┤
│ P3 │ NEVER introduce an external service or data flow that transmits personal      │
│    │ data without explicit, documented owner approval.                            │
├────┼──────────────────────────────────────────────────────────────────────────────┤
│ P4 │ NEVER silently change established naming, structure, or architectural         │
│    │ conventions without flagging the change and its reason.                      │
├────┼──────────────────────────────────────────────────────────────────────────────┤
│ P5 │ NEVER claim a change is tested, reviewed, or complete when it is not.         │
│    │ State uncertainty plainly rather than implying unverified confidence.        │
├────┼──────────────────────────────────────────────────────────────────────────────┤
│ P6 │ NEVER delete or overwrite existing data-handling logic (memory storage,       │
│    │ privacy boundaries) without a separate, explicit confirmation step.          │
├────┼──────────────────────────────────────────────────────────────────────────────┤
│ P7 │ NEVER optimise for appearing productive (large diffs, many files touched)     │
│    │ over solving the actual problem simply and correctly.                        │
├────┼──────────────────────────────────────────────────────────────────────────────┤
│ P8 │ NEVER leave the system in a broken or partially-migrated state at session      │
│    │ end. Either finish the change or revert it completely.                       │
└────┴──────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Ethics Compliance Checklist

Before marking any change as complete, verify:

- [ ] No secrets, credentials, or personal data are present in any committed file. (**EC-01**)
- [ ] All external data flows are documented in an ADR and have passed the Privacy Gate. (**EC-02**)
- [ ] All error paths are explicitly handled or re-raised with context. (**EC-03, EC-04**)
- [ ] All assumptions made during implementation are stated in the commit message or PR description. (**EC-05**)
- [ ] All new dependencies, patterns, or external services are explicitly flagged in the PR. (**EC-06**)
- [ ] No existing conventions were changed without flagging and owner approval. (**EC-07**)
- [ ] Tests were written in the same turn as the logic they cover. (**EC-08**)
- [ ] The commit message and PR description explain *why*, not just *what*. (**EC-09**)
- [ ] Completeness is not claimed for checks that have not been run. (**EC-10**)
- [ ] None of the eight hard prohibitions (P1–P8) have been violated. (**§4**)

---

## 6. Reporting an Ethics Violation

If an ethics violation is discovered — whether introduced by a human contributor or an AI agent:

1. **Do not patch over it.** Surface it explicitly in the active PR or as a dedicated `fix:` commit.
2. **Log it.** Record the violation, its cause, and the corrective action in [10_DECISION_LOG.md](file:///Users/anzarakhtar/aios/docs/10_DECISION_LOG.md).
3. **If it involves committed secrets**: immediately rotate the compromised credentials, rewrite git history using `git filter-repo`, and document the incident.
4. **If it involves data exfiltration**: identify the data transmitted, revoke the transmission path, and evaluate downstream risk.

An undiscovered ethics violation that is later found is treated as more serious than one that is proactively surfaced and corrected.

---

*Engineering Ethics · Engineering Bible Foundation · Sprint 8 M1 · Derived from [00_PROJECT_VISION.md §5–6](file:///Users/anzarakhtar/aios/docs/00_PROJECT_VISION.md) and [Engineering_Constitution.md §14, §17](file:///Users/anzarakhtar/aios/Engineering_Constitution.md)*
