# 01 — Engineering Guidelines
**Version 1.0** · *Classified: For One Person Only* · *July 2026*

---

## Document Metadata
* **Purpose**: Define the core engineering philosophy, software development lifecycle (SDLC), dependency management, and refactoring standards for the Personal AI OS. It translates the constitutional vision into day-to-day developer and AI agent constraints.
* **Scope**: Governs all codebase contributions, code updates, dependencies integration, and refactoring practices inside the `core/` and `skills/` monorepo workspaces.
* **Audience**: Lead Software Engineers, Technical Architects, and AI Coding Agents contributing code to the system.
* **Related Documents**:
  * [00_PROJECT_VISION.md](file:///Users/anzarakhtar/aios/docs/00_PROJECT_VISION.md) - The constitutional root of the project.
  * [02_ARCHITECTURE_GUIDELINES.md](file:///Users/anzarakhtar/aios/docs/02_ARCHITECTURE_GUIDELINES.md) - Kernel/Service boundaries and contract design patterns.
  * [04_CODING_STANDARDS.md](file:///Users/anzarakhtar/aios/docs/04_CODING_STANDARDS.md) - Exact syntax, complexity, and file size formatting guidelines.
  * [05_SECURITY_GUIDELINES.md](file:///Users/anzarakhtar/aios/docs/05_SECURITY_GUIDELINES.md) - Security classifications, credentials, and data privacy gates.
  * [06_TESTING_GUIDELINES.md](file:///Users/anzarakhtar/aios/docs/06_TESTING_GUIDELINES.md) - Pytest fixtures, test hierarchies, and quality gates.
  * [10_DECISION_LOG.md](file:///Users/anzarakhtar/aios/docs/10_DECISION_LOG.md) - History and template log for Architectural Decision Records (ADRs).
  * [16_ENGINEERING_BIBLE.md](file:///Users/anzarakhtar/aios/docs/16_ENGINEERING_BIBLE.md) - Technical implementation details and REPL execution flow.
* **Future Extensions**: This document will be expanded to detail continuous integration/continuous deployment (CI/CD) automated testing checks as repository hooks are implemented.

---

## 1. Core Engineering Principles

These principles represent the operational discipline of the project. They are designed to prevent structural decay in a system where the primary developer is an AI coding agent operating across disconnected chat sessions.

```
+-----------------------------------------------------------------------------------+
|                            ENGINEERING PRINCIPLE MATRIX                           |
+------------------------------------+----------------------------------------------+
| Principle                          | Operational Rule                             |
+------------------------------------+----------------------------------------------+
| Boring by Default                  | Prioritize standard libraries and stable,    |
|                                    | well-documented technologies.                |
+------------------------------------+----------------------------------------------+
| Optimize for Deletion              | Write self-contained modules that can be     |
|                                    | removed with zero collateral breakage.       |
+------------------------------------+----------------------------------------------+
| One Reason to Change (SRP)         | Isolate files and classes around a single    |
|                                    | clear technical responsibility.              |
+------------------------------------+----------------------------------------------+
| Working Software Over Perfection   | Ship simple, functional code first, then    |
|                                    | iterate based on usage, not anticipation.     |
+------------------------------------+----------------------------------------------+
| No Speculative Generality          | Ban abstractions designed for non-existent   |
|                                    | future requirements.                         |
+------------------------------------+----------------------------------------------+
```

### 1.1 Boring by Default
* **Rationale**: A one-person operating system cannot afford the maintenance overhead of experimental frameworks, beta libraries, or highly niche technologies. Boring, stable, and widely-documented technologies ensure that both the human owner and any AI coding agent can quickly reason about bugs and find solutions.
* **Execution**:
  * Prioritize the Python Standard Library. If a task can be accomplished using `json`, `sqlite3`, `pathlib`, or `asyncio`, do not add external wrappers.
  * Avoid exotic paradigms or specialized runtime tools unless they are approved via an ADR in [10_DECISION_LOG.md](file:///Users/anzarakhtar/aios/docs/10_DECISION_LOG.md).
  * Prefer standard, synchronous code for database I/O and configuration parsing (e.g., using `tomli` for configuration parsing).

### 1.2 Optimize for Deletion
* **Rationale**: The capabilities needed in the system will evolve rapidly. If components are tightly coupled, the cost of replacing or deleting obsolete code becomes prohibitive, leading to dead code accumulation and code rot.
* **Execution**:
  * Every module or service must expose a clean, public boundary and hide its internal helpers.
  * Sibling modules must never depend on each other's private submodules. If shared functionality is needed, it must be extracted into a common utility or a dedicated library under the composition root.
  * Prioritize flat files and clear folder structures (never nest folders deeper than 3 levels from the repository root).

### 1.3 One Reason to Change (Single Responsibility)
* **Rationale**: AI-assisted coding is highly susceptible to regression bugs when files handle multiple disconnected responsibilities. A change to fix a UI configuration should never risk breaking database persistence.
* **Execution**:
  * Class definitions must focus on a single domain (e.g., `ConversationStore` manages files serialization; `ConversationManager` coordinates active session instances).
  * Do not combine multiple behaviors inside single scripts (e.g., separating `cli.py` presentation loops from `kernel.py` bootstrap logic).
  * Limit source file sizes to a maximum of **400 lines of code** (as defined in [04_CODING_STANDARDS.md](file:///Users/anzarakhtar/aios/docs/04_CODING_STANDARDS.md)). If a file crosses this threshold, it must be split immediately.

### 1.4 Working Software Over Perfect Architecture
* **Rationale**: Premature architecture and over-engineering waste cognitive effort. It is impossible to predict the exact interfaces the system will need 5 years from now; they must be discovered through actual usage.
* **Execution**:
  * Build the simplest version that works and meets the functional requirements.
  * Do not design complex factory patterns or generic interface layers for components that only have a single concrete implementation today.
  * Rely on pytest suites to act as the safety net, allowing rapid, iterative refactoring as requirements mature.

### 1.5 No Speculative Generality
* **Rationale**: Unused abstractions, unused parameter options, and placeholder functions ("for future use") add immediate maintenance overhead and confuse AI reasoning pathways.
* **Execution**:
  * Every function parameter, class method, and environment variable must serve a current, active requirement.
  * If a feature is not part of the active sprint or the current roadmap milestone, do not write code for it.
  * Do not write stub methods, dummy routes, or unused wrapper APIs under the assumption that "we will need them later."

---

## 2. Dependency Management Policy

Every dependency introduced is a permanent liability. To prevent dependency inflation and supply chain risks, the project enforces a strict audit and control policy.

```
                  +------------------------------------------+
                  |  PROPOSED DEPENDENCY ADDITION FLOWCHARTS |
                  +---------------------+--------------------+
                                        |
                                        v
                            Is it in Standard Library?
                               /                  \
                            (Yes)                 (No)
                             /                      \
              Use Built-In Modules             Does it touch personal data?
                                                    /                  \
                                                 (Yes)                 (No)
                                                   /                      \
                                        Requires owner approval   Does it have releases in 18m?
                                        & ADR logged in docs/10/        /                  \
                                                                     (Yes)                 (No)
                                                                      /                      \
                                                                 Pin Exact Version         Block addition
                                                                 in pyproject.toml
```

### 2.1 Dependency Evaluation Criteria
Before adding any new external library or package:
1. **Standard Library Verification**: Verify if the functionality can be implemented using standard Python libraries with under 100 lines of code. If yes, write the custom implementation.
2. **Library Status Audit**: The target library must be active. Any library with an "unmaintained" status (no commits, releases, or active issue triage in the last **18 months**) is strictly prohibited.
3. **Weight Assessment**: Prefer a small, single-purpose library over a massive framework. For example, use a plain HTTP client like `httpx` rather than importing an entire agentic middleware package.

### 2.2 Version Pinning Rules
* All dependencies must be pinned to an **exact version** inside configuration files (e.g., `pyproject.toml` or `requirements.txt`).
* The use of floating version ranges (`^`, `~`, `>=`, or `latest`) is strictly prohibited.
* *Example of correct configuration*:
  ```toml
  [dependencies]
  tomli = "2.0.1"
  httpx = "0.27.0"
  pytest = "8.2.2"
  ```
* Rationale: A system intended to run unattended for a decade cannot tolerate silent upstream updates breaking the execution environment overnight.

### 2.3 Dependency Approval and Logging Process
1. **Architecture Decision Record**: Any new dependency must be formally justified and logged in [10_DECISION_LOG.md](file:///Users/anzarakhtar/aios/docs/10_DECISION_LOG.md).
2. **Justification Structure**: The ADR entry must explicitly outline:
   * The specific problem the dependency solves.
   * Alternatives considered (including writing it from scratch).
   * Security, performance, and maintenance impacts.
3. **Privacy Gate (Data Exfiltration)**: If a dependency requires network access or interacts with personal files, memory caches, or conversation logs, it must be flagged. Any external data transmission paths require explicit sign-off from the user and must be detailed in [05_SECURITY_GUIDELINES.md](file:///Users/anzarakhtar/aios/docs/05_SECURITY_GUIDELINES.md).

---

## 3. Refactoring Workflow

Refactoring is the process of improving the system's internal structure without changing its external behavior. It must be treated as a surgical, disciplined operation.

### 3.1 Refactoring Triggers
Code should be refactored when:
* **Difficulty in Testing**: Writing unit or integration tests for a service becomes complicated or requires excessive mock setups. This is the primary indicator that interfaces are tightly coupled.
* **Duplication**: The same logical flow or validation routine is repeated across different skill sets or submodules.
* **SRP Violation**: A file is modified for multiple unrelated reasons, or functions cross the cyclomatic complexity limit of 10.

### 3.2 Refactoring Protocols
1. **Isolation Rule**: Refactoring must be executed in dedicated commits and pull requests. **Never** mix refactoring code with functional changes, new features, or bug fixes.
2. **Behavioral Invariance**: A refactor must not modify observable behavior. If API signatures, return schemas, CLI commands, or output formats must change, the operation is classified as a feature change or API deprecation—not a refactor—and must be versioned accordingly.
3. **Incremental Progress**: Do not perform "big-bang" rewrites. Modify components step-by-step behind established interface boundaries defined in the service registry. Keep the application compiling and runnable after every single file edit.
4. **Safety Net Retention**: Refactoring is only permitted when the affected modules have test coverage. You must run the test suite before starting, and all tests must remain green during and after the refactoring edits.

---

## 4. Definition of Done (DoD)

A development task, bug fix, or feature branch is considered **Done** only when it satisfies every item on the following checklist. No exceptions are made for "hotfixes" or AI-generated changes.

### ◈ Compile & Run
* [ ] The codebase executes with zero compilation errors, interpreter syntax errors, or runtime initialization crashes.
* [ ] The linter and formatter run successfully with zero manually-suppressed rules (e.g., `ruff check` and `ruff format` run clean).

### ◈ Testing & Coverage
* [ ] Unit tests are written to verify the public interfaces of all added or modified classes and functions.
* [ ] The entire test suite passes successfully.
* [ ] Overall test coverage does not decrease, and touched files maintain at least **85%** test coverage (as detailed in [06_TESTING_GUIDELINES.md](file:///Users/anzarakhtar/aios/docs/06_TESTING_GUIDELINES.md)).

### ◈ Architecture & Design
* [ ] All concrete services are registered via the composition root in `bootstrap.py` and communicate exclusively through interfaces defined in `registry.py`.
* [ ] Function cyclomatic complexity remains at or below **10**, and no function takes more than **4 parameters** (as defined in [04_CODING_STANDARDS.md](file:///Users/anzarakhtar/aios/docs/04_CODING_STANDARDS.md)).
* [ ] File size limits do not exceed **400 lines**.

### ◈ Security & Privacy
* [ ] Verified that no secrets, access keys, private configuration tokens, or personal identifiers have been committed to source code or git history (checked against the rules in [05_SECURITY_GUIDELINES.md](file:///Users/anzarakhtar/aios/docs/05_SECURITY_GUIDELINES.md)).
* [ ] Any tool that modifies files, issues shell commands, or connects to external endpoints is labeled with the correct risk classification (READ, WRITE, MODIFY, DELETE, NETWORK) and verified against the approval gates.

### ◈ Documentation
* [ ] Every new or updated class, method, and function includes Google-style docstrings outlining parameters, returns, exceptions, and side effects.
* [ ] The module's associated README or skill document is updated to reflect new command structures, aliases, and dependencies.
* [ ] If a dependency was added, an ADR has been recorded in the decision log.

### ◈ Version Control
* [ ] The branch is focused on a single logical feature or fix.
* [ ] Commit messages follow the Conventional Commits format (`feat:`, `fix:`, `refactor:`, `docs:`, `test:`).
* [ ] If the commit was written or assisted by an AI agent, the commit trailer contains the appropriate attribution:
  `Co-authored-by: AI-agent <assistant@personal-ai-os.local>`

---

*Engineering Guidelines · Personal AI OS · Version 1.0 · Governed by the Project Constitution.*
