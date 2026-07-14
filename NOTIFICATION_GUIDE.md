# Notification Center Guide

The **Notification Center** aggregates telemetry, logs, and alerts from all running AI OS subsystems. It ensures that background completions, deployment alerts, and workflow failures are visible to the user.

## Core Features
1. **Unread Badging**: Pinned status indicators count unread alerts across workspaces.
2. **Filtering**: Supports category filtering to isolate alerts.
3. **Read Tracking**: Marks alerts as read upon entering the workspace.
4. **Prioritization**: Categorizes alerts into low, medium, and high priorities.

## Notification Categories

* **workflow**: n8n deployment logs and automation run alerts.
* **agent**: Agent task completion or execution error notifications.
* **github**: Pull request opened, build failure, or issue creation alerts.
* **research**: Research synthesis completed notifications.
* **proposal**: Proposal drafts compiled by the Agency Agent.
* **meeting**: Calendar and meeting follow-up reminders.

## Persistence Schema

Notifications are stored in `.agent/notifications.json`:

```json
[
  {
    "notification_id": "8b51d451-b8ef-4c60-a232-1b0f541b5139",
    "title": "Agent Completed Task",
    "message": "agent_software completed task 'Develop CRM Codebase' in 4.2s.",
    "category": "agent",
    "priority": "high",
    "read": false,
    "timestamp": 1784051048.225
  }
]
```

## Python API Usage

To publish an alert from any service or module:

```python
from aios.registry import ServiceRegistry
from aios.services.ux_platform import UXPlatform

ux = ServiceRegistry._global_registry.get(UXPlatform)
ux.add_notification(
    title="Workflow Deployed",
    message="Wayne enterprises sync workflow v1.2 active",
    category="workflow",
    priority="high"
)
```

## CLI Usage

To inspect the notification alerts:
```bash
aios notifications
```
This renders a table of all notifications, their categories, priorities, message details, and read statuses.
