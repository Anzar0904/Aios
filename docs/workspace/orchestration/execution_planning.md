# Execution Planning & Replanning Spec
**Sprint 10 · Milestone 6** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define DAG planner generation, step tracking, and error-driven replanning rules.
* **Scope**: Governs execution step graphs, compiler checks, and fallback triggers.
* **Audience**: AI Prompt Engineers, Integration Engineers, and Quality Auditors.
* **Related Documents**:
  * [workspace/capabilities.md](file:///Users/anzarakhtar/aios/docs/workspace/capabilities.md) - Capabilities domains.
  * [workspace/development_tools/tool_orchestration.md](file:///Users/anzarakhtar/aios/docs/workspace/development_tools/tool_orchestration.md) - Tool orchestration.

---

## 1. DAG Execution Planner

The **Execution Planner** converts high-level objectives (e.g. "fix auth bug and push") into a Directed Acyclic Graph (DAG) of task steps ($G_{plan} = (V_{steps}, E_{dependencies})$):

```
       [Step 1: Edit code]
                |
                v
      [Step 2: Cargo Check]
                |
                v
       [Step 3: Run Tests]
         /             \
    (Success)        (Failure)
       /                 \
      v                   v
[Step 4: git push]   [Step 5: Diagnostics & Fix] ===> Link back to Step 1
```

* **Nodes ($V_{steps}$)**: Custom tool executions (e.g., `EditFile`, `RunBuild`, `RunTests`, `GitCommit`).
* **Dependencies ($E_{dependencies}$)**: Execution orders (e.g., Step 2 cannot run until Step 1 completes).

---

## 2. Error-Driven Replanning Loop

When a step fails (e.g., a test suite fails):
1. **Analyze Failure**: The planner captures stderr outputs, compiler warnings, and test logs.
2. **Diagnose**: Runs static analyses or DAP debug sessions to isolate the failure to specific AST symbols.
3. **Generate Fix**: Creates a sub-plan containing targeted edits to fix the identified issue.
4. **Mutate DAG**: Updates the execution graph by inserting the fix steps before the failed verification step, continuing execution.

---

## 3. Fallback Gates & Rollbacks

To prevent leaving the workspace in a broken state:
* **Pre-Commit Checks**: If build checks fail after three fix attempts, the system halts execution.
* **Safe Rollbacks**: Restores files to their pre-task state using Git commands (`git checkout -- [paths]` or `git reset --hard`) to clean up temporary edits.
* **Alert Escalate**: Triggers notification warnings to the developer and prompts for manual guidance.
