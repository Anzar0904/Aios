# Qdrant Performance Baseline Report

This baseline records operation durations gathered over 100 benchmark iterations.

---

## 1. Latency Profile (ms)

| Operation | Average | P50 | P95 | P99 |
| :--- | :--- | :--- | :--- | :--- |
| **Ping Connection** | 0.001 | 0.000 | 0.002 | 0.003 |
| **Embedding Generation** | 0.563 | 0.606 | 0.728 | 1.114 |
| **Vector Search** | 5.109 | 1.644 | 2.815 | 338.769 |
| **CRUD Upsert** | 1.459 | 1.351 | 1.985 | 13.780 |

---

## 2. Telemetry Summaries
- **Search Throughput**: 195.7 queries/sec
- **Cache Hits**: Reused calculations returned in 0.008ms
