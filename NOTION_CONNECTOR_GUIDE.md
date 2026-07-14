# Notion Connector Guide

The Notion Connector syncs databases, pages, task lists, and sprint goals into AI OS.

---

## 1. Capabilities

- **Database Discovery**: Discovers associated page blocks and database lists.
- **Task Synchronization**: Unifies local `.agent/tasks.json` with remote Notion Task databases.
- **Goal Alignment**: Syncs sprint goals and milestones.

---

## 2. CLI Invocation

To authenticate and trigger syncs:

```bash
# Connect using integration secret token
aios integrations connect notion integration_token secret_notion_api_val

# Trigger task and goal synchronization
aios integrations sync notion
```
