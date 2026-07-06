# Terminal Session & Process Management Spec
**Sprint 10 · Milestone 5** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define technical interfaces for managing terminal sessions, capturing stdout/stderr, and controlling process timeouts.
* **Scope**: Governs shell subprocess spawners, stream buffers, and watchdog timers.
* **Audience**: Systems Integrators, DBAs, and Lead Developers.
* **Related Documents**:
  * [workspace/security_model.md](file:///Users/anzarakhtar/aios/docs/workspace/security_model.md) - Security sandboxing.
  * [workspace/development_tools/tool_orchestration.md](file:///Users/anzarakhtar/aios/docs/workspace/development_tools/tool_orchestration.md) - Tool orchestration.

---

## 1. Terminal Process Runner

The **Terminal Management** layer handles the execution of shell commands, tests, compilers, and external scripts. It wraps process spawns in a control structure to capture outputs and enforce constraints.

```
[Command Execution Request] (e.g. run pytest)
             |
             v
[Verify Command Safety] ===> Block if blacklisted tokens found
             |
             v
[Spawn Subprocess] ===> redirect pipes: stdout, stderr, stdin
             |
             +---> Output Thread: Capture lines and save to SQLite logs
             +---> Watchdog Thread: Monitor elapsed run time
             |
             v
[Exit Code Evaluation] ===> Return process details & log file path
```

---

## 2. Stream Buffering & Log Recording

To keep log sizes manageable while supporting debugging needs:
* **Circular Output Buffer**: The runner buffers up to **10,000 lines** of console output in memory. Excess output is rotated to a local file in the temporary directory.
* **Stdin Piping**: Enables the AI OS to feed inputs to interactive commands (e.g., confirming database migrations or package installs) after securing developer permission.
* **ANSI Escape Stripper**: Console output streams are cleaned of ANSI color codes and cursor movement markers before being saved to the database.

---

## 3. Execution Watchdog Timers

To prevent infinite loops or hung commands (e.g., a test runner waiting for user input):
* **Default Timeout**: All commands default to a **300-second (5-minute)** timeout, unless overridden.
* **Liveness Heartbeat**: Commands emitting high-frequency logs can extend their duration limit automatically.
* **Force Kill Sequence**: If a process times out, the system issues a `SIGTERM`. If the process fails to exit within 5 seconds, it issues a `SIGKILL` to clean up the workspace.
