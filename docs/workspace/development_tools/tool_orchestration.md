# Development Tool Orchestration Spec
**Sprint 10 · Milestone 5** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define orchestration loops, Event Bus integrations, and sequential tool execution flows.
* **Scope**: Governs core Task Executor pipelines and coordination policies.
* **Audience**: Systems Architects, Lead Developers, and AI developers.
* **Related Documents**:
  * [16_ENGINEERING_BIBLE.md](file:///Users/anzarakhtar/aios/docs/16_ENGINEERING_BIBLE.md) - System tasks.
  * [workspace/development_tools/terminal_management.md](file:///Users/anzarakhtar/aios/docs/workspace/development_tools/terminal_management.md) - Terminal execution.

---

## 1. Central Conductor Pipeline

The **Tool Orchestration** engine coordinates multiple workspace tools (filesystem, compiler, debugger, git) to execute developer plans safely.

```
                    [Agent: Process Dev Plan]
                               |
                               v
                     [State 1: Code Editing]
            - Modify source files within workspace bounds.
                               |
                               v
                    [State 2: Build & Check]
            - Run compiler (Cargo, Poetry, Npm).
            - If fail -> Parse error -> Start Debugger/DAP -> Correct code -> Loop.
                               |
                               v
                     [State 3: Verification]
            - Run targeted pytest/jest suites.
            - If fail -> Identify failed symbols -> Fix.
                               |
                               v
                   [State 4: Version Control]
            - conventional commit validation.
            - Push code changes to Git branch.
```

---

## 2. Event Bus Integrations

Orchestration tasks publish status signals to the AI OS **Event Bus**:
* **`workspace.file_edited`**: Published when files are saved, triggering AST re-indexes.
* **`workspace.build_status`**: Emits build success/failure states.
* **`workspace.test_completed`**: Publishes test pass rates and diagnostics.
* **`workspace.git_commit`**: Emits commit hashes and changed file lists.

---

## 3. Task Executor & Memory Service Sync

* **Task Execution Registry**: Active task steps (e.g. running a build, executing git commits) are registered under the system-wide `TaskExecutor`, allowing developers to track progress and cancel tasks at any point.
* **Memory Sync Loops**: Completed reports, error logs, and git diff statistics are formatted, embedded, and cached inside the Qdrant `workspace_memory` vector index. This ensures the reasoning engine has access to recent build and execution history during planning.
