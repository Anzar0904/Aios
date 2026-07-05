# Redis Performance Baseline Report

This baseline records operation durations gathered over 100 benchmark iterations.

---

## 1. Latency Profile (ms)

| Operation | Average | P50 | P95 | P99 |
| :--- | :--- | :--- | :--- | :--- |
| **Connection Ping** | 0.038 | 0.032 | 0.068 | 0.075 |
| **Cache SET** | 0.049 | 0.045 | 0.080 | 0.097 |
| **Cache GET** | 0.046 | 0.042 | 0.074 | 0.092 |
| **Cache DELETE** | 0.040 | 0.035 | 0.069 | 0.090 |
| **Coordination Lock** | 0.173 | 0.150 | 0.290 | 0.346 |
| **Queue Operations** | 0.248 | 0.212 | 0.424 | 0.525 |
| **Rate Limiter Check** | 0.088 | 0.078 | 0.143 | 0.170 |

---

## 2. Telemetry Summaries
- **Average Combined Latency**: 0.097 ms
- **Command Throughput**: 10258.0 ops/sec
- **Connection Pool Utilization**: 10%
