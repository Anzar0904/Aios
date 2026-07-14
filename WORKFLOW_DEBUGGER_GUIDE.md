# Workflow Debugger Guide

The Workflow Debugger scans execution logs, credential fields, and webhook configurations to auto-repair node configuration issues.

---

## 1. Diagnostic Checks

Running `aios workflow diagnose <id>` executes:
- **Webhook Check**: Asserts if nodes tracking HTTP webhooks define webhook URLs. Raises `MISSING_WEBHOOK_URL` error if blank.
- **Credential Check**: Asserts if nodes (Notion, Slack, Gmail, GitHub) reference credential configs. Raises `EMPTY_CREDENTIALS` warning if missing.

---

## 2. Auto-Repair Engine

Running `aios workflow repair <id>` attempts to fix identified issues automatically:

### Webhook Repairs
- **Problem**: Missing Webhook URL (`MISSING_WEBHOOK_URL`).
- **Solution**: Auto-assigns a local webhook endpoint (`http://localhost:5678/webhook/<id>`).

### Credential Repairs
- **Problem**: Empty Credentials (`EMPTY_CREDENTIALS`).
- **Solution**: Injects a temporary development credential key (`dev-key-temp-aios`) into the node parameters list.

---

## 3. CLI Commands Reference

```bash
# Run diagnostics on a workflow
aios workflow diagnose <workflow_id>

# Auto-repair identified workflow issues
aios workflow repair <workflow_id>
```
