# AI Memory Persistence Diagnostics

This document outlines tracing rules, log messages, failover inspection, and diagnostic guidelines.

## 1. Tracing Failures

All persistence actions are logged to `provider_telemetry` and `provider_statistics`. In case of issues:
1. Examine the `provider_failovers` table to find which provider failed and the error message recorded.
2. Cross-reference the `checkpoint_id` in the failover log with the `provider_checkpoints` table to inspect the prompt context during the failure.
3. Check `provider_health` to verify if the provider was rate-limited or marked unhealthy.

## 2. Checkpoints Recovery

If an execution fails midway:
- The checkpoint saves the context and retry attempt count.
- `ResumeManager` can re-load the request state to replay the request or trigger failovers without repeating initial preprocessing.

## 3. Telemetry Inspection

The `provider_telemetry` table stores p95 and average query latencies. Large spikes in average latency indicate backend congestion or api throttling.
