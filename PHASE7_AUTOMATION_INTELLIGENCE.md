# Phase 7: n8n Automation Intelligence

> **Status:** ✅ Production — 18/18 Tests passing

## Overview

Phase 7 establishes the **Automation Intelligence Layer** for the AI OS, transforming it into an autonomous workflow operating system. It enables generating, deploying, versioning, monitoring, diagnosing, and auto-repairing n8n automation workflows.

All automation entities (`Workflow`, `Deployment`, `Webhook`, `Execution`, `Credential`, `WorkflowTemplate`) are mapped natively into the Universal Knowledge Graph using BELONGS_TO, SERVES, USES, DEPLOYED_BY, EXECUTES, and CALLS relationships.

---

## Subsystems

1. **Workflow Registry Service**: Central catalog managing active workflow nodes, connections, webhooks, version numbers, and health scores.
2. **n8n Service Layer**: Integration adapter simulating trigger/node configurations, deactivation, and executions.
3. **Workflow Generator**: Procedural blueprint assembler creating complete setups for Lead Gen, Outreach, CRM Sync, social media, and DevOps from prompts.
4. **Workflow Deployment Engine**: Deploys verified JSON workflows, validating syntax structure, trigger counts, and credential links.
5. **Live Deployment Notification Alert**: Displays terminal notifications immediately upon deployment.
6. **Workflow Monitor**: Logs latency, node errors, retry counters, and computes running health scores.
7. **Workflow Debugger**: Scans configurations to diagnose failures (e.g. empty credential fields, webhook errors) and runs auto-repairs.
8. **Workflow Versioning**: Stores revision histories and supports rolling back configurations to specific previous deployments.

---

## Database Schemas

See [WORKFLOW_REGISTRY_GUIDE.md](file:///Users/anzarakhtar/aios/WORKFLOW_REGISTRY_GUIDE.md) for full SQLite specifications.

---

## CLI Command Summary

```bash
aios workflows                       # Render active workflows and execution stats
aios workflow dashboard              # Render active workflows and execution stats (alias)
aios workflow generate <name> <tpl>  # Generate a workflow from templates catalog
aios workflow deploy <name> <json>   # Validate and deploy raw JSON configuration
aios workflow activate <id>          # Activate workflow trigger events
aios workflow deactivate <id>        # Deactivate workflow triggers
aios workflow diagnose <id>          # Run diagnostics and report credential/node issues
aios workflow repair <id>            # Auto-repair credential or webhook parameters
aios workflow versions <id>          # View deployment history and rollbacks list
aios workflow rollback <id> <ver>    # Revert workflow configuration to specific version
```
