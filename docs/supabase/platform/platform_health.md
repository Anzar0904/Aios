# Platform Health & Diagnostics Spec
**Sprint 12 · Milestone 4** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define system health metrics, connection pools thresholds, and automated repair tasks.
* **Scope**: Governs health limits, diagnostic tasks, and failovers.
* **Audience**: Systems Engineers, DBAs, and Lead Developers.
* **Related Documents**:
  * [supabase/capabilities.md](file:///Users/anzarakhtar/aios/docs/supabase/capabilities.md) - Capabilities.
  * [supabase/platform/platform_monitoring.md](file:///Users/anzarakhtar/aios/docs/supabase/platform/platform_monitoring.md) - Platform monitoring.

---

## 1. Platform Health Indicators

The **Platform Health** module monitors system metrics to ensure overall performance:

```
+------------------------------------+------------------------------------+----------+
| Health Indicator                   | Target Range                       | Priority |
+------------------------------------+------------------------------------+----------+
| 1. Database Connection Pool        | < 80% pool utilization             | High     |
+------------------------------------+------------------------------------+----------+
| 2. Deno Function Executions        | 0 compilation/bundle errors        | High     |
+------------------------------------+------------------------------------+----------+
| 3. Storage Usage Limit             | < 90% project storage tier         | Medium   |
+------------------------------------+------------------------------------+----------+
| 4. Network Gateway Latency         | < 150ms handshake latency          | High     |
+------------------------------------+------------------------------------+----------+
```

---

## 2. Automated Diagnostics

* **Pool Inspector**: Checks active database connection counts, flagging if they approach maximum limits.
* **Storage Checker**: Audits total storage usage, flagging projects approaching their tier limits.

---

## 3. Maintenance & Recovery Tasks

If metrics exceed limits:
1. **Connection Pool Reset**: Issues a pool reset command if connection locks are detected.
2. **Old Deployments Purge**: Deletes historical Deno function deployment logs to free storage.
3. **Storage Eviction**: Evicts temporary files from storage buckets to free space.
