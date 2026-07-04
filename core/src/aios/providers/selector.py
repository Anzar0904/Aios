import random
from typing import Tuple, List, Dict, Any, Optional

from aios.providers.config import ProviderConfig
from aios.providers.health import ProviderHealthMonitor
from aios.providers.registry import ProviderRegistry
from aios.services.model import LLMRequest


from aios.providers.models import DIInitializeMixin


class CapabilityRouter(DIInitializeMixin):
    """Filters candidate providers by requested metadata capabilities."""

    def filter_by_capabilities(self, providers: List[Any], request: LLMRequest) -> List[Any]:
        filtered = []
        prefs = request.preferences or {}
        for p in providers:
            caps = p.capabilities
            if prefs.get("tool_calling") and not (caps.function_calling or caps.tools):
                continue
            if prefs.get("vision") and not caps.vision:
                continue
            if prefs.get("reasoning") and not caps.reasoning:
                continue
            if prefs.get("structured_output") and not caps.structured_output:
                continue
            filtered.append(p)
        return filtered if filtered else providers


class PriorityRouter(DIInitializeMixin):
    """Sorts candidate providers by prioritized ordering."""

    def route(self, providers: List[Any]) -> List[Any]:
        return sorted(providers, key=lambda x: x.priority)


class LatencyRouter(DIInitializeMixin):
    """Sorts candidate providers by historical latency metrics."""

    def __init__(self, health_monitor: ProviderHealthMonitor) -> None:
        self.health_monitor = health_monitor

    def route(self, providers: List[Any]) -> List[Any]:
        return sorted(providers, key=lambda x: self.health_monitor.get_average_latency(x.name))


class CostRouter(DIInitializeMixin):
    """Sorts candidate providers by input token cost values."""

    def route(self, providers: List[Any]) -> List[Any]:
        return sorted(providers, key=lambda x: x.cost_per_million_input)


class WeightedRouter(DIInitializeMixin):
    """Selects candidate provider randomly based on success rate weights."""

    def __init__(self, health_monitor: ProviderHealthMonitor) -> None:
        self.health_monitor = health_monitor

    def select(self, providers: List[Any]) -> Optional[Any]:
        if not providers:
            return None
        weights = [self.health_monitor.get_success_rate(p.name) for p in providers]
        if sum(weights) == 0:
            return random.choice(providers)
        return random.choices(providers, weights=weights, k=1)[0]


class HybridRouter(DIInitializeMixin):
    """Computes a balanced utility score based on cost, latency, and priority."""

    def __init__(self, health_monitor: ProviderHealthMonitor) -> None:
        self.health_monitor = health_monitor

    def route(self, providers: List[Any]) -> List[Any]:
        scored = []
        for p in providers:
            lat = self.health_monitor.get_average_latency(p.name)
            cost = p.cost_per_million_input
            pri = p.priority

            lat_score = min(lat, 5.0) / 5.0
            cost_score = min(cost, 20.0) / 20.0
            pri_score = min(pri, 10.0) / 10.0

            score = (0.4 * lat_score) + (0.4 * cost_score) + (0.2 * pri_score)
            scored.append((score, p))
        scored.sort(key=lambda x: x[0])
        return [item[1] for item in scored]


class RoutingPolicyEngine(DIInitializeMixin):
    """Parses routing strategies and delegates to specialized sub-routers."""

    def __init__(
        self,
        health_monitor: ProviderHealthMonitor,
        capability_router: CapabilityRouter,
        priority_router: PriorityRouter,
        latency_router: LatencyRouter,
        cost_router: CostRouter,
        hybrid_router: HybridRouter,
        weighted_router: WeightedRouter
    ) -> None:
        self.health_monitor = health_monitor
        self.capability_router = capability_router
        self.priority_router = priority_router
        self.latency_router = latency_router
        self.cost_router = cost_router
        self.hybrid_router = hybrid_router
        self.weighted_router = weighted_router

    def get_routed_providers(self, providers: List[Any], request: LLMRequest, strategy: str = "hybrid") -> List[Any]:
        filtered = self.capability_router.filter_by_capabilities(providers, request)
        if strategy == "cost":
            return self.cost_router.route(filtered)
        elif strategy == "latency":
            return self.latency_router.route(filtered)
        elif strategy == "priority":
            return self.priority_router.route(filtered)
        elif strategy == "weighted":
            best = self.weighted_router.select(filtered)
            return [best] if best else filtered
        else:
            return self.hybrid_router.route(filtered)


class ProviderSelector(DIInitializeMixin):
    """Conductor choosing the optimal provider based on routing engines."""

    def __init__(
        self,
        config: ProviderConfig,
        registry: ProviderRegistry,
        health_monitor: ProviderHealthMonitor
    ) -> None:
        self.config = config
        self.registry = registry
        self.health_monitor = health_monitor

        self.capability_router = CapabilityRouter()
        self.priority_router = PriorityRouter()
        self.latency_router = LatencyRouter(health_monitor)
        self.cost_router = CostRouter()
        self.weighted_router = WeightedRouter(health_monitor)
        self.hybrid_router = HybridRouter(health_monitor)

        self.policy_engine = RoutingPolicyEngine(
            health_monitor,
            self.capability_router,
            self.priority_router,
            self.latency_router,
            self.cost_router,
            self.hybrid_router,
            self.weighted_router
        )

    def select_best_provider(
        self, request: LLMRequest, required_context_len: int = 4096
    ) -> Tuple[str, str]:
        offline = self.config.offline_mode

        # 1. Prioritize providers that officially support the requested model
        supported_candidates = []
        if request.model_name:
            for p in self.registry.list_providers():
                if request.model_name in p.supported_models:
                    if offline and not p.is_local:
                        continue
                    if not self.health_monitor.is_healthy(p.name):
                        continue
                    if required_context_len > p.context_window:
                        continue
                    supported_candidates.append(p)

        # 2. If we found matching providers, route among them
        if supported_candidates:
            prefs = request.preferences or {}
            strategy = prefs.get("routing_strategy", "hybrid")
            routed = self.policy_engine.get_routed_providers(supported_candidates, request, strategy)
            best_p = routed[0]
            return best_p.name, request.model_name

        # 3. Otherwise, fall back to preferred provider and fallback chain
        fallback_candidates = []
        candidates_order = []
        if self.config.preferred_provider:
            candidates_order.append(self.config.preferred_provider)
        candidates_order.extend(self.config.fallback_chain)
        candidates_order.append("mock")

        seen = set()
        for name in candidates_order:
            if name not in seen:
                seen.add(name)
                p = self.registry.get_provider(name)
                if p:
                    if offline and not p.is_local:
                        continue
                    if not self.health_monitor.is_healthy(p.name):
                        continue
                    if required_context_len > p.context_window:
                        continue
                    fallback_candidates.append(p)

        if not fallback_candidates:
            fallback_p = "ollama" if offline else "openai"
            meta = self.registry.get_provider(fallback_p)
            return fallback_p, (meta.supported_models[0] if meta and meta.supported_models else "mock-model")

        # 4. Check manual override preference
        prefs = request.preferences or {}
        manual_override = prefs.get("preferred_provider")
        if manual_override:
            meta = self.registry.get_provider(manual_override)
            if meta:
                return manual_override, (request.model_name or meta.supported_models[0])

        # 5. Route among fallback candidates
        strategy = prefs.get("routing_strategy", "hybrid")
        routed = self.policy_engine.get_routed_providers(fallback_candidates, request, strategy)
        best_p = routed[0]

        # Determine fallback model name
        selected_model = None
        if best_p.name == "omniroute":
            selected_model = request.model_name or "auto"
        elif request.model_name:
            if request.model_name in best_p.supported_models or "/" in request.model_name:
                selected_model = request.model_name
            elif best_p.name == "ollama" and request.model_name == "llama3":
                selected_model = "llama3"
            elif best_p.name == "openai" and request.model_name.startswith("gpt"):
                selected_model = request.model_name
            elif best_p.name == "claude_code" and request.model_name.startswith("claude"):
                selected_model = request.model_name
            elif best_p.name == "gemini_cli" and request.model_name.startswith("gemini"):
                selected_model = request.model_name

        if not selected_model:
            if best_p.is_local:
                selected_model = self.config.preferred_local_model
            else:
                selected_model = self.config.preferred_remote_model

        return best_p.name, selected_model
