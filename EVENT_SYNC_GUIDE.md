# Event Sync Guide

All connectors emit event streams upon synchronization or webhooks reception, dispatching data across the AI OS.

---

## 1. Event Propagation Pipeline

```mermaid
graph TD
    Connector[Connector Sync / Webhook] --> Event[Emit IntegrationEvent]
    Event --> DB[Log in SQLite event table]
    Event --> Graph[KG Bridge: Emit Node and link via EMITS]
    Event --> Bus[Universal Event Bus Notify]
    Event --> Alert[Notification Center Warning Alerts]
    Event --> UI[Render in Integrations Status CLI Dashboard]
```

---

## 2. Event Types

- **GitHubPush**: Repository code push.
- **GitHubPR**: New Pull Request issue opened.
- **NotionPageCreated**: New Notion page.
- **WorkflowDeployed**: Successfully deployed n8n workflow.
- **CalendarEventCreated**: Meeting booked.
- **EmailReceived**: Inbox message.
- **SlackMessage**: Channel update.
- **TelegramMessage**: Bot notification.

---

## 3. History Auditing

Verify recent sync events in the integrations dashboard:
`aios integrations status`
