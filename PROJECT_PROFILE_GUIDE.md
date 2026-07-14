# Project Profile Guide

This guide describes how to configure, customize, and extend project profiles within the AI OS.

## Profile Architecture

A Project Profile defines a project's identity, metadata, preferred models, and active system integrations.

```yaml
name: AI OS
type: software
priority: critical
preferred_models:
  - deepseek-coder-v2
  - qwen2.5-coder
  - deepseek-r1

github:
  enabled: true
  repo: Anzar0904/Aios
  branch: main

notion:
  enabled: true
  workspace_id: ws_01
  database_id: db_02

n8n:
  enabled: true
  workflow_ids:
    - workflow_task_sync
    - workflow_deploy

memory:
  enabled: true
  namespace: unique-uuid-namespace
  retention_days: 365

knowledge_graph:
  enabled: true
```

---

## Configuration Fields

### Core Fields

| Field | Type | Options / Description |
|---|---|---|
| `name` | String | Unique name of the project. |
| `description` | String | A brief description of the project. |
| `project_type` | Enum | `software`, `agency`, `research`, `college`, `hackathon`, `portfolio`, `automation`, `other` |
| `status` | Enum | `active`, `paused`, `completed`, `archived`, `planning` |
| `priority` | Enum | `critical`, `high`, `medium`, `low` |
| `owner` | String | Username or group identifying project ownership. |

### Model Preferences

Each project specifies a descending list of preferred models. The AI OS model router automatically delegates tasks according to this routing table:
- **Software Projects**: Defaults to coding-specialized models (`deepseek-coder-v2`, `qwen2.5-coder`).
- **Research Projects**: Defaults to reasoning models (`deepseek-r1`).
- **Agency Projects**: Prioritizes balanced assistants (`qwen3.5`, `gemma3:12b`).

### Integration Adapters

- **github**:
  - `enabled`: Activates git analysis.
  - `repo`: Owner/Repo slug (e.g. `Anzar0904/Aios`).
  - `branch`: Target tracking branch.
- **notion**:
  - `enabled`: Automatically syncs tasks, calendars, and sprint logs to Notion.
- **n8n**:
  - `enabled`: Monitors automation execution and registers workflow health reports.

---

## Modifying Profiles

Project profiles can be updated via CLI or directly using the service layer:

```bash
# Update priority or status via CLI
aios project status
```

Or via Python:
```python
from aios.services.project_registry_impl import ProjectRegistryImpl

reg = ProjectRegistryImpl()
reg.initialize()

# Update preferred models
reg.update_project(project_id, {
    "preferred_models": ["gpt-4o", "claude-3-5-sonnet"]
})
```
