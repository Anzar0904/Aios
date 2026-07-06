# IDE & Editor Integration Spec
**Sprint 10 · Milestone 5** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define technical interfaces and RPC protocols for editor-agnostic editor integrations.
* **Scope**: Governs WebSocket server parameters, client plugins, and editor state synchronization.
* **Audience**: Systems Integrators, Client Developers, and AI developers.
* **Related Documents**:
  * [workspace/capabilities.md](file:///Users/anzarakhtar/aios/docs/workspace/capabilities.md) - Capabilities domains.
  * [workspace/development_tools/README.md](file:///Users/anzarakhtar/aios/docs/workspace/development_tools/README.md) - Dev tools hub.

---

## 1. Editor-Agnostic RPC Server

To avoid vendor lock-in and support multiple editor frontends (VS Code, JetBrains IDEs, Neovim, Emacs), the **AI OS Kernel** hosts a local **JSON-RPC WebSocket Server**:
* **Port**: Bound to local loopback interface (`127.0.0.1:48200`), blocking external network connections.
* **Message Protocol**: Standard JSON-RPC 2.0 payloads.

```
+------------------+                   +----------------------------------+
|  Editor Client   | ==(WebSocket)==>  | AI OS Workspace RPC Server       |
|  (VS Code, Neo)  |                   | (127.0.0.1:48200)                |
+------------------+                   +----------------------------------+
         |                                               |
         +--- Notify: Active Tab File ------------------>| (Sync state)
         +--- Notify: Cursor Line/Col ------------------>| (Cache coordinates)
         +--- Request: Resolve Agent Plan <--------------+ (Read input details)
```

---

## 2. Editor State Synchronization

The RPC server listens for state events emitted by the client plugins to maintain active context:
* **`workspace/didChangeActiveTextEditor`**: Sent when the developer changes tabs. Updates the active workspace context in the memory database.
* **`workspace/didChangeCursorPosition`**: Sent as the developer moves their cursor. Cache coordinates (`file_path`, `line_number`, `column_number`) so agent queries can target the exact symbol under the cursor.
* **`workspace/didModifyFile`**: Notifies the AI OS filesystem watcher to queue AST re-compiles.

---

## 3. Client Plugin Specifications

* **VS Code**: TypeScript client using vscode extension API listeners (`window.onDidChangeActiveTextEditor`).
* **Neovim**: Lua plugin implementing native RPC channels (`vim.lsp.start_client` or standalone sockets).
* **JetBrains**: Kotlin plugin targeting the IntelliJ SDK platform APIs.
