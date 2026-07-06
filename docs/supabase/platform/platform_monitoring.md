# Platform Monitoring Spec
**Sprint 12 · Milestone 4** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define API metrics parsing, log checks, and alert triggers.
* **Scope**: Governs metrics caches, syslog readers, and database loggers.
* **Audience**: Systems Engineers, DBAs, and Lead Developers.
* **Related Documents**:
  * [supabase/database/database_health.md](file:///Users/anzarakhtar/aios/docs/supabase/database/database_health.md) - Database health.
  * [supabase/platform/platform_health.md](file:///Users/anzarakhtar/aios/docs/supabase/platform/platform_health.md) - Platform health.

---

## 1. Metrics Auditing

The **Platform Monitoring** engine retrieves and analyzes system logs from the Supabase API Gateway (Kong) and database:
* **API Latency**: Monitors response times, flagging queries or API calls that exceed **1000ms**.
* **Deno Memory Consumption**: Checks memory usage logs, flagging edge functions approaching Deno's **150MB** limit.
* **HTTP Error Rates**: Tracks HTTP 5xx error volumes, warning if rates exceed **1%** of total traffic.

---

## 2. Syslog Analysis

Background tasks parse log records:
* **Database Errors**: Scans Postgres error logs for transaction terminations or deadlock issues.
* **Realtime Connections**: Tracks active WebSocket connections, monitoring client limits.
* **Alert Logging**: Logs warnings to `docs/supabase/scratch/platform_alerts.log`.
