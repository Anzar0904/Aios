# Qdrant Performance Baseline Report

This baseline records operation durations gathered over 100 benchmark iterations.

---

## 1. Latency Profile (ms)

| Operation | Average | P50 | P95 | P99 |
| :--- | :--- | :--- | :--- | :--- |
| **Ping Connection** | 0.002 | 0.002 | 0.003 | 0.003 |
| **Embedding Generation** | 1.251 | 1.252 | 1.689 | 1.886 |
| **Vector Search** | 2.649 | 2.446 | 3.861 | 11.078 |
| **CRUD Upsert** | 2.310 | 2.062 | 3.149 | 16.025 |

---

## 2. Telemetry Summaries
- **Search Throughput**: 377.5 queries/sec
- **Cache Hits**: Reused calculations returned in 0.007ms
