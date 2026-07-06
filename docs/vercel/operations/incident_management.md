# Incident Management & Alarm Rules Spec
**Sprint 13 · Milestone 5** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define alarm levels, incident states, and diagnosis reporting rules.
* **Scope**: Governs alarm levels, incident logs, and diagnostics.
* **Audience**: Systems Engineers, DBAs, and Lead Developers.
* **Related Documents**:
  * [vercel/operations/logging_analysis.md](file:///Users/anzarakhtar/aios/docs/vercel/operations/logging_analysis.md) - Log analysis.
  * [vercel/operations/monitoring_intelligence.md](file:///Users/anzarakhtar/aios/docs/vercel/operations/monitoring_intelligence.md) - Monitoring.

---

## 1. Alarm Classification & Incidents

The **Incident Management** module handles system alerts:
* **Warning Alarm**: Triggered if latency or memory usage exceeds thresholds (e.g. LCP > 2.5s or function memory > 80%).
* **Critical Alarm**: Triggered if error rates exceed limits (e.g. server error rates > 1%) or DNS routing fails.
* **Incident Lifecycle Tracking**: Logs incidents to SQLite:
  ```sql
  CREATE TABLE IF NOT EXISTS project_incidents (
      incident_id TEXT PRIMARY KEY,
      project_id TEXT NOT NULL,
      severity TEXT CHECK(severity IN ('WARNING', 'CRITICAL')) NOT NULL,
      status TEXT CHECK(status IN ('OPEN', 'INVESTIGATING', 'RESOLVED')) NOT NULL,
      summary TEXT NOT NULL,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      resolved_at TIMESTAMP,
      FOREIGN KEY(project_id) REFERENCES vercel_projects(project_id) ON DELETE CASCADE
  );
  ```
* **Diagnostics Reporting**: Compiles error details, logs, and stack traces to help resolve incidents.
