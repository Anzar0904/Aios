# Notion Intelligence — Security & Trust Model
**Sprint 9 · Milestone 1 (Foundation)** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Establish credential isolation, permissions scoping, prompt injection sanitization, and data loss prevention policies for the Notion Intelligence module.
* **Scope**: Governs key managers, data scrubbers, security interceptors, and local encryption models.
* **Audience**: Security Officers, Systems Architects, and Audit Engineers.
* **Related Documents**:
  * [05_SECURITY_GUIDELINES.md](file:///Users/anzarakhtar/aios/docs/05_SECURITY_GUIDELINES.md) - Threat models and path validation routines.
  * [notion/capabilities.md](file:///Users/anzarakhtar/aios/docs/notion/capabilities.md) - Permissions and scopes mappings.

---

## 1. Credential Security & Isolation

Integration tokens and API keys are protected assets. To prevent accidental leaks and exfiltration:

* **Config Isolation**: Credentials must never be hardcoded or checked into Git. The integration token (`NOTION_TOKEN`) is loaded from environment variables or from a secured configuration file (`config/config.toml`).
* **Cache Encryption**: The local SQLite replica database containing synced pages, page titles, and comment history is encrypted at rest using **SQLCipher** (AES-256), utilizing a key derived from system-level variables.
* **Network Isolation**: The `NotionAPIClient` only communicates with `https://api.notion.com`. Subprocess requests targeting external domains or unofficial proxies are blocked by the OS-level sandboxing system.

---

## 2. Principle of Least Privilege (PoLP)

The Notion integration is restricted in scope by design:

* **Connection Scoping**: The integration token is locked to the specific sub-pages and databases shared by the user. It cannot search or scan other parts of the workspace.
* **Mutation Restriction**:
  * **Read-Only Mode**: The OS configuration can enforce `notion_read_only = true` to guarantee that the system never writes to or alters any remote Notion pages.
  * **Mutation Risk Gating**: When writes are enabled, the OS categorizes operations:

```
+---------------+------------------------+---------------------------------------+
| Risk Level    | Operations             | Action Gate                           |
+---------------+------------------------+---------------------------------------+
| LOW           | Adding log entries,    | Logged automatically; executed        |
|               | appending reports.     | asynchronously without interruption.  |
+---------------+------------------------+---------------------------------------+
| MEDIUM        | Updating task card     | Allowed if initiated by a direct user  |
|               | status categories.     | REPL command.                         |
+---------------+------------------------+---------------------------------------+
| HIGH          | Deleting pages or      | Blocked. Requires explicit manual     |
|               | database records.      | confirmation in the REPL console.     |
+---------------+------------------------+---------------------------------------+
```

---

## 3. Security Guardrails & Sanitization

Because the AI OS processes content retrieved from external Notion workspaces, it treats all Notion block text as **untrusted user input**.

### 3.1 Prompt & Command Injection Mitigation
* **Command Sanitization**: Code blocks pulled from Notion pages are treated as raw text and are never executed directly by the local shell. If the user asks the OS to run code copied from a Notion page, the OS displays the code and prompts the user for confirmation.
* **Parser Isolation**: The Notion AST parser does not support processing raw HTML tags, javascript execution elements, or macro commands. Unrecognized blocks are ignored and logged as plain text.

### 3.2 Data Loss Prevention (DLP)
To protect personal information from leaking to external servers:
1. **PII and Secret Detection**: Before sending write requests to the Notion API, sync payloads are parsed by a DLP pre-sync scrubber.
2. **Regex Scanning**: The scrubber scans text arrays for:
   * Private SSH/PGP keys.
   * Cloud API tokens (e.g. AWS, GCP, GitHub tokens).
   * Password strings.
   * Standard PII formats (e.g. Social Security numbers, credit card strings).
3. **Redaction**: Matches are replaced with placeholders (e.g., `[REDACTED_API_TOKEN]`) before remote transmission.

---

## 4. Security Auditing

All operations are logged to a local file (`logs/notion_security_audit.log`). Every log entry includes:
* UTC Timestamp
* Target Page ID / Database ID
* Operation Type (`READ`, `WRITE`, `DELETE`)
* Invoking Service Name (e.g., `ApprovalEngineService`, `MemoryService`)
* Bytes Transmitted
* Risk Class Rating (`LOW`, `MEDIUM`, `HIGH`)
* Payload Sanity Status (e.g. `CLEAN`, `SCRUBBED`)
