# Qdrant Performance Baseline Report

This baseline records operation durations gathered over 100 benchmark iterations.

---

## 1. Latency Profile (ms)

| Operation | Average | P50 | P95 | P99 |
| :--- | :--- | :--- | :--- | :--- |
| **Ping Connection** | 0.000 | 0.000 | 0.000 | 0.001 |
| **Embedding Generation** | 0.349 | 0.326 | 0.468 | 0.588 |
| **Vector Search** | 0.955 | 0.621 | 3.567 | 4.922 |
| **CRUD Upsert** | 1.195 | 0.550 | 6.062 | 11.610 |

---

## 2. Telemetry Summaries
- **Search Throughput**: 1046.6 queries/sec
- **Cache Hits**: Reused calculations returned in 0.004ms
