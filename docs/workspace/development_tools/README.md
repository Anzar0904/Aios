# IDE & Development Tool Integration — Navigation Hub
**Sprint 10 · Milestone 5** · Version 1.0 · July 2026

---

> [!IMPORTANT]
> This directory houses the **IDE & Development Tool Integration** specifications for the Personal AI OS.
> It builds upon the [Workspace Foundation](file:///Users/anzarakhtar/aios/docs/workspace/README.md), [Project Discovery](file:///Users/anzarakhtar/aios/docs/workspace/project_discovery/README.md), [Codebase Intelligence](file:///Users/anzarakhtar/aios/docs/workspace/codebase/README.md), and [Source Control Intelligence](file:///Users/anzarakhtar/aios/docs/workspace/source_control/README.md) specifications.
>
> To maintain compiler independence, all tools (LSPs, debuggers, compilers, shells, editors) are orchestrated centrally by the AI OS reasoning kernel. Operations communicate via standardized local protocols (JSON-RPC, DAP, LSP adapters).

---

## Documents

| Document | Purpose |
|---|---|
| [ide_integration.md](file:///Users/anzarakhtar/aios/docs/workspace/development_tools/ide_integration.md) | Editor-agnostic JSON-RPC socket protocols, active editor tab syncing, and cursor maps |
| [lsp_integration.md](file:///Users/anzarakhtar/aios/docs/workspace/development_tools/lsp_integration.md) | Language Server Protocol (LSP) proxy setups, definition queries, and hover context parsing |
| [terminal_management.md](file:///Users/anzarakhtar/aios/docs/workspace/development_tools/terminal_management.md) | Async terminal streams execution, stdin/stdout pipe monitors, and process limit controls |
| [debugger_integration.md](file:///Users/anzarakhtar/aios/docs/workspace/development_tools/debugger_integration.md) | Debug Adapter Protocol (DAP) session management, breakpoint mappings, and call-stack trace dumps |
| [build_systems.md](file:///Users/anzarakhtar/aios/docs/workspace/development_tools/build_systems.md) | Compiler triggers (Cargo, Npm, Make), stdout error parsers, and diagnostic symbol tags |
| [package_manager_support.md](file:///Users/anzarakhtar/aios/docs/workspace/development_tools/package_manager_support.md) | Dependency graph tracking, version drift alerts, package license audits, and lock validations |
| [tool_orchestration.md](file:///Users/anzarakhtar/aios/docs/workspace/development_tools/tool_orchestration.md) | The Task Executor coordination loop, Event Bus notifications, and multi-tool orchestration |

---

## Reading Order

1. **[`ide_integration.md`](file:///Users/anzarakhtar/aios/docs/workspace/development_tools/ide_integration.md)**: Explore the editor-independent socket protocols.
2. **[`lsp_integration.md`](file:///Users/anzarakhtar/aios/docs/workspace/development_tools/lsp_integration.md)** & **[`debugger_integration.md`](file:///Users/anzarakhtar/aios/docs/workspace/development_tools/debugger_integration.md)**: Review structural LSP and DAP client implementations.
3. **[`terminal_management.md`](file:///Users/anzarakhtar/aios/docs/workspace/development_tools/terminal_management.md)**: Study terminal stream execution and safety limits.
4. **[`build_systems.md`](file:///Users/anzarakhtar/aios/docs/workspace/development_tools/build_systems.md)** & **[`package_manager_support.md`](file:///Users/anzarakhtar/aios/docs/workspace/development_tools/package_manager_support.md)**: Understand build loops and package manager audits.
5. **[`tool_orchestration.md`](file:///Users/anzarakhtar/aios/docs/workspace/development_tools/tool_orchestration.md)**: Examine the central task orchestration pipeline and event flows.
