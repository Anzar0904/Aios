# Workflow Deployment Guide

The Workflow Deployment Engine ensures that deployed JSON configurations match n8n node formats, check triggers, and register credentials cleanly.

---

## 1. Deployment Validation Checks

When a workflow is deployed via `aios workflow deploy`:
1. **JSON Validation**: Checks raw string parsing using standard parser checks.
2. **Node Presence**: Validates that at least one functional node block exists.
3. **Trigger Analysis**: Scans node types looking for Cron (`cron`), Webhook (`webhook`), Google Sheets, or GitHub triggers. Logs trigger counts to metadata.
4. **Credential Links**: Scans parameters looking for credential objects. If empty, logs a diagnostic warning.

---

## 2. Instant Deployment Notification Alert

Whenever a workflow is deployed successfully, the CLI engine displays a terminal notification:

```
+-----------------------------------------------+
| WORKFLOW DEPLOYED                             |
|                                               |
| Workflow:   Lead Generation System            |
| Status:     Healthy                           |
| Webhook:    Available (http://...)            |
| Project:    Agency                            |
| Client:     ABC Company                       |
| Deployment: Success                           |
+-----------------------------------------------+
```

---

## 3. Deployment CLI Reference

```bash
# Deploy a workflow from a raw JSON configuration
aios workflow deploy "My Pipeline" '{"nodes": [{"name": "My Cron", "type": "n8n-nodes-base.cron"}]}'
```
