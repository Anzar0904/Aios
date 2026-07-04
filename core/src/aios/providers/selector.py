from typing import Tuple

from aios.providers.config import ProviderConfig
from aios.providers.health import ProviderHealthMonitor
from aios.providers.registry import ProviderRegistry
from aios.services.model import LLMRequest


class ProviderSelector:
    def __init__(
        self,
        config: ProviderConfig,
        registry: ProviderRegistry,
        health_monitor: ProviderHealthMonitor,
    ) -> None:
        self.config = config
        self.registry = registry
        self.health_monitor = health_monitor

    def select_best_provider(
        self, request: LLMRequest, required_context_len: int = 4096
    ) -> Tuple[str, str]:
        offline = self.config.offline_mode

        # Prioritize providers that officially support the requested model
        preferred_providers = []
        if request.model_name:
            for p in self.registry.list_providers():
                if request.model_name in p.supported_models:
                    preferred_providers.append(p.name)

        candidates = []
        if self.config.preferred_provider == "omniroute":
            candidates.append("omniroute")
        candidates.extend(preferred_providers)
        if self.config.preferred_provider and self.config.preferred_provider != "omniroute":
            candidates.append(self.config.preferred_provider)
        candidates.extend(self.config.fallback_chain)
        # Always allow mock as final fallback
        candidates.append("mock")

        seen = set()
        ordered_candidates = []
        for c in candidates:
            if c not in seen:
                seen.add(c)
                ordered_candidates.append(c)

        for p_name in ordered_candidates:
            p_info = self.registry.get_provider(p_name)
            if not p_info:
                continue

            if offline and not p_info.is_local:
                continue

            if not self.health_monitor.is_healthy(p_name):
                continue

            if required_context_len > p_info.context_window:
                continue

            selected_model = None
            if p_name == "omniroute":
                selected_model = request.model_name or "auto"
            elif request.model_name:
                if request.model_name in p_info.supported_models or "/" in request.model_name:
                    selected_model = request.model_name
                elif p_name == "ollama" and request.model_name == "llama3":
                    selected_model = "llama3"
                elif p_name == "openai" and request.model_name.startswith("gpt"):
                    selected_model = request.model_name
                elif p_name == "anthropic" and request.model_name.startswith("claude"):
                    selected_model = request.model_name
                elif p_name == "gemini" and request.model_name.startswith("gemini"):
                    selected_model = request.model_name

            if not selected_model:
                if p_info.is_local:
                    selected_model = self.config.preferred_local_model
                else:
                    selected_model = self.config.preferred_remote_model

            if selected_model:
                return p_name, selected_model


        if offline:
            return "ollama", self.config.preferred_local_model
        return "openrouter", "qwen/qwen3-coder"
