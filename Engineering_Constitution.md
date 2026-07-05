# Engineering Constitution
### Personal AI OS — Version 1.0

*This document defines HOW the Personal AI OS is built. It governs every coding session, every AI-assisted contribution, and every line of code that enters the system. Where the Constitutional Document defines what the system is for, this document defines the discipline that keeps it buildable, maintainable, and trustworthy for ten years.*

*Derived from and subordinate to the Personal AI OS Constitution. Where a rule here appears to conflict with a Guiding Principle (Simple, Minimal, Fast, Modular, Extensible, Private, Secure, Personal, Intelligent, Helpful, Honest), the Guiding Principle wins.*

---

## 1. Engineering Principles

| Principle | Rule | Reason |
|---|---|---|
| Boring by default | Choose the most proven, widely-documented technology over the newest one. | A one-person system has no team to absorb the risk of exotic tooling; boring tech is well-documented, which matters most when the primary contributor is an AI. |
| Optimize for deletion | Every module must be easy to delete and replace, not just easy to add to. | The Constitution treats today's best model as tomorrow's second-best — code must assume its dependencies are temporary. |
| One reason to change | Each file, function, or module should have exactly one responsibility. | Mixed responsibilities are the single biggest cause of AI-introduced regressions, because a change made for one reason silently breaks another. |
| Working software over perfect architecture | Ship the simplest version that works, then refactor under real usage. | This is a system for one user, evolving over a decade — premature architecture is wasted effort that will be wrong anyway. |
| No speculative generality | Do not build for a future requirement that doesn't exist yet. | Matches the Minimal principle directly: features and abstractions must earn their existence, not be pre-built "just in case." |

---

## 2. Project Structure Rules

- **One repository per skill category**, plus one core/orchestration repository. Never one monolithic repo, never a repo per feature.
  *Reason: Skill categories are the system's real unit of modularity (Section 08 of the Constitution) — the repo boundary should match that, not the feature-of-the-week boundary.*
- **Flat over nested.** No folder should be more than 3 levels deep from the repo root.
  *Reason: Deep nesting slows down both human and AI navigation and is a common source of import errors.*
- **Standard skeleton in every repo**: `src/`, `tests/`, `docs/`, `config/`, `scripts/`. No repo invents its own layout.
  *Reason: A predictable skeleton lets an AI coding agent orient itself in seconds without exploring the whole tree.*
- **Config is never hardcoded.** All environment-specific values live in `config/` or environment variables, never inline in source.
  *Reason: Supports the Private and Secure principles — secrets and environment specifics must never be committed alongside logic.*
- **No file exceeds 400 lines.** Split before you hit the limit, not after.
  *Reason: Long files are where AI-assisted edits most often lose context and introduce silent bugs.*

---

## 3. Module Design Rules

- **Every module exposes a single public interface** (a defined set of functions/classes) and hides its internals. Nothing outside the module reaches into its internals directly.
  *Reason: This is what makes a module actually replaceable — the Modular principle is meaningless if callers depend on internal details.*
- **Modules communicate through contracts, not shared state.** Pass data explicitly; do not rely on global variables or implicit shared memory.
  *Reason: Implicit coupling is invisible until it breaks, and it breaks exactly when you try to swap a component.*
- **AI-model access is always behind an adapter interface**, never called directly from business logic.
  *Reason: Directly ties to the Constitution's "today's best model is tomorrow's second-best" — swapping models must be a one-file change.*
- **No module may depend on a "sibling" module's internals to avoid a shared dependency.** Extract the shared logic into its own module instead.
  *Reason: This shortcut is how tangled dependency graphs are born; untangling later costs far more than doing it right once.*
- **Every module has a one-paragraph README stating its purpose, its public interface, and what it explicitly does not do.**
  *Reason: The "does not do" line prevents scope creep and gives an AI agent a hard boundary before it starts editing.*

---

## 4. Dependency Rules

- **New dependencies require a one-line justification recorded in `docs/decisions/`** — what problem it solves and what was considered instead.
  *Reason: Cheap dependencies compound into an unmaintainable tree; a paper trail forces the "does this justify its existence" question the Constitution demands of all new capability.*
- **Prefer the standard library over a package, and a small package over a framework.**
  *Reason: Fewer dependencies means fewer breaking upgrades and a smaller attack surface — directly serving the Secure principle.*
- **Pin exact versions in production; never use floating version ranges (`^`, `~`, `latest`).**
  *Reason: A system meant to run unattended for a decade cannot tolerate a silent upstream change breaking it overnight.*
- **No dependency with unmaintained status (no commits/releases in 18+ months) is added.** Existing ones are flagged for replacement.
  *Reason: An abandoned dependency is an unpatched vulnerability waiting to happen.*
- **Third-party services that touch personal data require explicit sign-off before integration**, logged in `docs/decisions/`.
  *Reason: Privacy is non-negotiable per the Constitution; every external data path must be a deliberate, documented decision, not a side effect of adding a package.*

---

## 5. Naming Conventions

- **Names describe intent, not implementation.** `getActiveProjects()` not `queryProjectsTable()`.
  *Reason: Implementation details change; intent doesn't — names should survive refactors.*
- **One casing convention per language, applied without exception**: `snake_case` for Python, `camelCase` for JS/TS variables and functions, `PascalCase` for classes/types/components.
  *Reason: Consistency removes an entire category of nitpick and lets an AI agent predict names correctly instead of guessing.*
- **Booleans are questions**: `isReady`, `hasMemoryEntry`, `canRetry` — never `flag`, `status`, or `check`.
  *Reason: A boolean name should make the calling code read like a sentence, eliminating ambiguity about polarity.*
- **No abbreviations except universally known ones** (`id`, `url`, `config`). Spell out everything else.
  *Reason: Abbreviations save the writer seconds and cost every future reader (human or AI) far more in ambiguity.*
- **File names match their primary export.** A file exporting `MemoryStore` is named `memory_store.py` / `MemoryStore.ts`, not `utils.py`.
  *Reason: This is what makes the codebase navigable by filename alone, which matters most when an AI agent is searching for the right place to make a change.*

---

## 6. Code Quality Standards

- **A linter and formatter run on every commit, with zero manually-overridden rules.**
  *Reason: Style debates cost time that should go toward substance; automation removes the debate entirely.*
- **Cyclomatic complexity per function capped at 10.** If a function exceeds it, extract sub-functions.
  *Reason: High-complexity functions are exactly where bugs hide and where AI-generated patches are most likely to introduce a regression.*
- **No function takes more than 4 parameters.** Beyond that, pass a single structured object.
  *Reason: Long parameter lists are a proxy for a function doing too much, and they invite argument-order mistakes.*
- **Dead code is deleted, never commented out.** Version control is the archive, not the file.
  *Reason: Commented-out code silently accumulates and is routinely misread as intentional by both humans and AI.*
- **No magic numbers or strings.** Every literal with meaning is a named constant.
  *Reason: Magic values are a leading cause of subtle, hard-to-trace bugs, and they carry no explanation for why that value was chosen.*

---

## 7. Error Handling

- **Fail loudly in development, fail safely in production.** Never silently swallow an exception in either environment.
  *Reason: A system that hides its own failures cannot be trusted — this is a direct extension of the Honest principle applied to the code itself.*
- **Every error caught must either be handled meaningfully or re-raised with added context.** No empty `catch`/`except` blocks.
  *Reason: An empty catch block is where real problems go to disappear until they resurface somewhere unrelated and unrecognizable.*
- **User-facing errors are plain language; internal errors carry full technical detail in logs.** Never show a stack trace to the user, never omit one from the log.
  *Reason: Keeps the interaction honest and direct per the Constitution's personality rules, while preserving everything needed to actually debug the issue.*
- **Expected failure states (e.g., no network, no API key) are modeled explicitly, not treated as exceptions.**
  *Reason: Using exceptions for expected conditions makes control flow unpredictable and harder to reason about than an explicit result type or status check.*
- **Every external call (API, database, filesystem) has an explicit timeout and a defined fallback behavior.**
  *Reason: Directly serves the Fast principle — one hanging dependency should never be able to freeze the whole system.*

---

## 8. Logging

- **Every log line answers: what happened, where, and with what data.** No bare `"error occurred"` messages.
  *Reason: A log that can't reconstruct what happened is worse than no log — it creates false confidence that the system is observable.*
- **Log levels are used strictly**: `DEBUG` for development detail, `INFO` for normal operation milestones, `WARN` for recoverable issues, `ERROR` for failures needing attention.
  *Reason: Consistent levels let future-you filter signal from noise instantly instead of re-reading every line.*
- **No personal data appears in logs in plaintext** — hash, redact, or reference by ID instead.
  *Reason: Logs are often the least-protected part of a system; this is where the Private principle is most easily and invisibly violated.*
- **Logs are structured (JSON or key-value), never free-form sentences.**
  *Reason: Structured logs can be queried and monitored programmatically; free-form text can only be read, one line at a time, by a human.*
- **Every scheduled or automated job logs a start and an end, even on success.**
  *Reason: Silence is indistinguishable from failure in an unattended system — an explicit "completed" line is the only way to know nothing quietly broke.*

---

## 9. Testing Strategy

- **Every module ships with unit tests covering its public interface before it is considered done.** No exceptions for "small" changes.
  *Reason: In an AI-assisted codebase, tests are the primary safety net catching regressions a human reviewer might not have time to trace manually.*
- **Test the contract, not the implementation.** Tests must survive an internal refactor that doesn't change behavior.
  *Reason: Implementation-coupled tests actively punish the Modular principle by breaking every time a component is legitimately swapped.*
- **Integration tests cover every module boundary where two independently-replaceable components meet.**
  *Reason: This is precisely where "swap the AI model" or "swap the database" failures happen — unit tests alone won't catch them.*
- **No PR merges with failing tests or reduced coverage on touched files.** This applies equally to AI-generated changes.
  *Reason: An AI agent under instruction to "make it work" will otherwise be tempted to skip or weaken tests rather than fix the underlying issue.*
- **Critical paths (memory storage, privacy boundaries, model-adapter swap) require regression tests that run on every commit, not just on release.**
  *Reason: These are the paths where a silent failure would violate the Constitution's non-negotiable guarantees (privacy, trust) rather than just cause an inconvenience.*

---

## 10. Documentation Standards

- **Every module has a README; every public function has a docstring stating purpose, inputs, outputs, and failure modes.**
  *Reason: Documentation is what lets an AI coding agent operate on a module correctly without re-deriving its intent from scratch each session.*
- **Architecture decisions are recorded where they're made** (`docs/decisions/NNNN-title.md`), not left to be inferred from code.
  *Reason: Ten years from now, the code will explain "what"; only a decision record explains "why," and "why" is what prevents repeating past mistakes.*
- **Documentation is updated in the same commit as the code it describes.** A PR that changes behavior without touching docs is incomplete.
  *Reason: Documentation that lags the code becomes actively misleading, which is worse than no documentation at all.*
- **No documentation duplicates what the code already makes obvious.** Document intent and tradeoffs, not restated syntax.
  *Reason: Matches the Minimal principle — documentation is a maintenance burden too, and should earn its place like any other artifact.*
- **The root of each repository has a single onboarding doc** answering: what this is, how to run it, how to test it, where to look next.
  *Reason: Every new coding session — human or AI — should be able to get oriented from one file in under a minute.*

---

## 11. Git Workflow

- **`main` is always deployable.** All work happens on short-lived feature branches merged via pull request.
  *Reason: A system relied on daily cannot tolerate a broken main branch, even temporarily.*
- **One logical change per commit; one logical feature per branch.** No "misc fixes" commits.
  *Reason: Small, focused commits are what make `git bisect` and history review actually useful when something breaks months later.*
- **Commit messages follow Conventional Commits** (`feat:`, `fix:`, `refactor:`, `docs:`, `test:`, `chore:`).
  *Reason: A consistent format enables automated changelog generation and lets you scan history by category instantly.*
- **Every branch is deleted immediately after merge.**
  *Reason: Stale branches accumulate as clutter and create ambiguity about which line of work is still active — a small but real violation of Minimal.*
- **AI-authored commits are marked as such in the commit trailer** (e.g., `Co-authored-by: AI-agent`).
  *Reason: The Constitution demands the system never become a black box — knowing which changes were AI-generated preserves that transparency in the history itself.*

---

## 12. Versioning

- **Semantic Versioning (`MAJOR.MINOR.PATCH`) applies to every repository, including internal libraries.**
  *Reason: A predictable versioning scheme is what makes safe upgrades possible across a decade of dependency changes.*
- **Breaking a module's public interface always requires a MAJOR bump, even in a single-user system.**
  *Reason: Discipline here isn't for external consumers — it's what keeps you honest about the actual blast radius of a change before you make it.*
- **Every release has a changelog entry written in plain language, not generated commit-message noise.**
  *Reason: A future you, reviewing a decade of history, needs "why this mattered," not a raw commit dump.*
- **The core orchestration layer and each skill category version independently.**
  *Reason: Directly enforces Modular and Extensible — a skill category should be upgradeable without forcing a release of everything else.*
- **Deprecated interfaces are marked and kept functional for at least one MINOR version before removal.**
  *Reason: Even a one-person system benefits from a grace period — it prevents an AI agent's in-flight change from being broken by an unrelated same-day removal.*

---

## 13. Security Standards

- **No secret, API key, or credential is ever committed to version control**, including in history. Use a secrets manager or environment variables exclusively.
  *Reason: This is the single highest-leverage rule under the Secure principle — one leaked credential can compromise a system that knows everything about its owner.*
- **All personal data is encrypted at rest and in transit, with no exceptions for "internal-only" storage.**
  *Reason: The Constitution assumes the system will eventually be targeted; encryption is the baseline, not a hardening step for later.*
- **Every external-facing interface authenticates every request. There is no "trusted internal network" assumption.**
  *Reason: Zero-trust is cheap to build in from day one and expensive to retrofit after a breach.*
- **Dependencies are scanned for known vulnerabilities on every build; a critical vulnerability blocks merge.**
  *Reason: Most real-world breaches come through outdated dependencies, not novel exploits — this closes the cheapest attack vector automatically.*
- **Any component that could exfiltrate personal data to a third party (including AI model providers) is explicitly flagged, documented, and requires deliberate opt-in.**
  *Reason: Directly operationalizes the Private principle — data must never leave the system's control by default or by accident.*

---

## 14. AI Coding Rules

*Rules for any AI agent (including Claude) contributing code to this system.*

- **The AI always states its assumptions before writing code when a request is ambiguous**, then proceeds with a clearly labeled default rather than stalling.
  *Reason: Mirrors the Constitution's Decision-Making Philosophy — one precise clarification is worth more than silent guessing or excessive interrogation.*
- **The AI never introduces a new dependency, architectural pattern, or external service without flagging it explicitly in its output**, even if it "seemed like the right tool."
  *Reason: Silent scope expansion is how a Minimal system quietly becomes bloated — every addition must be visible and approvable.*
- **The AI treats existing conventions in the codebase as binding**, even if it would personally choose differently, unless explicitly asked to change them.
  *Reason: Consistency across a decade of contributions — many by different AI sessions with no shared memory — depends entirely on respecting what's already there.*
- **The AI writes tests for any new logic in the same turn it writes the logic, not as a follow-up.**
  *Reason: Deferred testing is testing that doesn't happen; this rule closes the gap where AI-assisted velocity most commonly trades away correctness.*
- **The AI explains *why* a change was made, not just *what* changed**, in commit messages, PR descriptions, and code comments for non-obvious logic.
  *Reason: This is the Honest principle applied to the AI's own output — future sessions (human or AI) need the reasoning trail, not just the diff.*

---

## 15. Refactoring Rules

- **Refactor in dedicated commits/PRs, never mixed with a feature or bug fix.**
  *Reason: Mixing the two makes it impossible to review either change cleanly or to revert one without the other.*
- **A refactor must not change observable behavior.** If behavior needs to change, that's a feature, not a refactor — label it accordingly.
  *Reason: Blurring this line is how "just a refactor" quietly ships regressions with no one looking for them.*
- **Refactor when a module's tests become hard to write, not on a schedule.** Difficulty testing is the signal that a design has drifted.
  *Reason: This gives a concrete, objective trigger instead of vague "code smell" judgment calls that vary session to session.*
- **Never rewrite a module from scratch while it's still relied on elsewhere.** Refactor incrementally behind its existing interface.
  *Reason: Big-bang rewrites are the highest-risk way to introduce regressions in a system with no team to catch them quickly.*
- **Every refactor preserves or improves test coverage — it never reduces it, even temporarily.**
  *Reason: A refactor is exactly when the safety net matters most; weakening it during the riskiest kind of change defeats its purpose.*

---

## 16. Definition of Done

A change is **done** only when all of the following are true:

1. It compiles/runs with no errors or warnings.
2. It has unit tests covering its logic, and all tests pass.
3. Documentation (docstrings, README, decision record if applicable) is updated in the same commit.
4. It follows every naming, structure, and quality rule in this document.
5. It has been reviewed for privacy and security impact per Sections 4 and 13.
6. The commit message and PR description explain *why*, not just *what*.
7. It does not reduce test coverage or leave dead code behind.

*Reason: A single, explicit checklist removes ambiguity about "finished" — critical when contributions come from many disconnected AI sessions with no shared memory of what "usually" counts as complete.*

---

## 17. Things AI Must Never Do

- **Never commit secrets, credentials, or personal data to version control**, under any framing, including "temporary" or "for testing."
- **Never disable, weaken, or skip a test to make a build pass.** Fix the underlying issue or flag it explicitly instead.
- **Never introduce a new external service or data flow that sends personal data off-system without explicit, documented approval.**
- **Never silently change established naming, structure, or architectural conventions** without flagging the change and the reason.
- **Never claim a change is tested, reviewed, or complete when it is not.** State uncertainty plainly instead of implying confidence.
- **Never delete or overwrite existing data-handling logic (memory storage, privacy boundaries) without an explicit, separate confirmation step.**
- **Never optimize for looking productive (large diffs, many files touched) over solving the actual problem simply.**
- **Never leave a system in a broken or partially-migrated state at the end of a session** — either finish the change or revert it.

*Reason: These are the non-negotiable failure modes — the engineering equivalent of the Constitution's "What This AI OS Should Never Become." Violating any one of them doesn't just introduce a bug; it breaks the trust the entire system depends on.*

---

*Engineering Constitution · Version 1.0 · Subordinate to and derived from the Personal AI OS Constitution*
