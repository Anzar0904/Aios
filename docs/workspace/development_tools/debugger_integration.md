# Debugger & DAP Coordination Spec
**Sprint 10 · Milestone 5** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define technical interfaces for coordinating debug adapter sessions and parsing crash outputs.
* **Scope**: Governs DAP clients, breakpoints, and call-stack trace dumping.
* **Audience**: AI Prompt Engineers, Integration Engineers, and Quality Auditors.
* **Related Documents**:
  * [workspace/capabilities.md](file:///Users/anzarakhtar/aios/docs/workspace/capabilities.md) - Capabilities domains.
  * [workspace/development_tools/lsp_integration.md](file:///Users/anzarakhtar/aios/docs/workspace/development_tools/lsp_integration.md) - LSP integrations.

---

## 1. Debug Adapter Protocol (DAP) Integration

To automate bug diagnostics, the AI OS interfaces with standard local debuggers (e.g. `debugpy` for Python, `node-debug2` for JS/TS, `lldb` for native compiled projects) using the standardized **Debug Adapter Protocol (DAP)**.

```
[Agent: Debug Failure] ===> DAP Adapter Manager
                                    |
                          [Load Launch Config] (e.g. launch.json)
                                    |
                           [Start Debug Session] ===> Spawn DAP target process
                                    |
                           [Register Breakpoints] ===> Set file line targets
                                    |
                            [Trigger Execution]
                                    |
                           [Trap Stopped Event] ===> Retrieve call-stack & local variables
```

---

## 2. Dynamic Debugging Commands

The DAP Client allows agents to coordinate executions step-by-step:
* **`setBreakpoints`**: Sets breakpoints at specific lines.
* **`stepIn` / `stepOut` / `next`**: Steps through execution scopes.
* **`stackTrace`**: Queries the stack frames, mapping execution points back to file and symbol indexes.
* **`scopes` / `variables`**: Inspects local variables and arguments within stack frames.

---

## 3. Crash Diagnostics & Variable Dumps

When a test run or local application execution crashes:
1. The AI OS traps the unhandled exception using the DAP listener.
2. It dumps the call stack list, matching frame files to codebase symbol paths.
3. For each frame, it dumps the values of local variables and arguments.
4. It compiles this crash metadata into a diagnostic summary. This provides the reasoning engine with the context needed to resolve the crash without human assistance.
