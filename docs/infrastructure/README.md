# Infrastructure Documentation

> This section documents external service integrations, workflow automation infrastructure, and source control operations.

---

## n8n Workflow Automation

| Document | Purpose |
|---|---|
| [N8N_RUNTIME_STATUS.md](N8N_RUNTIME_STATUS.md) | Current n8n server status and connection health |
| [N8N_RUNTIME_INTEGRATION_REPORT.md](N8N_RUNTIME_INTEGRATION_REPORT.md) | Full n8n integration report: workflows, executions, and validation |

Full n8n operational suite in `docs/n8n/`:
- `N8N_DIAGNOSTICS.md` — n8n connectivity and health diagnostics
- `N8N_EXECUTION_REPORT.md` — Workflow execution report and statistics
- `N8N_HEALTH.md` — n8n service health snapshot
- `N8N_SERVER_INFO.md` — Server version, plugins, and configuration

## Source Control

| Document | Purpose |
|---|---|
| [SOURCE_CONTROL_STATUS.md](SOURCE_CONTROL_STATUS.md) | Git repository health, branch status, and CI pipeline state |

Full source control suite in `docs/source_control/`:
- `BRANCH_REPORT.md` — Branch inventory and protection rules
- `PULL_REQUEST_REPORT.md` — Open/closed PR tracking
- `RELEASE_REPORT.md` — Release history and tag management
- `REPOSITORY_REPORT.md` — Repository statistics and metadata
- `WORKFLOW_REPORT.md` — GitHub Actions workflow summary
- `DIAGNOSTICS.md` — Source control connectivity diagnostics

---

## Related Sections
- [Deployment →](../deployment/README.md)
- [Troubleshooting →](../troubleshooting/README.md)
- [Database →](../database/README.md)
