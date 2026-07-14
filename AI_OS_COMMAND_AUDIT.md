# AI OS Command Audit Report

This report audits every command registered in the AI OS shell interface. It verifies whether commands are properly wired, registered in `core/src/aios/cli.py`, executable, and backed by test coverage.

## CLI Subcommands Audit Table

| Subcommand | Purpose | Registered | Executable | Tested | Verification Code / Method |
|---|---|---|---|---|---|
| `aios` | Clean system boot & Command Center launch | Yes (main entry) | Yes | Yes | `core/tests/test_ux_platform.py` |
| `aios dashboard` | Launches interactive Command Center | Yes | Yes | Yes | `execute_builtin_cli_command(["dashboard"])` |
| `aios search <query>` | Universal search across projects/tasks/docs | Yes | Yes | Yes | `execute_builtin_cli_command(["search", "aios"])` |
| `aios notifications` | List unread and priority alerts | Yes | Yes | Yes | `execute_builtin_cli_command(["notifications"])` |
| `aios workspace <name>` | Launch directly into specific workspace view | Yes | Yes | Yes | `execute_builtin_cli_command(["workspace", "project"])` |
| `aios status` | Renders active OS status bar panel | Yes | Yes | Yes | `execute_builtin_cli_command(["status"])` |
| `aios project` / `projects` | List, create, and inspect active projects | Yes | Yes | Yes | `core/tests/test_project_intelligence.py` |
| `aios agency` | CRM pipelines, meetings tracker, and revenue | Yes | Yes | Yes | `core/tests/test_agency.py` |
| `aios workflow` / `workflows` | n8n workflow deployment, triggers, versioning | Yes | Yes | Yes | `core/tests/test_workflow_intelligence.py` |
| `aios github` | Pull Request reviews, commits telemetry, health | Yes | Yes | Yes | `core/tests/test_source_control.py` |
| `aios research` | Academic paper retrieval and crawl synthesis | Yes | Yes | Yes | `core/tests/test_research.py` |
| `aios personal` | Track routines, morning schedules, habits | Yes | Yes | Yes | `core/tests/test_personal.py` |
| `aios chat` | Direct conversation stream with default model | Yes | Yes | Yes | `core/tests/test_reasoning.py` |
| `aios agent` / `agents` | Deploy, inspect, and run multi-agent pipelines | Yes | Yes | Yes | `core/tests/test_agents.py` |
| `aios ask <query>` | Resolve query and execute single task | Yes | Yes | Yes | `core/tests/test_nl_os.py` |
| `aios intent <query>` | Debug intent type categorization and scores | Yes | Yes | Yes | `core/tests/test_reasoning.py` |
| `aios plan <query>` | View Action Plan generation before running | Yes | Yes | Yes | `core/tests/test_nl_os.py` |
| `aios execute <query>` | Runs reasoning routing and execution pipeline | Yes | Yes | Yes | `core/tests/test_nl_os.py` |
| `aios context` | Get/Set context variables | Yes | Yes | Yes | `core/tests/test_session.py` |
| `aios diagnostics` / `doctor` | Self-diagnostics system check | Yes | Yes | Yes | `core/tests/test_ux_polish.py` |
| `aios session` | Inspect active session configuration | Yes | Yes | Yes | `core/tests/test_session.py` |
| `aios models` / `providers` | List available providers and configured LLM | Yes | Yes | Yes | `core/tests/test_providers.py` |
| `aios graph` | Query local SQLite knowledge graph | Yes | Yes | Yes | `core/tests/test_knowledge_graph.py` |

## Audit Summary
All **23 primary command verbs** are registered in the unified parser and router inside `core/src/aios/cli.py`. The boot sequence launches directly into the interactive UX Command Center loop when no arguments are supplied.
