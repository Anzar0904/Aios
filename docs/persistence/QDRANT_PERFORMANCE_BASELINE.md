# Qdrant Performance Baseline Report

This baseline records operation durations gathered over 100 benchmark iterations.

---

## 1. Latency Profile (ms)

| Operation | Average | P50 | P95 | P99 |
| :--- | :--- | :--- | :--- | :--- |
| **Ping Connection** | 0.001 | 0.001 | 0.002 | 0.003 |
| **Embedding Generation** | 1.084 | 1.066 | 1.276 | 1.728 |
| **Vector Search** | 2.305 | 2.189 | 3.199 | 6.309 |
| **CRUD Upsert** | 2.102 | 1.700 | 5.737 | 12.840 |

---

## 2. Telemetry Summaries
- **Search Throughput**: 433.8 queries/sec
- **Cache Hits**: Reused calculations returned in 0.006ms
