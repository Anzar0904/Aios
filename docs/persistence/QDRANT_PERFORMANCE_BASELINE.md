# Qdrant Performance Baseline Report

This baseline records operation durations gathered over 100 benchmark iterations.

---

## 1. Latency Profile (ms)

| Operation | Average | P50 | P95 | P99 |
| :--- | :--- | :--- | :--- | :--- |
| **Ping Connection** | 0.000 | 0.000 | 0.001 | 0.002 |
| **Embedding Generation** | 0.378 | 0.343 | 0.492 | 0.549 |
| **Vector Search** | 1.539 | 1.504 | 1.941 | 3.222 |
| **CRUD Upsert** | 1.411 | 1.223 | 1.667 | 17.518 |

---

## 2. Telemetry Summaries
- **Search Throughput**: 649.7 queries/sec
- **Cache Hits**: Reused calculations returned in 0.003ms
