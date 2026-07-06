# Language Server Protocol (LSP) Proxy Spec
**Sprint 10 · Milestone 5** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define technical specifications for proxying requests to local Language Servers (LSPs).
* **Scope**: Governs LSP client launchers, message routing, and semantic data extraction.
* **Audience**: Systems Developers, Search Engineers, and AI developers.
* **Related Documents**:
  * [workspace/codebase/code_navigation.md](file:///Users/anzarakhtar/aios/docs/workspace/codebase/code_navigation.md) - Code navigation.
  * [workspace/development_tools/ide_integration.md](file:///Users/anzarakhtar/aios/docs/workspace/development_tools/ide_integration.md) - IDE connections.

---

## 1. LSP Proxy Architecture

While the AI OS maintains a local static index of code symbols, resolving complex type inferences, macro expansions, and dynamic autocompletions requires communicating with active Language Servers (`rust-analyzer`, `gopls`, `pyright`, `typescript-language-server`).

The **LSP Proxy** connects to these local servers over standard I/O pipes or socket channels:

```
[Agent: Resolve Types] ===> Workspace LSP Adapter
                                    |
                            [Identify Language] (e.g. Python -> Pyright)
                                    |
                          [Launch/Connect LSP] ===> Local Pyright Process (stdin/stdout)
                                    |
                            [JSON-RPC Message] ===> Send textDocument/hover
                                    |
                            [Response Parser] ===> Return markdown signature to agent
```

---

## 2. Supported LSP Actions

The LSP Adapter implements client wrappers for core LSP capabilities:
* **`textDocument/definition`**: Resolves type and variable definitions, returning line numbers and target files.
* **`textDocument/references`**: Queries the server for all references to a symbol, supporting cross-module refactoring.
* **`textDocument/hover`**: Retrieves documentation, type signatures, and parameters for the token under the cursor.
* **`textDocument/diagnostic`**: Pulls compiler diagnostics (warnings, errors) directly from the language server in real time.

---

## 3. LSP Lifecycle Management

* **Auto-Discovery**: The system scans local system directories and package structures to locate installed language servers.
* **Process Isolation**: Language servers are spawned as background daemon processes, managed by the AI OS, and terminated when the workspace session closes.
* **Request Buffering**: To prevent blocking agent pipelines, LSP queries are executed asynchronously, returning results via callback hooks.
