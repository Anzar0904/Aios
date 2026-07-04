import time
from typing import Dict, List, Optional, Any

from aios.providers.models import ProviderStatus, DIInitializeMixin


class ProviderTokenUsageTracker(DIInitializeMixin):
    """Tracks daily and monthly input/output token counts."""

    def __init__(self) -> None:
        self._daily_input: Dict[str, int] = {}
        self._daily_output: Dict[str, int] = {}
        self._monthly_input: Dict[str, int] = {}
        self._monthly_output: Dict[str, int] = {}

    def record_tokens(self, provider_name: str, input_tokens: int, output_tokens: int) -> None:
        self._daily_input[provider_name] = self._daily_input.get(provider_name, 0) + input_tokens
        self._daily_output[provider_name] = self._daily_output.get(provider_name, 0) + output_tokens
        self._monthly_input[provider_name] = self._monthly_input.get(provider_name, 0) + input_tokens
        self._monthly_output[provider_name] = self._monthly_output.get(provider_name, 0) + output_tokens

    def get_usage(self, provider_name: str) -> Dict[str, int]:
        return {
            "daily_input": self._daily_input.get(provider_name, 0),
            "daily_output": self._daily_output.get(provider_name, 0),
            "monthly_input": self._monthly_input.get(provider_name, 0),
            "monthly_output": self._monthly_output.get(provider_name, 0),
        }


class ProviderLatencyAnalyzer(DIInitializeMixin):
    """Tracks and calculates latency history statistics."""

    def __init__(self) -> None:
        self._latencies: Dict[str, List[float]] = {}

    def record_latency(self, provider_name: str, latency: float) -> None:
        if provider_name not in self._latencies:
            self._latencies[provider_name] = []
        self._latencies[provider_name].append(latency)
        if len(self._latencies[provider_name]) > 100:
            self._latencies[provider_name].pop(0)

    def get_average_latency(self, provider_name: str) -> float:
        lats = self._latencies.get(provider_name, [])
        return sum(lats) / len(lats) if lats else 0.5

    def get_p95_latency(self, provider_name: str) -> float:
        lats = sorted(self._latencies.get(provider_name, []))
        if not lats:
            return 0.5
        idx = int(len(lats) * 0.95)
        return lats[idx]


class ProviderCostAnalyzer(DIInitializeMixin):
    """Computes cost model values based on token rates."""

    def __init__(self, registry: Any) -> None:
        self._registry = registry
        self._costs: Dict[str, float] = {}

    def estimate_cost(self, provider_name: str, input_tokens: int, output_tokens: int) -> float:
        if not self._registry:
            return 0.0
        meta = self._registry.get_provider(provider_name)
        if not meta:
            return 0.0
        return (input_tokens * meta.cost_per_million_input / 1_000_000.0) + (
            output_tokens * meta.cost_per_million_output / 1_000_000.0
        )

    def record_cost(self, provider_name: str, cost: float) -> None:
        self._costs[provider_name] = self._costs.get(provider_name, 0.0) + cost

    def get_total_cost(self, provider_name: str) -> float:
        return self._costs.get(provider_name, 0.0)


class ProviderSuccessAnalyzer(DIInitializeMixin):
    """Tracks positive requests execution counts and timestamps."""

    def __init__(self) -> None:
        self._successes: Dict[str, int] = {}
        self._timestamps: Dict[str, float] = {}

    def record_success(self, provider_name: str) -> None:
        self._successes[provider_name] = self._successes.get(provider_name, 0) + 1
        self._timestamps[provider_name] = time.time()

    def get_success_count(self, provider_name: str) -> int:
        return self._successes.get(provider_name, 0)

    def get_last_success_time(self, provider_name: str) -> float:
        return self._timestamps.get(provider_name, 0.0)


class ProviderFailureAnalyzer(DIInitializeMixin):
    """Tracks failed request executions and stores log details."""

    def __init__(self) -> None:
        self._failures: Dict[str, int] = {}
        self._timestamps: Dict[str, float] = {}
        self._error_logs: Dict[str, List[str]] = {}

    def record_failure(self, provider_name: str, error_message: str) -> None:
        self._failures[provider_name] = self._failures.get(provider_name, 0) + 1
        self._timestamps[provider_name] = time.time()
        if provider_name not in self._error_logs:
            self._error_logs[provider_name] = []
        self._error_logs[provider_name].append(error_message)

    def get_failure_count(self, provider_name: str) -> int:
        return self._failures.get(provider_name, 0)

    def get_last_failure_time(self, provider_name: str) -> float:
        return self._timestamps.get(provider_name, 0.0)


class ProviderRateLimitManager(DIInitializeMixin):
    """Manages provider rate limit cooldown parameters."""

    def __init__(self) -> None:
        self._cooldowns: Dict[str, float] = {}

    def trigger_rate_limit(self, provider_name: str, retry_after: float = 60.0) -> None:
        self._cooldowns[provider_name] = time.time() + retry_after

    def is_rate_limited(self, provider_name: str) -> bool:
        cooldown = self._cooldowns.get(provider_name, 0.0)
        return time.time() < cooldown


class ProviderQuotaManager(DIInitializeMixin):
    """Monitors daily/monthly budget quotas and raises failover triggers."""

    def __init__(self) -> None:
        self._quota_limits: Dict[str, float] = {
            "openai": 10.0,
            "claude_code": 10.0,
            "gemini_cli": 10.0,
        }
        self._quota_used: Dict[str, float] = {}

    def record_cost(self, provider_name: str, cost: float) -> None:
        self._quota_used[provider_name] = self._quota_used.get(provider_name, 0.0) + cost

    def is_quota_exhausted(self, provider_name: str) -> bool:
        limit = self._quota_limits.get(provider_name, 10.0)
        used = self._quota_used.get(provider_name, 0.0)
        return used >= limit

    def get_remaining_quota(self, provider_name: str) -> float:
        limit = self._quota_limits.get(provider_name, 10.0)
        used = self._quota_used.get(provider_name, 0.0)
        return max(0.0, limit - used)


class ProviderHealthMonitor(DIInitializeMixin):
    """Consolidated provider health, latency, rate limits, and quota manager."""

    def __init__(self, registry: Optional[Any] = None) -> None:
        self.latency_analyzer = ProviderLatencyAnalyzer()
        self.cost_analyzer = ProviderCostAnalyzer(registry)
        self.success_analyzer = ProviderSuccessAnalyzer()
        self.failure_analyzer = ProviderFailureAnalyzer()
        self.rate_limit_manager = ProviderRateLimitManager()
        self.quota_manager = ProviderQuotaManager()
        self.token_usage = ProviderTokenUsageTracker()

    def record_success(self, provider_name: str, latency: float) -> None:
        self.latency_analyzer.record_latency(provider_name, latency)
        self.success_analyzer.record_success(provider_name)

    def record_failure(self, provider_name: str, error_message: str = "Unknown error") -> None:
        self.failure_analyzer.record_failure(provider_name, error_message)

    def get_average_latency(self, provider_name: str) -> float:
        return self.latency_analyzer.get_average_latency(provider_name)

    def get_success_rate(self, provider_name: str) -> float:
        success = self.success_analyzer.get_success_count(provider_name)
        failure = self.failure_analyzer.get_failure_count(provider_name)
        total = success + failure
        if total == 0:
            return 1.0
        return success / total

    def get_availability_pct(self, provider_name: str) -> float:
        return self.get_success_rate(provider_name) * 100.0

    def is_healthy(self, provider_name: str) -> bool:
        if self.rate_limit_manager.is_rate_limited(provider_name):
            return False
        if self.quota_manager.is_quota_exhausted(provider_name):
            return False
        return self.get_success_rate(provider_name) >= 0.5
