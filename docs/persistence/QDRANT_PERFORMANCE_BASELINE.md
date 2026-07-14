# Qdrant Performance Baseline Report

This baseline records operation durations gathered over 100 benchmark iterations.

---

## 1. Latency Profile (ms)

| Operation | Average | P50 | P95 | P99 |
| :--- | :--- | :--- | :--- | :--- |
| **Ping Connection** | 0.001 | 0.001 | 0.002 | 0.004 |
| **Embedding Generation** | 1.040 | 0.993 | 1.435 | 1.658 |
| **Vector Search** | 2.727 | 2.538 | 3.160 | 19.255 |
| **CRUD Upsert** | 2.250 | 2.044 | 2.815 | 15.732 |

---

## 2. Telemetry Summaries
- **Search Throughput**: 366.6 queries/sec
- **Cache Hits**: Reused calculations returned in 0.008ms
