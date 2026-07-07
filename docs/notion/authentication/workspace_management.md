# Notion Intelligence — Workspace Management
**Sprint 9 · Milestone 2** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define multi-workspace configuration models, workspace-switching interfaces, registration protocols, and active workspace scopes.
* **Scope**: Governs workspace configuration schemas, profile indexing registries, and REPL CLI boundaries.
* **Audience**: Systems Architects, CLI Developers, and AI coding agents.
* **Related Documents**:
  * [00_PROJECT_VISION.md](file:///Users/anzarakhtar/aios/docs/00_PROJECT_VISION.md) - Project Constitution.
  * [notion/capabilities.md](file:///Users/anzarakhtar/aios/docs/notion/capabilities.md) - Workspace permissions and boundaries.

---

## 1. System of Record: AI OS Primary

In the Personal AI OS architecture, **Notion is treated as an external sync target, never the system of truth**. 
* **State Ownership**: The local AI OS maintains the primary index of registered workspaces, pages, and metadata hashes.
* **Orchestration**: If a workspace is deleted or updated on Notion, the AI OS keeps its local history intact. It only updates its registers after validating diffs.
* **Data Flow Directionality**: Configuration resides locally. Workspace selection, active scopes, and sync bounds are governed entirely by local user settings.

---

## 2. Multi-Workspace Support

The Notion Intelligence module supports registering multiple Notion workspaces under a single user profile.

```
       [Config Manager] ===> Reads Active Workspace Index (SQLite/Keyring)
              |
              +---> Workspace A ("Personal Workspace" - ID: 8f8bca...) [Active Scope]
              |
              +---> Workspace B ("Work Workspace"     - ID: d9fa12...)
```

### 2.1 Workspace Metadata Schema
Each registered workspace is logged in the local SQLite metadata directory (`notion_workspaces` table):
```sql
CREATE TABLE IF NOT EXISTS notion_workspaces (
    workspace_id TEXT PRIMARY KEY,
    workspace_name TEXT NOT NULL,
    workspace_icon TEXT,
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active INTEGER CHECK(is_active IN (0, 1)) DEFAULT 0,
    sync_policy TEXT CHECK(sync_policy IN ('ON_DEMAND', 'SCHEDULED')) DEFAULT 'ON_DEMAND',
    last_sync_completed_at TIMESTAMP
);
```

### 2.2 Configuration Schema
The active workspace mappings are referenced in `config/config.toml` (or inside the local sqlite registry configuration table):
```toml
[providers.notion]
active_workspace_id = "8f8bca12-efd8-4ba3-bfd0-cd1712a4501a"
offline_mode = false

[[providers.notion.workspaces]]
id = "8f8bca12-efd8-4ba3-bfd0-cd1712a4501a"
name = "Personal Workspace"
sync_interval_minutes = 60

[[providers.notion.workspaces]]
id = "d9fa12bc-e747-49d7-8e6f-54bf9e16bc82"
name = "Work Workspace"
sync_interval_minutes = 120
```

---

## 3. Workspace Selection & CLI Control

The user controls the active workspace namespace directly from the REPL command line interface. The OS routes search and sync queries targeting Notion to the active workspace.

### 3.1 CLI Commands (REPL Layer)
* `notion workspace list`: Lists all registered workspaces, showing names, IDs, and active tags.
* `notion workspace use <workspace_id_or_name>`: Switches the active workspace, updating the local configuration state.
* `notion workspace register`: Launches the OAuth authentication code loop to add a new workspace connection.
* `notion workspace remove <workspace_id>`: Removes credentials and local replica cache files matching the targeted workspace.

### 3.2 Workspace-Scoped Queries
When performing searches inside the memory database, queries are scoped strictly to the active workspace:
```python
# Query is scoped to active workspace ID
workspace_id = auth_manager.get_active_workspace_id()
chunks = vector_store.search(
    query=user_query,
    filters={"workspace_id": workspace_id}
)
```
