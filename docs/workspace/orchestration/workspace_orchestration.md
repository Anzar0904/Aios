# AI Workspace Orchestration Spec
**Sprint 10 · Milestone 6** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define technical interfaces and coordination loops for the central Workspace Orchestration engine.
* **Scope**: Governs coordinator threads, Event Bus subscriptions, and multi-tool orchestration.
* **Audience**: Systems Architects, DBAs, and AI developers.
* **Related Documents**:
  * [workspace/workspace_intelligence.md](file:///Users/anzarakhtar/aios/docs/workspace/workspace_intelligence.md) - Conceptual vision.
  * [workspace/orchestration/README.md](file:///Users/anzarakhtar/aios/docs/workspace/orchestration/README.md) - Orchestration hub.

---

## 1. The Central Director Paradigm

The **AI Workspace Orchestration** engine serves as the main coordinator of the development workspace. Instead of tools triggering actions independently, the AI OS kernel controls all filesystem modifications, LSP checks, terminal commands, and compiler runs.

```
                    +------------------------------------+
                    |        AI OS Kernel (Director)     |
                    +------------------------------------+
                      /         |            |         \
                     v          v            v          v
               [Filesystem]   [LSP]     [Terminal]  [Git Executor]
```

* **Coordination Loop**:
  1. **Observe**: Gathers file change events, compiler status updates, and developer cursor movements.
  2. **Reason**: Analyzes the active workspace state against active goals.
  3. **Plan**: Generates or updates execution plans.
  4. **Act**: Invokes the necessary tools (e.g. refactoring code, running tests, committing changes) sequentially.

---

## 2. Event Bus Orchestration Signals

The coordinator subscribes to and publishes system-wide events:
* **`workspace.goal_initiated`**: Published when a user sets an objective (e.g. "fix compiler warnings"), starting the planning phase.
* **`workspace.plan_step_completed`**: Signals that a plan step (e.g., code edit or test run) succeeded.
* **`workspace.plan_step_failed`**: Signals a step failure, triggering the diagnostics and replanning loops.
* **`workspace.sync_completed`**: Published when local changes are successfully committed and pushed.
