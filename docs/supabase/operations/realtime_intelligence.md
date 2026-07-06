# Realtime Intelligence & Configuration State Spec
**Sprint 12 · Milestone 5** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define Realtime WebSocket parameters, replication configurations, and state drift abstractions.
* **Scope**: Governs WebSocket channels, replication tables, and state models.
* **Audience**: Systems Architects, DBAs, and Lead Developers.
* **Related Documents**:
  * [supabase/capabilities.md](file:///Users/anzarakhtar/aios/docs/supabase/capabilities.md) - Capabilities.
  * [supabase/operations/README.md](file:///Users/anzarakhtar/aios/docs/supabase/operations/README.md) - Operations navigation hub.

---

## 1. The Managed Resource State Abstraction

To track and resolve database operational issues, the AI OS uses a structured state evaluation pipeline:

```
[Managed Resource]
        |
        +---> Configuration: Settings parameters.
        +---> Desired State: Expected configuration defined in local settings.
        +---> Observed State: Actual configuration parsed from Supabase.
        |
        v
[Compute Health & Drift] ===> Analyze performance status and discrepancies
        |
        v
[Recommendation] ===> Generate SQL/API remediation commands
        |
        v
[Execution Plan] ===> Apply changes via dry-run checked migrations
```

---

## 2. Realtime Channel Auditing

The **Realtime Intelligence** module inspects and audits WebSocket subscription configurations:
* **Replication Tables**: Queries database replication configurations to verify table subscription states:
  ```sql
  SELECT source, table_name, active FROM pg_publication_tables 
  WHERE pubname = 'supabase_realtime';
  ```
* **Active Client Metrics**: Monitors active WebSocket connection counts, flagging projects approaching maximum limits.
* **Metadata Logging**: Maps publication details to the SQLite database, updating the catalog.
