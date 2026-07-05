# Automation Persistence Diagnostics Report

This document details diagnostic check routines for verifying schema configurations and policy constraints in the Automation Persistence subsystem.

## 1. Schema Drift Verification
To verify tables:
```sql
SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'workflow_%';
```
Exposes:
- `workflow_executions`
- `workflow_monitoring`
- `workflow_optimizations`
- `workflow_versions`
- `workflow_translations`
- `workflow_integrations`

## 2. Policy Violations Checks
* **STRICT Policy**: Ensures connection timeouts or missing entity requests immediately abort execution with a `RuntimeError`.
* **BEST_EFFORT Policy**: Degrades gracefully, logging exceptions and falling back to memory caching context.
