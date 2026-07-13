# Qdrant Performance Baseline Report

This baseline records operation durations gathered over 100 benchmark iterations.

---

## 1. Latency Profile (ms)

| Operation | Average | P50 | P95 | P99 |
| :--- | :--- | :--- | :--- | :--- |
| **Ping Connection** | 0.001 | 0.001 | 0.002 | 0.004 |
| **Embedding Generation** | 1.072 | 0.998 | 1.464 | 1.549 |
| **Vector Search** | 2.240 | 2.198 | 2.868 | 3.644 |
| **CRUD Upsert** | 2.099 | 1.819 | 3.500 | 15.285 |

---

## 2. Telemetry Summaries
- **Search Throughput**: 446.4 queries/sec
- **Cache Hits**: Reused calculations returned in 0.007ms
