from typing import Dict


class ProviderMetricsCollector:
    def __init__(self) -> None:
        self.total_tokens = 0
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.total_cost = 0.0
        self.provider_usage: Dict[str, int] = {}
        self.model_usage: Dict[str, int] = {}

    def record_usage(
        self,
        provider_name: str,
        model_name: str,
        prompt_tokens: int,
        completion_tokens: int,
        cost: float,
    ) -> None:
        self.prompt_tokens += prompt_tokens
        self.completion_tokens += completion_tokens
        self.total_tokens += prompt_tokens + completion_tokens
        self.total_cost += cost
        self.provider_usage[provider_name] = self.provider_usage.get(provider_name, 0) + 1
        self.model_usage[model_name] = self.model_usage.get(model_name, 0) + 1

    def get_summary(self) -> dict:
        return {
            "total_tokens": self.total_tokens,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_cost_usd": self.total_cost,
            "provider_usage": self.provider_usage,
            "model_usage": self.model_usage,
        }
