import time
from typing import Any, Iterator

from aios.providers.config import ProviderConfig
from aios.providers.health import ProviderHealthMonitor
from aios.providers.metrics import ProviderMetricsCollector
from aios.providers.registry import ProviderRegistry
from aios.providers.selector import ProviderSelector
from aios.services.model import LLMRequest, LLMResponse


class ProviderRouter:
    def __init__(
        self,
        config: ProviderConfig,
        registry: ProviderRegistry,
        health_monitor: ProviderHealthMonitor,
        metrics: ProviderMetricsCollector,
        provider_factory: Any,
    ) -> None:
        self.config = config
        self.registry = registry
        self.health_monitor = health_monitor
        self.metrics = metrics
        self.provider_factory = provider_factory
        self.selector = ProviderSelector(config, registry, health_monitor)

    def route_request(self, request: LLMRequest) -> LLMResponse:
        required_len = len(request.prompt) // 4 + 100

        tried_providers = set()

        while len(tried_providers) < len(self.registry.list_providers()):
            p_name, model_name = self.selector.select_best_provider(request, required_len)

            if p_name in tried_providers:
                found_new = False
                for fallback_p in self.config.fallback_chain:
                    if fallback_p not in tried_providers:
                        p_name = fallback_p
                        p_info = self.registry.get_provider(p_name)
                        if p_info:
                            if p_info.is_local:
                                model_name = self.config.preferred_local_model
                            else:
                                model_name = self.config.preferred_remote_model
                            found_new = True
                            break
                if not found_new:
                    break

            tried_providers.add(p_name)

            mapped_name = p_name
            if p_name == "anthropic":
                mapped_name = "claude"
            try:
                provider = self.provider_factory.get_provider(mapped_name)
            except Exception:
                continue

            request.model_name = model_name

            start_time = time.time()
            try:
                response = provider.generate(request)
                latency = time.time() - start_time
                self.health_monitor.record_success(p_name, latency)

                p_info = self.registry.get_provider(p_name)
                cost = 0.0
                prompt_tokens = response.usage.get("prompt_tokens", 0)
                comp_tokens = response.usage.get("completion_tokens", 0)
                if p_info:
                    cost = (prompt_tokens * p_info.cost_per_million_input / 1_000_000) + (
                        comp_tokens * p_info.cost_per_million_output / 1_000_000
                    )

                self.metrics.record_usage(p_name, model_name, prompt_tokens, comp_tokens, cost)
                return response
            except Exception:
                self.health_monitor.record_failure(p_name)
                continue

        mock_provider = self.provider_factory.get_provider("mock")
        return mock_provider.generate(request)

    def route_stream(self, request: LLMRequest) -> Iterator[LLMResponse]:
        required_len = len(request.prompt) // 4 + 100

        tried_providers = set()

        while len(tried_providers) < len(self.registry.list_providers()):
            p_name, model_name = self.selector.select_best_provider(request, required_len)

            if p_name in tried_providers:
                found_new = False
                for fallback_p in self.config.fallback_chain:
                    if fallback_p not in tried_providers:
                        p_name = fallback_p
                        p_info = self.registry.get_provider(p_name)
                        if p_info:
                            if p_info.is_local:
                                model_name = self.config.preferred_local_model
                            else:
                                model_name = self.config.preferred_remote_model
                            found_new = True
                            break
                if not found_new:
                    break

            tried_providers.add(p_name)

            mapped_name = p_name
            if p_name == "anthropic":
                mapped_name = "claude"
            try:
                provider = self.provider_factory.get_provider(mapped_name)
            except Exception:
                continue

            request.model_name = model_name

            start_time = time.time()
            try:
                chunks = []
                for chunk in provider.generate_stream(request):
                    chunks.append(chunk.content)
                    yield chunk

                latency = time.time() - start_time
                self.health_monitor.record_success(p_name, latency)

                p_info = self.registry.get_provider(p_name)
                cost = 0.0
                prompt_tokens = len(request.prompt) // 4
                comp_tokens = len("".join(chunks)) // 4
                if p_info:
                    cost = (prompt_tokens * p_info.cost_per_million_input / 1_000_000) + (
                        comp_tokens * p_info.cost_per_million_output / 1_000_000
                    )

                self.metrics.record_usage(p_name, model_name, prompt_tokens, comp_tokens, cost)
                return
            except Exception:
                self.health_monitor.record_failure(p_name)
                continue

        mock_provider = self.provider_factory.get_provider("mock")
        yield from mock_provider.generate_stream(request)

