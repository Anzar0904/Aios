# Workflow Architecture Diagram

```mermaid
graph TD
  Webhook_Trigger --> PostgreSQL_Insert
  PostgreSQL_Insert --> Slack_Notify
```
