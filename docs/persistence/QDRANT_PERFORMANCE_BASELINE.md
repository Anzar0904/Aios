# Qdrant Performance Baseline Report

This baseline records operation durations gathered over 100 benchmark iterations.

---

## 1. Latency Profile (ms)

| Operation | Average | P50 | P95 | P99 |
| :--- | :--- | :--- | :--- | :--- |
| **Ping Connection** | 0.002 | 0.002 | 0.004 | 0.005 |
| **Embedding Generation** | 1.678 | 1.618 | 2.580 | 3.047 |
| **Vector Search** | 2.920 | 2.824 | 3.766 | 12.227 |
| **CRUD Upsert** | 2.661 | 2.423 | 3.622 | 14.871 |

---

## 2. Telemetry Summaries
- **Search Throughput**: 342.5 queries/sec
- **Cache Hits**: Reused calculations returned in 0.010ms
