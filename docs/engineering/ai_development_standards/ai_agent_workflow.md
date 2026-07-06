# AI Agent Workflow & Multi-Agent Coordination
**Engineering Bible — Milestone 6**
**Version 1.0** · *Classified: For One Person Only* · *July 2026*

---

## 1. The Agent Cognitive Lifecycle

AI agents in the Personal AI OS execute queries using a structured cognitive lifecycle:

```
 [User Input] ➔ [Intent Resolution] ➔ [Context Assembly] ➔ [Task Planning] ➔ [Tool Execution] ➔ [Summary]
```

1. **Intent Resolution**: Map natural language queries to registered system commands or route them to the Brain.
2. **Context Assembly**: Gather active workspace context (cwd, git status) and query semantic memory.
3. **Task Planning**: Decompose complex objectives into a sequence of executable tool steps.
4. **Tool Execution**: Execute steps in order. High-risk operations require human approval.
5. **Summary**: Format results into a clear markdown response.

---

## 2. Multi-Agent Delegation

For complex or long-running tasks:
* **Spawning Subagents**: Spawn specialized subagents (such as the `research` subagent for read-only codebase reviews or a `self` clone for isolated work) using the `invoke_subagent` tool.
* **Message-Driven Communication**: Communicate with subagents using the `send_message` tool.
* **No Loop Polling**: Avoid polling or checking subagent status in a loop. The Agent Runtime handles messaging asynchronously and notifies the parent agent once a subagent responds.

---

## 3. Background Task Coordination

When managing long-running terminal tools or compiler tasks:
* **Asynchronous Scheduling**: Run long-running commands as background tasks using `run_command` (configured with `WaitMsBeforeAsync`).
* **Timer Schedules**: Use the `schedule` tool to configure one-shot notifications or recurring cron jobs. Do not run sleep commands (`sleep 600`) to delay execution.
* **Task State Management**: Use `manage_task` with the `TaskId` to monitor progress, send input, or cancel execution.

---

*Engineering Bible AI Development Standards · Personal AI OS · Sprint 8 M6 · Governed by [04_AI_MODEL_STRATEGY.md](file:///Users/anzarakhtar/aios/docs/04_AI_MODEL_STRATEGY.md)*
