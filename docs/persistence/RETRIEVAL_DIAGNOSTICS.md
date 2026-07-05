# Retrieval Diagnostics & Health Documentation

This document describes the health checks, error logging, and diagnostic recommendations for the Hybrid Retrieval service in the Personal AI OS.

---

## 1. Health Monitoring

The `HybridRetrievalServiceImpl.get_health()` method verifies the overall status of the pipeline:

```json
{
  "status": "HEALTHY",
  "failures_recorded": 0
}
```

If error counts exceed tolerance thresholds or remote connections fail, status degrades to `DEGRADED`.

---

## 2. Diagnostics & Alerts

The `get_diagnostics()` method exposes active errors and warnings:

```json
{
  "alerts": [
    {
      "message": "Qdrant query failed: Connection refused",
      "timestamp": 1719876251.2
    }
  ]
}
```

---

## 3. Dynamic Recommendations

The `get_recommendations()` method runs rule-based analysis over cache and latency telemetry:

1. **Category**: `retrieval_cache`
   * *Issue*: "Retrieval cache hit ratio is low (<50%)."
   * *Remediation*: "Increase cache TTL or warm up cache for frequent queries."
   * *Severity*: `WARNING`

2. **Category**: `hybrid_retrieval`
   * *Issue*: "Average retrieval latency is high (>200ms)."
   * *Remediation*: "Tune Qdrant indexing parameters (e.g. HNSW index) or reduce candidate recall limits."
   * *Severity*: `WARNING`

---

## 4. Troubleshooting Fallback Paths

When Qdrant queries fail (e.g. socket offline or collection errors), the pipeline automatically degrades to:
* **Lexical fallback**: Executing full-text pattern match query (`LIKE %query%`) against local SQLite/PostgreSQL `ai_memory` table.
* **Alerting**: Logging the primary failure to the `_errors` diagnostics queue while returning fallback records with static scores (`0.5`).
