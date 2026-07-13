"""
aios/providers/interface.py

Defines the universal AIProvider interface and the AIProviderRegistry.
"""

from __future__ import annotations

import abc
import time
from dataclasses import dataclass, field
from typing import Any, Dict, Iterator, List, Optional, Tuple

from aios.providers.models import ProviderCapabilities


class AIProvider(abc.ABC):
    """Universal abstract interface for all AI provider engines."""

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Returns the identifier name of the provider."""
        pass

    @abc.abstractmethod
    def generate(
        self,
        model: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs: Any,
    ) -> str:
        """Executes content generation for a prompt."""
        pass

    @abc.abstractmethod
    def stream(
        self,
        model: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs: Any,
    ) -> Iterator[str]:
        """Streams content generation for a prompt."""
        pass

    @abc.abstractmethod
    def embeddings(
        self,
        model: str,
        text: str,
        **kwargs: Any,
    ) -> List[float]:
        """Generates embedding vector for text."""
        pass

    @abc.abstractmethod
    def health(self) -> bool:
        """Checks the health and availability of the provider."""
        pass

    @abc.abstractmethod
    def capabilities(self) -> ProviderCapabilities:
        """Returns the capabilities of the provider."""
        pass


class AIProviderRegistry:
    """Universal registry to manage, register, and look up AIProvider instances."""

    def __init__(self) -> None:
        self._providers: Dict[str, AIProvider] = {}

    def register(self, provider: AIProvider) -> None:
        """Registers a concrete AIProvider instance."""
        self._providers[provider.name] = provider

    def lookup(self, name: str) -> Optional[AIProvider]:
        """Retrieves a registered AIProvider instance by name."""
        return self._providers.get(name)

    def list_providers(self) -> List[str]:
        """Lists the names of all registered providers."""
        return list(self._providers.keys())


# Global singleton instance for system-wide access
universal_provider_registry = AIProviderRegistry()


@dataclass
class ModelInfo:
    """Represents metadata and capabilities of a specific AI model."""

    provider: str
    model_id: str
    display_name: str
    family: str
    version: str = "1.0.0"
    max_context_tokens: int = 4096
    max_output_tokens: int = 1024
    supports_chat: bool = True
    supports_reasoning: bool = False
    supports_coding: bool = False
    supports_vision: bool = False
    supports_embeddings: bool = False
    supports_tool_calling: bool = False
    supports_streaming: bool = True
    supports_json: bool = False
    supports_functions: bool = False
    enabled: bool = True


class ModelRegistry:
    """Universal registry managing metadata for AI models and their provider mappings."""

    def __init__(self, provider_registry: Optional[AIProviderRegistry] = None) -> None:
        self._provider_registry = provider_registry or universal_provider_registry
        self._models: Dict[str, ModelInfo] = {}
        self._resolution_mappings: Dict[Tuple[str, str], str] = {}

    def register_model(self, model: ModelInfo) -> None:
        """Registers a ModelInfo metadata profile."""
        self._models[model.model_id] = model

    def get_model(self, model_id: str) -> Optional[ModelInfo]:
        """Looks up a ModelInfo metadata profile by its model_id."""
        return self._models.get(model_id)

    def list_models(self, provider_name: Optional[str] = None) -> List[ModelInfo]:
        """Lists all registered models, optionally filtering by provider."""
        if provider_name:
            return [m for m in self._models.values() if m.provider == provider_name]
        return list(self._models.values())

    def get_provider_for_model(self, model_id: str) -> Optional[str]:
        """Finds the provider name mapped to the specified model_id."""
        model = self.get_model(model_id)
        if model:
            return model.provider
        return None

    def register_model_resolution(self, provider: str, canonical_id: str, provider_id: str) -> None:
        """Allows dynamic registration of canonical-to-provider model mappings."""
        self._resolution_mappings[(provider, canonical_id)] = provider_id

    def resolve_provider_model(self, provider: str, model_id: str) -> str:
        """Resolves a canonical model ID to its provider-specific model ID."""
        return self._resolution_mappings.get((provider, model_id), model_id)


# Global singleton instance for system-wide access
universal_model_registry = ModelRegistry()


class CapabilityRegistry:
    """Universal registry describing the capabilities of AI providers and models."""

    def __init__(self, provider_registry: Optional[AIProviderRegistry] = None) -> None:
        self._provider_registry = provider_registry or universal_provider_registry
        self._provider_capabilities: Dict[str, ProviderCapabilities] = {}
        self._model_capabilities: Dict[str, ProviderCapabilities] = {}

    def register_provider_capabilities(
        self, provider_name: str, caps: ProviderCapabilities
    ) -> None:
        """Registers capabilities for a provider."""
        self._provider_capabilities[provider_name] = caps

    def register_model_capabilities(self, model_name: str, caps: ProviderCapabilities) -> None:
        """Registers capabilities for a specific model."""
        self._model_capabilities[model_name] = caps

    def get_capabilities(
        self, provider_name: str, model_name: Optional[str] = None
    ) -> Optional[ProviderCapabilities]:
        """Retrieves capabilities for a provider or model.

        Falls back to provider capabilities if model caps not found.
        """
        if model_name and model_name in self._model_capabilities:
            return self._model_capabilities[model_name]

        if provider_name in self._provider_capabilities:
            return self._provider_capabilities[provider_name]

        # Integrate with AIProvider.capabilities() if registered in the registry
        if self._provider_registry:
            provider = self._provider_registry.lookup(provider_name)
            if provider:
                return provider.capabilities()

        return None


# Global singleton instance for system-wide access
universal_capability_registry = CapabilityRegistry()


@dataclass
class ProviderHealth:
    """Represents health status metrics of an AI provider."""

    available: bool = True
    latency_ms: float = 0.0
    last_checked: float = field(default_factory=time.time)
    last_error: Optional[str] = None
    success_rate: float = 1.0
    failure_rate: float = 0.0
    health_score: float = 100.0
    timeout_history: List[float] = field(default_factory=list)
    last_successful_request: float = 0.0
    last_failure_request: float = 0.0


class ProviderHealthRegistry:
    """Registry managing dynamic health metrics for AI providers."""

    def __init__(self, provider_registry: Optional[AIProviderRegistry] = None) -> None:
        self._provider_registry = provider_registry or universal_provider_registry
        self._health_states: Dict[str, ProviderHealth] = {}

    def get_health(self, provider_name: str) -> ProviderHealth:
        """Retrieves current health details for a provider.

        Returns default health if none registered.
        """
        if provider_name not in self._health_states:
            # Check if provider exists in AIProviderRegistry
            exists = False
            if self._provider_registry:
                exists = self._provider_registry.lookup(provider_name) is not None
            self._health_states[provider_name] = ProviderHealth(available=exists)
        return self._health_states[provider_name]

    def update_health(self, provider_name: str, **kwargs: Any) -> None:
        """Updates health attributes dynamically for a provider."""
        current = self.get_health(provider_name)

        # Update attributes in place
        for key, val in kwargs.items():
            if hasattr(current, key):
                setattr(current, key, val)

        # Automatically update updated last_checked timestamp unless explicitly passed
        if "last_checked" not in kwargs:
            current.last_checked = time.time()

    def update_health_success(self, provider_name: str, latency_ms: float) -> None:
        """Updates registry on successful request to a provider."""
        health = self.get_health(provider_name)
        health.available = True
        health.latency_ms = latency_ms
        health.last_checked = time.time()
        health.last_successful_request = time.time()

        # update success/failure rate
        success = health.success_rate * 0.9 + 0.1
        health.success_rate = success
        health.failure_rate = 1.0 - success

        # calculate dynamic health score
        score = success * 100.0
        if latency_ms > 1000:
            score -= min(30.0, (latency_ms - 1000) / 100)
        health.health_score = max(0.0, min(100.0, score))

    def update_health_failure(self, provider_name: str, error_message: str) -> None:
        """Updates registry on failed request to a provider."""
        health = self.get_health(provider_name)
        if "timeout" in error_message.lower() or "deadline" in error_message.lower():
            health.timeout_history.append(time.time())
            if len(health.timeout_history) > 10:
                health.timeout_history.pop(0)

        health.last_checked = time.time()
        health.last_failure_request = time.time()
        health.last_error = error_message

        success = health.success_rate * 0.9
        health.success_rate = success
        health.failure_rate = 1.0 - success

        score = success * 100.0
        now = time.time()
        recent_timeouts = sum(1 for t in health.timeout_history if now - t < 300)
        score -= min(40.0, recent_timeouts * 10)

        if success < 0.2:
            health.available = False

        health.health_score = max(0.0, min(100.0, score))


# Global singleton instance for system-wide access
universal_health_registry = ProviderHealthRegistry()


@dataclass
class ProviderCost:
    """Represents the token pricing model for a provider or specific model."""

    input_cost_per_million_tokens: float = 0.0
    output_cost_per_million_tokens: float = 0.0
    currency: str = "USD"

    def estimated_request_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Estimates the cost of a single request based on token counts."""
        input_cost = (input_tokens * self.input_cost_per_million_tokens) / 1_000_000.0
        output_cost = (output_tokens * self.output_cost_per_million_tokens) / 1_000_000.0
        return input_cost + output_cost


@dataclass
class ProviderQuota:
    """Represents the quota limits and remaining budgets of a provider."""

    requests_remaining: int = 1000
    tokens_remaining: int = 1000000
    reset_time: float = 0.0
    unlimited: bool = False


class ProviderCostRegistry:
    """Registry managing pricing/costs of providers and models."""

    def __init__(self, provider_registry: Optional[AIProviderRegistry] = None) -> None:
        self._provider_registry = provider_registry or universal_provider_registry
        self._provider_costs: Dict[str, ProviderCost] = {}
        self._model_costs: Dict[str, ProviderCost] = {}

    def register_provider_cost(self, provider_name: str, cost: ProviderCost) -> None:
        """Registers cost profile for a provider."""
        self._provider_costs[provider_name] = cost

    def register_model_cost(self, model_name: str, cost: ProviderCost) -> None:
        """Registers cost profile for a specific model."""
        self._model_costs[model_name] = cost

    def get_cost(
        self, provider_name: str, model_name: Optional[str] = None
    ) -> Optional[ProviderCost]:
        """Retrieves cost profile for a model or provider.

        Falls back to provider cost.
        """
        if model_name and model_name in self._model_costs:
            return self._model_costs[model_name]

        if provider_name in self._provider_costs:
            return self._provider_costs[provider_name]

        # Integrate with AIProviderRegistry to fetch metadata costs
        if self._provider_registry:
            provider = self._provider_registry.lookup(provider_name)
            if provider:
                meta = getattr(provider, "metadata", provider)
                if hasattr(meta, "cost_per_million_input") and hasattr(
                    meta, "cost_per_million_output"
                ):
                    return ProviderCost(
                        input_cost_per_million_tokens=meta.cost_per_million_input,
                        output_cost_per_million_tokens=meta.cost_per_million_output,
                    )
        return None


class ProviderQuotaRegistry:
    """Registry managing quotas (requests/tokens remaining) for providers."""

    def __init__(self, provider_registry: Optional[AIProviderRegistry] = None) -> None:
        self._provider_registry = provider_registry or universal_provider_registry
        self._quotas: Dict[str, ProviderQuota] = {}

    def get_quota(self, provider_name: str) -> ProviderQuota:
        """Retrieves quota tracking details for a provider.

        Returns default unlimited quota if none registered.
        """
        if provider_name not in self._quotas:
            # Check if provider exists
            exists = False
            if self._provider_registry:
                exists = self._provider_registry.lookup(provider_name) is not None
            self._quotas[provider_name] = ProviderQuota(unlimited=not exists)
        return self._quotas[provider_name]

    def update_quota(self, provider_name: str, **kwargs: Any) -> None:
        """Updates quota parameters dynamically for a provider."""
        current = self.get_quota(provider_name)
        for key, val in kwargs.items():
            if hasattr(current, key):
                setattr(current, key, val)


# Global singleton instances for system-wide access
universal_cost_registry = ProviderCostRegistry()
universal_quota_registry = ProviderQuotaRegistry()


@dataclass
class RoutingRequest:
    """Represents a request to select the optimal AI provider/model endpoint."""

    task_type: str  # e.g., "chat", "coding", "reasoning", "embeddings", "vision"
    required_capabilities: List[str] = field(default_factory=list)
    estimated_input_tokens: int = 100
    estimated_output_tokens: int = 100
    preferred_provider: Optional[str] = None
    preferred_model: Optional[str] = None
    excluded_providers: List[str] = field(default_factory=list)
    routing_policy: Optional[str] = None


@dataclass
class RoutingDecision:
    """Represents the final provider/model routing choice determined by the RoutingEngine."""

    provider: str
    model: str
    routing_score: float
    reasoning: str


class RoutingEngine:
    """Routing engine that dynamically selects the best provider/model endpoint."""

    def __init__(
        self,
        provider_registry: Optional[AIProviderRegistry] = None,
        capability_registry: Optional[CapabilityRegistry] = None,
        health_registry: Optional[ProviderHealthRegistry] = None,
        cost_registry: Optional[ProviderCostRegistry] = None,
        quota_registry: Optional[ProviderQuotaRegistry] = None,
        model_registry: Optional[ModelRegistry] = None,
    ) -> None:
        self.provider_registry = provider_registry or universal_provider_registry
        self.capability_registry = capability_registry or universal_capability_registry
        self.health_registry = health_registry or universal_health_registry
        self.cost_registry = cost_registry or universal_cost_registry
        self.quota_registry = quota_registry or universal_quota_registry
        self.model_registry = model_registry or universal_model_registry

    def route(self, request: RoutingRequest) -> RoutingDecision:
        """Determines the best provider/model routing decision based on active registry metrics."""
        # 0. Check if 9Router is active and is the primary gateway
        use_ninerouter = True
        if request.preferred_provider and request.preferred_provider != "ninerouter":
            use_ninerouter = False

        ninerouter_provider = self.provider_registry.lookup("ninerouter")
        is_ninerouter_active = ninerouter_provider and ninerouter_provider.health()

        if use_ninerouter and is_ninerouter_active:
            preferred_model = request.preferred_model
            preferred_backend = None
            try:
                from pathlib import Path

                from aios.config import load_config

                config = load_config(Path("config/config.toml"))
                if config and hasattr(config, "llm") and getattr(config.llm, "ninerouter", None):
                    preferred_model = preferred_model or config.llm.ninerouter.preferred_model
                    preferred_backend = config.llm.ninerouter.preferred_backend
            except Exception:
                pass

            nr_models = self.model_registry.list_models("ninerouter")
            selected_model = preferred_model

            if not selected_model and nr_models:
                task = request.task_type
                if task == "coding":
                    matches = [m.model_id for m in nr_models if m.supports_coding]
                    if not matches:
                        matches = [
                            m.model_id
                            for m in nr_models
                            if "coder" in m.model_id.lower() or "qwen" in m.model_id.lower()
                        ]
                    if matches:
                        selected_model = matches[0]
                elif task == "reasoning":
                    matches = [m.model_id for m in nr_models if m.supports_reasoning]
                    if not matches:
                        matches = [
                            m.model_id
                            for m in nr_models
                            if "o1" in m.model_id.lower() or "r1" in m.model_id.lower()
                        ]
                    if matches:
                        selected_model = matches[0]
                elif task == "vision":
                    matches = [m.model_id for m in nr_models if m.supports_vision]
                    if not matches:
                        matches = [
                            m.model_id
                            for m in nr_models
                            if "vision" in m.model_id.lower() or "gpt-4o" in m.model_id.lower()
                        ]
                    if matches:
                        selected_model = matches[0]
                elif task == "embeddings":
                    matches = [m.model_id for m in nr_models if m.supports_embeddings]
                    if not matches:
                        matches = [m.model_id for m in nr_models if "embed" in m.model_id.lower()]
                    if matches:
                        selected_model = matches[0]

                if not selected_model:
                    matches = [m.model_id for m in nr_models if m.supports_chat]
                    if matches:
                        selected_model = matches[0]
                    else:
                        selected_model = nr_models[0].model_id if nr_models else "gpt-4o"

            if not selected_model:
                selected_model = "gpt-4o"

            reason = (
                f"Selected model '{selected_model}' "
                f"for task '{request.task_type}' and routed through 9Router gateway."
            )
            if preferred_backend:
                reason += f" Preferred backend: {preferred_backend}."

            return RoutingDecision(
                provider="ninerouter",
                model=selected_model,
                routing_score=100.0,
                reasoning=reason,
            )

        # 1. Check for manual provider override
        if request.preferred_provider:
            pref_provider = request.preferred_provider
            pref_model = request.preferred_model or "default"

            provider_inst = self.provider_registry.lookup(pref_provider)
            if provider_inst and pref_provider not in request.excluded_providers:
                return RoutingDecision(
                    provider=pref_provider,
                    model=pref_model,
                    routing_score=100.0,
                    reasoning=f"Manual override requested for provider '{pref_provider}' "
                    f"and model '{pref_model}'.",
                )

        # Determine policy weights
        policy = request.routing_policy or "default"
        if policy == "default":
            try:
                from pathlib import Path

                from aios.config import load_config

                config = load_config(Path("config/config.toml"))
                if (
                    config
                    and hasattr(config, "llm")
                    and getattr(config.llm, "routing_policy", None)
                ):
                    policy = config.llm.routing_policy
            except Exception:
                pass

        if policy == "cost-first":
            health_w, latency_w, cost_w = 0.1, 0.0, 0.9
        elif policy == "speed-first":
            health_w, latency_w, cost_w = 0.1, 0.9, 0.0
        elif policy == "quality-first":
            health_w, latency_w, cost_w = 0.8, 0.1, 0.1
        else:  # default or local-first
            health_w, latency_w, cost_w = 0.4, 0.3, 0.3

        # 2. Iterate through all registered providers and evaluate them
        candidates: List[Tuple[str, str, float, str]] = []
        registered_models = self.model_registry.list_models()

        if registered_models:
            for model_info in registered_models:
                if not model_info.enabled:
                    continue
                p_name = model_info.provider
                m_name = model_info.model_id

                if p_name in request.excluded_providers:
                    continue

                provider = self.provider_registry.lookup(p_name)
                if not provider:
                    continue

                # A. Capabilities Match
                caps = self.capability_registry.get_capabilities(p_name, m_name)

                if request.task_type == "coding" and not (
                    model_info.supports_coding
                    or (
                        caps
                        and (
                            getattr(caps, "coding", False)
                            or getattr(caps, "code_generation", False)
                        )
                    )
                ):
                    continue
                if request.task_type == "embeddings" and not (
                    model_info.supports_embeddings or (caps and getattr(caps, "embeddings", False))
                ):
                    continue
                if request.task_type == "vision" and not (
                    model_info.supports_vision or (caps and getattr(caps, "vision", False))
                ):
                    continue
                if request.task_type == "reasoning" and not (
                    model_info.supports_reasoning or (caps and getattr(caps, "reasoning", False))
                ):
                    continue

                if request.required_capabilities:
                    missing_caps = False
                    for cap_name in request.required_capabilities:
                        has_cap = getattr(model_info, f"supports_{cap_name}", False) or (
                            caps and getattr(caps, cap_name, False)
                        )
                        if not has_cap:
                            missing_caps = True
                            break
                    if missing_caps:
                        continue

                # B. Health Check
                health = self.health_registry.get_health(p_name)
                if not health.available:
                    continue
                if health.health_score < 20.0:
                    continue

                # C. Quota Verification
                quota = self.quota_registry.get_quota(p_name)
                if not quota.unlimited:
                    total_tokens = request.estimated_input_tokens + request.estimated_output_tokens
                    if quota.requests_remaining <= 0 or quota.tokens_remaining < total_tokens:
                        continue

                # D. Cost Estimation
                cost_profile = self.cost_registry.get_cost(p_name, m_name)
                est_cost = 0.0
                if cost_profile:
                    est_cost = cost_profile.estimated_request_cost(
                        request.estimated_input_tokens, request.estimated_output_tokens
                    )

                # E. Weighted Scoring
                health_contrib = health.health_score * health_w
                if health.latency_ms > 0:
                    latency_score = max(0.0, 100.0 - (health.latency_ms / 50.0))
                else:
                    latency_score = 80.0
                latency_contrib = latency_score * latency_w
                cost_score = max(0.0, 100.0 - (est_cost * 100.0))
                cost_contrib = cost_score * cost_w

                final_score = health_contrib + latency_contrib + cost_contrib

                is_local = False
                if hasattr(model_info, "is_local"):
                    is_local = getattr(model_info, "is_local", False)
                if not is_local:
                    meta = getattr(provider, "metadata", provider)
                    is_local = getattr(meta, "is_local", False) or p_name in (
                        "ollama",
                        "lmstudio",
                        "mock",
                    )

                if policy == "local-first" and is_local:
                    final_score += 100.0

                if policy == "quality-first":
                    if model_info.supports_reasoning:
                        final_score += 30.0
                    if model_info.supports_coding:
                        final_score += 20.0

                reason = (
                    f"Routed under policy '{policy}'. "
                    f"Health score: {health.health_score:.1f} "
                    f"({health_w * 100.0:.0f}% weight), "
                    f"latency: {health.latency_ms:.1f}ms ({latency_w * 100.0:.0f}% weight), "
                    f"estimated cost: {est_cost:.4f} USD ({cost_w * 100.0:.0f}% weight)."
                )

                candidates.append((p_name, m_name, final_score, reason))
        else:
            registered_providers = self.provider_registry.list_providers()

            for p_name in registered_providers:
                if p_name in request.excluded_providers:
                    continue
                provider = self.provider_registry.lookup(p_name)
                if not provider:
                    continue

                meta = getattr(provider, "metadata", provider)
                models_to_test = getattr(meta, "supported_models", ["default"])
                if not models_to_test:
                    models_to_test = ["default"]

                for m_name in models_to_test:
                    caps = self.capability_registry.get_capabilities(p_name, m_name)
                    if caps:
                        if request.task_type == "coding" and not (
                            getattr(caps, "coding", False)
                            or getattr(caps, "code_generation", False)
                        ):
                            continue
                        if request.task_type == "embeddings" and not getattr(
                            caps, "embeddings", False
                        ):
                            continue
                        if request.task_type == "vision" and not getattr(caps, "vision", False):
                            continue
                        if request.task_type == "reasoning" and not getattr(
                            caps, "reasoning", False
                        ):
                            continue

                        missing_caps = False
                        for cap_name in request.required_capabilities:
                            if not getattr(caps, cap_name, False):
                                missing_caps = True
                                break
                        if missing_caps:
                            continue
                    else:
                        if request.task_type in ["embeddings", "vision"]:
                            continue

                    health = self.health_registry.get_health(p_name)
                    if not health.available:
                        continue
                    if health.health_score < 20.0:
                        continue

                    quota = self.quota_registry.get_quota(p_name)
                    if not quota.unlimited:
                        total_tokens = (
                            request.estimated_input_tokens + request.estimated_output_tokens
                        )
                        if quota.requests_remaining <= 0 or quota.tokens_remaining < total_tokens:
                            continue

                    cost_profile = self.cost_registry.get_cost(p_name, m_name)
                    est_cost = 0.0
                    if cost_profile:
                        est_cost = cost_profile.estimated_request_cost(
                            request.estimated_input_tokens, request.estimated_output_tokens
                        )

                    health_contrib = health.health_score * health_w
                    if health.latency_ms > 0:
                        latency_score = max(0.0, 100.0 - (health.latency_ms / 50.0))
                    else:
                        latency_score = 80.0
                    latency_contrib = latency_score * latency_w
                    cost_score = max(0.0, 100.0 - (est_cost * 100.0))
                    cost_contrib = cost_score * cost_w

                    final_score = health_contrib + latency_contrib + cost_contrib

                    is_local = p_name in ("ollama", "lmstudio", "mock")
                    if policy == "local-first" and is_local:
                        final_score += 100.0

                    reason = (
                        f"Routed under policy '{policy}'. "
                        f"Health score: {health.health_score:.1f} "
                        f"({health_w * 100.0:.0f}% weight), "
                        f"latency: {health.latency_ms:.1f}ms "
                        f"({latency_w * 100.0:.0f}% weight), "
                        f"estimated cost: {est_cost:.4f} USD "
                        f"({cost_w * 100.0:.0f}% weight)."
                    )

                    candidates.append((p_name, m_name, final_score, reason))

        if request.preferred_model and candidates:
            model_matched = [c for c in candidates if c[1] == request.preferred_model]
            if model_matched:
                candidates = model_matched

        if not candidates:
            registered_providers = self.provider_registry.list_providers()
            valid_providers = [
                p for p in registered_providers if p not in request.excluded_providers
            ]
            if valid_providers:
                fb_p = valid_providers[0]
                provider = self.provider_registry.lookup(fb_p)
                meta = getattr(provider, "metadata", provider)
                fb_m = (
                    meta.supported_models[0]
                    if getattr(meta, "supported_models", None)
                    else "default"
                )
                return RoutingDecision(
                    provider=fb_p,
                    model=fb_m,
                    routing_score=10.0,
                    reasoning=f"No matching candidates passed filters. "
                    f"Falling back to default provider '{fb_p}'.",
                )

            return RoutingDecision(
                provider="mock",
                model="mock-model",
                routing_score=0.0,
                reasoning="No active providers registered. Falling back to mock provider.",
            )

        candidates.sort(key=lambda x: x[2], reverse=True)
        best = candidates[0]
        return RoutingDecision(
            provider=best[0],
            model=best[1],
            routing_score=best[2],
            reasoning=best[3],
        )


# Global singleton instance for system-wide access
universal_routing_engine = RoutingEngine()


@dataclass
class OmniRouteRequest:
    """Represents a unified prompt execution request to the OmniRoute Engine."""

    prompt: str
    system_prompt: Optional[str] = None
    task_type: str = "chat"
    required_capabilities: List[str] = field(default_factory=list)
    estimated_input_tokens: int = 100
    estimated_output_tokens: int = 100
    preferred_provider: Optional[str] = None
    preferred_model: Optional[str] = None
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    additional_params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OmniRouteResponse:
    """Represents a unified, provider-independent response from the OmniRoute Engine."""

    content: str
    provider: str
    model: str
    routing_decision: RoutingDecision
    usage: Dict[str, int] = field(default_factory=dict)
    cost: float = 0.0
    latency_ms: float = 0.0


class OmniRouteEngine:
    """Core execution engine coordinating routing, quota, and provider execution."""

    def __init__(
        self,
        provider_registry: Optional[AIProviderRegistry] = None,
        capability_registry: Optional[CapabilityRegistry] = None,
        health_registry: Optional[ProviderHealthRegistry] = None,
        cost_registry: Optional[ProviderCostRegistry] = None,
        quota_registry: Optional[ProviderQuotaRegistry] = None,
        routing_engine: Optional[RoutingEngine] = None,
        model_registry: Optional[ModelRegistry] = None,
    ) -> None:
        self.provider_registry = provider_registry or universal_provider_registry
        self.capability_registry = capability_registry or universal_capability_registry
        self.health_registry = health_registry or universal_health_registry
        self.cost_registry = cost_registry or universal_cost_registry
        self.quota_registry = quota_registry or universal_quota_registry
        self.routing_engine = routing_engine or universal_routing_engine
        self.model_registry = model_registry or universal_model_registry

    def execute(self, request: OmniRouteRequest) -> OmniRouteResponse:
        """Routes, executes, and updates telemetry/metadata for the request."""
        import logging

        logger = logging.getLogger(__name__)

        excluded_providers = []
        max_fallbacks = 3
        fallback_count = 0

        default_retries = 2
        try:
            from pathlib import Path

            from aios.config import load_config

            config = load_config(Path("config/config.toml"))
            if (
                config
                and hasattr(config, "llm")
                and getattr(config.llm, "omniroute_retry_count", None) is not None
            ):
                default_retries = config.llm.omniroute_retry_count
        except Exception:
            pass

        max_retries = request.additional_params.get("max_retries", default_retries)
        last_error = None
        routing_decision = None

        while fallback_count <= max_fallbacks:
            preferred_provider = request.preferred_provider
            if not preferred_provider and request.preferred_model:
                preferred_provider = self.model_registry.get_provider_for_model(
                    request.preferred_model
                )

            routing_req = RoutingRequest(
                task_type=request.task_type,
                required_capabilities=request.required_capabilities,
                estimated_input_tokens=request.estimated_input_tokens,
                estimated_output_tokens=request.estimated_output_tokens,
                preferred_provider=preferred_provider,
                preferred_model=request.preferred_model,
                excluded_providers=excluded_providers.copy(),
                routing_policy=request.additional_params.get("routing_policy"),
            )

            decision = self.routing_engine.route(routing_req)
            routing_decision = decision
            if not decision or (decision.provider == "mock" and excluded_providers):
                break

            provider_instance = self.provider_registry.lookup(decision.provider)
            if not provider_instance:
                excluded_providers.append(decision.provider)
                continue

            success = False
            content = ""
            latency_ms = 0.0

            for retry in range(max_retries + 1):
                start_time = time.time()
                try:
                    invoke_params = request.additional_params.copy()
                    if request.temperature is not None:
                        invoke_params["temperature"] = request.temperature
                    if request.max_tokens is not None:
                        invoke_params["max_tokens"] = request.max_tokens

                    resolved_model = self.model_registry.resolve_provider_model(
                        decision.provider, decision.model
                    )

                    content = provider_instance.generate(
                        model=resolved_model,
                        prompt=request.prompt,
                        system_prompt=request.system_prompt,
                        **invoke_params,
                    )
                    latency_ms = (time.time() - start_time) * 1000.0
                    success = True
                    break
                except Exception as e:
                    latency_ms = (time.time() - start_time) * 1000.0
                    last_error = str(e)

                    self.health_registry.update_health_failure(decision.provider, last_error)

                    logger.warning(
                        f"Provider '{decision.provider}' failed on attempt {retry + 1} "
                        f"with error: {last_error}. Retrying..."
                    )
                    time.sleep(0.1 * (retry + 1))

            if success:
                self.health_registry.update_health_success(decision.provider, latency_ms)

                cost_profile = self.cost_registry.get_cost(decision.provider, decision.model)
                input_tokens = request.estimated_input_tokens
                output_tokens = max(1, len(content) // 4)
                est_cost = 0.0
                if cost_profile:
                    est_cost = cost_profile.estimated_request_cost(input_tokens, output_tokens)

                quota = self.quota_registry.get_quota(decision.provider)
                if not quota.unlimited:
                    new_reqs = max(0, quota.requests_remaining - 1)
                    new_tokens = max(0, quota.tokens_remaining - (input_tokens + output_tokens))
                    self.quota_registry.update_quota(
                        decision.provider,
                        requests_remaining=new_reqs,
                        tokens_remaining=new_tokens,
                    )

                try:
                    from aios.providers.benchmark import record_metric

                    record_metric(
                        decision.provider,
                        decision.model,
                        input_tokens,
                        output_tokens,
                        est_cost,
                        latency_ms,
                        True,
                    )
                except Exception:
                    pass

                return OmniRouteResponse(
                    content=content,
                    provider=decision.provider,
                    model=decision.model,
                    routing_decision=decision,
                    usage={"input_tokens": input_tokens, "output_tokens": output_tokens},
                    cost=est_cost,
                    latency_ms=latency_ms,
                )
            else:
                logger.error(
                    f"Provider '{decision.provider}' failed after {max_retries} retries. "
                    f"Initiating fallback..."
                )
                excluded_providers.append(decision.provider)
                fallback_count += 1

                try:
                    from aios.providers.benchmark import record_metric

                    record_metric(decision.provider, decision.model, 0, 0, 0.0, latency_ms, False)
                except Exception:
                    pass

        if not routing_decision:
            routing_decision = RoutingDecision(
                provider="unknown",
                model="unknown",
                routing_score=0.0,
                reasoning="All fallback options failed.",
            )
        raise RuntimeError(
            f"OmniRoute execution failed. All fallback providers exhausted. "
            f"Last error: {last_error}"
        )


# Global singleton instance for system-wide access
universal_omniroute_engine = OmniRouteEngine()
