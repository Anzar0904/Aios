# AI OS Service Audit Report

This report audits the core system services registered under the `ServiceRegistry` within AI OS.

## Core Services Audit

### 1. Model Router (`ModelService`)
* **State**: Fully Implemented
* **Details**: Orchestrates requests to external providers (Anthropic, Gemini, OpenRouter) and applies retry/fallback policies.
* **Database / Config**: Configured via `config/config.toml`.
* **Dependencies**: None.

### 2. Memory Service (`MemoryService`)
* **State**: Fully Implemented
* **Details**: SQLite-backed semantic vector storage fallback with Qdrant connectivity checks.
* **Database / Config**: Schema written to `aios.db` or Qdrant cluster connections.
* **Dependencies**: `sqlite3` or `qdrant-client`.

### 3. Context Service (`ContextService`)
* **State**: Fully Implemented
* **Details**: Manages runtime contexts including active project, sprint goals, target topics, and user sessions.
* **Database / Config**: Stores local states in `.agent/context.json`.
* **Dependencies**: EventBus.

### 4. Knowledge Graph (`GraphService`)
* **State**: Fully Implemented
* **Details**: SQLite graph structure mapping entities (agents, tasks, workflows, repos) and their relational edges.
* **Database / Config**: Tables: `entities`, `relationships` in `aios_graph.db`.
* **Dependencies**: `sqlite3`.

### 5. Project Registry (`ProjectRegistry`)
* **State**: Fully Implemented
* **Details**: Backs workspace setup, folders metadata, and file trackers.
* **Database / Config**: SQLite table `projects` in `aios.db`.
* **Dependencies**: ContextService.

### 6. Agency Registry (`AgencyService`)
* **State**: Fully Implemented
* **Details**: Controls sales pipeline, clients contracts, expected revenue weightings, and calendar syncs.
* **Database / Config**: SQLite table `agency_leads` and `agency_clients`.
* **Dependencies**: GraphService.

### 7. Workflow Registry (`WorkflowService` / `N8NService`)
* **State**: Fully Implemented
* **Details**: Integrates with local self-hosted n8n instances, translates JSON workflows, and manages templates.
* **Database / Config**: Configured via `.agent/n8n_config.json`.
* **Dependencies**: `n8n` HTTP client.

### 8. Integration Registry (`IntegrationsService`)
* **State**: Fully Implemented
* **Details**: Connector registration and credential lookup policies.
* **Database / Config**: Vault audits log and credentials stored in `aios.db` (rot13 encrypted).
* **Dependencies**: `sqlite3`.

### 9. Documentation Service (`DocumentationService`)
* **State**: Fully Implemented
* **Details**: Analyzes code structure via AST parser and outputs API reference markdown docs.
* **Database / Config**: Outputs files in `docs/reference/`.
* **Dependencies**: SoftwareEngineerAgent.

### 10. Research Service (`ResearchService`)
* **State**: Fully Implemented
* **Details**: Performs crawls, searches google, parses PDF papers, and saves learning metrics.
* **Database / Config**: Tables: `research_papers`, `crawls` in `aios.db`.
* **Dependencies**: Search API keys.

### 11. Personal Service (`PersonalService`)
* **State**: Fully Implemented
* **Details**: Tracks goals, daily routines, schedule event queues, and calendar conflicts.
* **Database / Config**: SQLite tables `personal_goals`, `habits`, `calendar_events`.
* **Dependencies**: DailyOSService.

### 12. Agent Registry (`AutonomousAgentPlatform`)
* **State**: Fully Implemented
* **Details**: Instantiates and registers the 7 core specialized agents; coordinates task scheduling.
* **Database / Config**: Persists task lists and memory logs to `.agent/agent_memory.json`.
* **Dependencies**: ModelService.

### 13. Notification Center (`UXPlatform`)
* **State**: Fully Implemented
* **Details**: Orchestrates alerts tracking, priority logs, category filters, and workspace notifications.
* **Database / Config**: JSON file `.agent/notifications.json`.
* **Dependencies**: None.

### 14. Event Bus (`EventBus`)
* **State**: Fully Implemented
* **Details**: Async in-process pub/sub event router coordinating agent states and git triggers.
* **Database / Config**: Event queues in memory.
* **Dependencies**: None.

### 15. Scheduler (`DailyOSService`)
* **State**: Fully Implemented
* **Details**: Sequences cron-like checks for reminders, calendar conflicts, and daily summary schedules.
* **Database / Config**: Configured via `.agent/scheduler.json`.
* **Dependencies**: PersonalService.

### 16. Goal Engine (`ProjectIntelligenceService`)
* **State**: Fully Implemented
* **Details**: Maps high-level user statements into structured goals and breaks them into tasks.
* **Database / Config**: SQLite tables `project_goals`.
* **Dependencies**: GraphService.

### 17. Task Engine (`ExecutionEngine`)
* **State**: Fully Implemented
* **Details**: Resolves task dependencies via topological sorting and schedules execution routines.
* **Database / Config**: Task statuses (`pending`, `running`, `completed`, `failed`).
* **Dependencies**: Agent Registry.
