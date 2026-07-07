# Qdrant Performance Baseline Report

This baseline records operation durations gathered over 100 benchmark iterations.

---

## 1. Latency Profile (ms)

| Operation | Average | P50 | P95 | P99 |
| :--- | :--- | :--- | :--- | :--- |
| **Ping Connection** | 0.001 | 0.001 | 0.002 | 0.003 |
| **Embedding Generation** | 0.962 | 0.961 | 1.178 | 1.194 |
| **Vector Search** | 2.254 | 2.251 | 3.042 | 3.607 |
| **CRUD Upsert** | 2.017 | 1.844 | 2.403 | 17.399 |

---

## 2. Telemetry Summaries
- **Search Throughput**: 443.7 queries/sec
- **Cache Hits**: Reused calculations returned in 0.006ms
