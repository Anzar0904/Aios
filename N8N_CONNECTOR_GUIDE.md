# n8n Connector Guide

The n8n Connector integrates active workflow engines, execution trackers, and webhooks endpoints.

---

## 1. Capabilities

- **Workflow Discovery**: Connects to n8n api to catalog active workflows.
- **Execution Auditing**: Logs execution latency averages and failure stages.
- **Webhook Syncing**: Dynamically maps webhook triggers and registers them to the Universal Knowledge Graph.

---

## 2. CLI Invocation

To authenticate and trigger syncs:

```bash
# Connect using API key
aios integrations connect n8n api_key n8n_api_key_value_here

# Trigger manual synchronization
aios integrations sync n8n
```
