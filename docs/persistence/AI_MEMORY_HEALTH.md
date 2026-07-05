# AI Memory Persistence Health Specifications

This document defines health monitoring policies, circuit breaker behaviors, rate limits, cooldown durations, and availability indicators.

## 1. Health Mappings & Checks

The health state of each provider is computed dynamically inside `ProviderHealthMonitor.is_healthy` and persisted to the `provider_health` repository table.

```python
healthy = (not rate_limited) and (not quota_exhausted) and (success_rate >= 0.5)
```

## 2. Circuit Breaker States

- **CLOSED**: Default state when the provider is online. Success rates are above 50% and no limits are hit.
- **OPEN**: Tripped state. The circuit breaker is open when a provider fails consecutively more than 3 times (threshold configuration). Operations are automatically diverted to fallback adapters.

## 3. Cooldown and Rate Limit Handling

When a provider is rate limited (e.g., HTTP 429), `ProviderRateLimitManager` records a cooldown timestamp (default 60 seconds or custom `Retry-After`). The provider is skipped during model selection until the cooldown expires.

## 4. Quota Enforcement

- Daily/monthly budgets are tracked by `ProviderQuotaManager`.
- If budget limit is exceeded, the provider is marked as exhausted, and all subsequent calls are failed-over immediately.
