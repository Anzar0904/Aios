from typing import Dict, List


class ProviderHealthMonitor:
    def __init__(self) -> None:
        self._latencies: Dict[str, List[float]] = {}
        self._failures: Dict[str, int] = {}
        self._successes: Dict[str, int] = {}

    def record_success(self, provider_name: str, latency: float) -> None:
        if provider_name not in self._latencies:
            self._latencies[provider_name] = []
        self._latencies[provider_name].append(latency)
        if len(self._latencies[provider_name]) > 50:
            self._latencies[provider_name].pop(0)

        self._successes[provider_name] = self._successes.get(provider_name, 0) + 1

    def record_failure(self, provider_name: str) -> None:
        self._failures[provider_name] = self._failures.get(provider_name, 0) + 1

    def get_average_latency(self, provider_name: str) -> float:
        lats = self._latencies.get(provider_name, [])
        if not lats:
            return 0.5
        return sum(lats) / len(lats)

    def get_success_rate(self, provider_name: str) -> float:
        success = self._successes.get(provider_name, 0)
        failure = self._failures.get(provider_name, 0)
        total = success + failure
        if total == 0:
            return 1.0
        return success / total

    def is_healthy(self, provider_name: str) -> bool:
        return self.get_success_rate(provider_name) >= 0.5
