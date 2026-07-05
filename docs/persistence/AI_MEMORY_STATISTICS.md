# AI Memory Persistence Statistics & Costs

This document outlines metrics tracking, cost formulas, latency percentiles, and statistical logs.

## 1. Metrics & Instrumentation

`AIMemoryStatistics` reads operational metrics and aggregates them into persistent statistics logs. It tracks:
- **Total Requests**: Success count + failure count.
- **Success Count**: Total positive responses.
- **Failure Count**: Mapped exceptions and timeouts.
- **Last Error**: Mapped error logs.

## 2. Token Tracker & Cost Estimation

`ProviderTokenUsageTracker` logs daily and monthly tokens consumed by model prompts and completions.

### Cost Formula
The daily/monthly costs are computed dynamically using:
$$\text{Cost} = (\text{Input Tokens} \times \text{Input Rate}) + (\text{Output Tokens} \times \text{Output Rate})$$
Rates are derived from `ProviderMetadata` registered rates per million tokens.

## 3. Latency Metrics

`ProviderLatencyAnalyzer` tracks request execution latencies:
- **Average Latency**: Running mean of latencies.
- **P95 Latency**: 95th percentile latency (useful for identifying outlier bottlenecks).
- Persistent lists of latencies are written as serialized arrays to `provider_telemetry`.
