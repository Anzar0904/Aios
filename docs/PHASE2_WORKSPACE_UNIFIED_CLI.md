# AI OS Phase 2: AI Workspace & Unified CLI
## Technical & Developer Documentation

---

## Overview

Phase 2 introduces a unified command interface and automatic workspace session state restoration for AI OS. It implements a complete boot sequence, real system health checks, background execution services, Notion work synchronization, and project/sprint state caching.

---

## Boot Sequence Mechanics

When the AI OS Kernel boots:
1. **Load Config**: Loads configuration from `config/config.toml`.
2. **RESTORE WORKSPACE**: Retrieves cached workspace data from `.agent/session.json`. If `previous_workspace_root` exists, the context is restored to that path.
3. **BOOT SERVICES**: Sequentially boots and registers all services in the `ServiceRegistry`.
4. **START RUNTIME**: Spawns watchers (Git, Memory, Workspace, etc.) and starts a background ticking daemon thread in the `RuntimeService` to handle asynchronous tasks.
5. **START NOTION SYNC**: Schedules an immediate synchronization of daily tasks with Notion, and registers a recurring hourly job in the background task queue.
6. **TRANSITION READY**: Marks the system state as `READY` and publishes the `KernelStartedEvent`.

---

## Subsystem Health Checks

`aios doctor` (or `aios diagnostics` / startup sequence) runs functional health checks:

| Check Name | Target Checked | Healthy / Connected Criteria |
|---|---|---|
| **Python** | System Python Version | Installed version >= `3.12` |
| **Git** | Repository Context | Git executable in path & inside a git repository |
| **Ollama** | Local daemon | http://localhost:11434/api/tags responds with 200 |
| **Models** | Model discovery | At least 1 Ollama model downloaded and returned |
| **Notion** | Token verification | Integration token set in config or environment variables |
| **GitHub** | Token verification | Token set in config or environment variables |
| **Supabase** | Client credentials | Project URL and role key configured |
| **n8n** | Local runtime | Local host port 5678 reachable |
| **External HDD** | Mounted path | Path `/Volumes/AI_MODELS` exists |

---

## CLI Command Suite

AI OS subcommands are mapped to unified handlers:

### `aios dashboard`
Renders a rich systems dashboard:
- OS Kernel status & Uptime.
- Discovered Ollama model parameters & VRAM footprint.
- Real-time subsystems health state.
- Workspace branch and uncommitted changes.
- Daily sprint targets and task completion metrics.

### `aios work`
Displays workspace engineering context:
- Git status staged/unstaged/untracked files.
- Active sprint name and description.
- Discovered tests, build systems, and active linters.

### `aios today`
Tracks daily work and task plans:
- Today's completed and incomplete tasks.
- Detailed schedule slots.
- Notion synchronization status and workspace lists.

### `aios status`
Renders kernel state, session IDs, and number of active watchers/background tasks.

### `aios restart`
Gracefully stops all running services and watch loops, and performs a complete reboot initialization sequence.

### `aios doctor`
Runs the startup diagnostics health checks and prints recovery recommendations.

### `aios shutdown`
Halts all watchers, terminates background tasks, and exits gracefully.

---

## Test Validation & Verification

A production-quality test suite was added to [test_local_workspace_cli.py](file:///Users/anzarakhtar/aios/core/tests/test_local_workspace_cli.py):
- `TestSessionPersistence`: Verifies load/save caching of workspaces, sprint, and memory.
- `TestDiagnostics`: Verifies real checks for Python, Git, and External HDD status resolution.
- `TestCommandHandlers`: Verifies each subcommand handler (`dashboard`, `work`, `today`, `status`, `restart`, `shutdown`) executes correctly under mocked registry environments.

**Total local test suite: 174/174 passing.**
