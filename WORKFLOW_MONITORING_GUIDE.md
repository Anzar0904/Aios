# Workflow Monitoring Guide

The Workflow Monitor logs execution results, latency patterns, and node errors to determine overall pipeline health.

---

## 1. Execution Audits

Execution metadata is registered in the database for post-run analysis:

```sql
CREATE TABLE executions (
    execution_id     TEXT PRIMARY KEY,
    workflow_id      TEXT NOT NULL,
    status           TEXT NOT NULL DEFAULT 'running',
    latency_ms       INTEGER NOT NULL DEFAULT 0,
    error_message    TEXT NOT NULL DEFAULT '',
    failed_node      TEXT NOT NULL DEFAULT '',
    timestamp        REAL NOT NULL
);
```

### Metrics Tracked:
- **Latency (ms)**: Run time measurements to catch processing delays.
- **Failed Node**: The exact step where execution halted.
- **Error Message**: Raw trace logs.

---

## 2. Health Score System

The workflow health score is updated automatically upon every execution logging event:

$$\text{Health Score} = \left( \frac{\text{Total Executions} - \text{Failed Executions}}{\text{Total Executions}} \right) \times 100$$

- **100% Health**: All runs completed successfully.
- **Under 50% Health**: Trigger alerts are dispatched to the Notification Center.

---

## 3. Monitoring CLI Reference

```bash
# View list of active workflows and their health scores
aios workflows
```
