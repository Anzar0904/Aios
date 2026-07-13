import logging
from pathlib import Path
from typing import Any, Iterator, Optional

from aios.config import load_config
from aios.providers.adapters import ClaudeProvider, MockProvider, OpenAIProvider
from aios.providers.interface import (
    ModelInfo,
    OmniRouteRequest,
    universal_model_registry,
    universal_omniroute_engine,
    universal_provider_registry,
)
from aios.services.model import LLMRequest, LLMResponse, ModelService

logger = logging.getLogger(__name__)


def _resolve_provider_for_model(configured_provider: Optional[str]) -> Optional[str]:
    """Return the name of the best registered provider to serve an unrecognised model.

    Resolution order (first match wins):
      1. The provider named in ``config.llm.provider``, if it is already registered.
         This lets config.toml express an explicit preference without hardcoding anything
         in application code.
      2. The first registered provider that has at least one model with
         ``supports_coding=True``.  Capable inference providers (e.g. NVIDIA) are
         naturally preferred over stub/mock providers this way.
      3. The first registered non-mock provider.
      4. Whatever was registered first (last-resort fallback so routing stays alive).

    No provider names are hardcoded here; the ladder is driven entirely by the
    current state of the registries at call time.
    """
    registered = universal_provider_registry.list_providers()
    if not registered:
        return None

    # 1. Honour the explicit config preference
    if configured_provider and universal_provider_registry.lookup(configured_provider):
        return configured_provider

    # 2. First provider whose registered models advertise coding capability
    for p_name in registered:
        if any(m.supports_coding for m in universal_model_registry.list_models(p_name)):
            return p_name

    # 3. First non-mock provider
    for p_name in registered:
        if p_name != "mock":
            return p_name

    # 4. Last resort
    return registered[0]


class LocalModelService(ModelService):
    def __init__(
        self,
        default_model: str = None,
        config_path: str = "config/config.toml",
        registry: Optional[Any] = None,
    ) -> None:
        self._default_model = default_model or "mock-model"
        self._config_path = config_path

    def initialize(self) -> None:
        logger.info("Initializing LocalModelService")

        # Load config once; reuse the object for all decisions in this method.
        config = None
        try:
            config = load_config(Path(self._config_path))
            if not self._default_model or self._default_model == "mock-model":
                self._default_model = config.llm.default_model or "mock-model"
        except Exception:
            pass

        # ── Register built-in providers ──────────────────────────────────────
        # Each guard prevents double-registration when bootstrap_services has
        # already called register_nvidia_provider() ahead of initialize().
        if not universal_provider_registry.lookup("mock"):
            universal_provider_registry.register(MockProvider())
            universal_model_registry.register_model(
                ModelInfo(
                    provider="mock",
                    model_id="mock-model",
                    display_name="Mock",
                    family="Mock",
                )
            )
        if not universal_provider_registry.lookup("openai"):
            universal_provider_registry.register(OpenAIProvider())
            universal_model_registry.register_model(
                ModelInfo(
                    provider="openai",
                    model_id="gpt-4o",
                    display_name="GPT-4o",
                    family="GPT",
                )
            )
        if not universal_provider_registry.lookup("claude"):
            universal_provider_registry.register(ClaudeProvider())
            universal_model_registry.register_model(
                ModelInfo(
                    provider="claude",
                    model_id="claude-3-5-sonnet",
                    display_name="Claude 3.5",
                    family="Claude",
                )
            )
        if not universal_provider_registry.lookup("nvidia"):
            from aios.providers.nvidia import register_nvidia_provider

            register_nvidia_provider()

        if not universal_provider_registry.lookup("ollama"):
            from aios.providers.adapters import OllamaProvider

            universal_provider_registry.register(OllamaProvider())
            universal_model_registry.register_model(
                ModelInfo(
                    provider="ollama",
                    model_id="llama3",
                    display_name="Llama 3",
                    family="Llama",
                )
            )

        if not universal_provider_registry.lookup("ninerouter"):
            from aios.providers.ninerouter import NineRouterProvider, discover_9router

            base_url = "http://localhost:8080/v1"
            api_key = None
            timeout = 30
            if config and hasattr(config, "llm") and getattr(config.llm, "ninerouter", None):
                nr_cfg = config.llm.ninerouter
                base_url = getattr(nr_cfg, "base_url", "http://localhost:8080/v1")
                api_key = getattr(nr_cfg, "api_key", None)
                timeout = getattr(nr_cfg, "timeout", 30)

            nr_provider = NineRouterProvider(base_url=base_url, api_key=api_key, timeout=timeout)
            universal_provider_registry.register(nr_provider)
            try:
                discover_9router(nr_provider)
            except Exception as e:
                logger.warning(f"Initial 9Router discovery failed: {e}")

        # ── Register the configured default model ────────────────────────────
        # If config.toml names a model (e.g. "qwen/qwen3-coder") that is not yet
        # in the universal_model_registry we register it now under the best
        # available provider, determined dynamically by _resolve_provider_for_model.
        #
        # This preserves provider-agnostic architecture:
        #   • No provider name is hardcoded at the call site.
        #   • config.llm.provider is the first preference; the resolution ladder
        #     handles gaps when that provider is not yet registered.
        #   • When OpenRouter / OmniRoute is added later, setting
        #     config.llm.provider = "openrouter" will automatically route here.
        if config is not None:
            default_model_id = config.llm.default_model
            if default_model_id and not universal_model_registry.get_model(default_model_id):
                resolved = _resolve_provider_for_model(config.llm.provider)
                if resolved:
                    family = (
                        default_model_id.split("/")[0]
                        if "/" in default_model_id
                        else default_model_id
                    )
                    universal_model_registry.register_model(
                        ModelInfo(
                            provider=resolved,
                            model_id=default_model_id,
                            display_name=default_model_id,
                            family=family,
                            supports_chat=True,
                            supports_coding=True,
                            supports_reasoning=True,
                        )
                    )
                    logger.info(
                        "Registered default model '%s' under provider '%s'",
                        default_model_id,
                        resolved,
                    )

    def start(self) -> None:
        pass

    def ready(self) -> bool:
        return True

    def shutdown(self) -> None:
        pass

    def execute_prompt(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        req = LLMRequest(
            prompt=prompt,
            system_instruction=system_instruction,
            model_name=self._default_model,
        )
        res = self.execute_request(req)
        return res.content

    def execute_request(self, request: LLMRequest) -> LLMResponse:
        if not request.model_name:
            request.model_name = self._default_model

        omni_req = OmniRouteRequest(
            prompt=request.prompt,
            system_prompt=request.system_instruction,
            task_type=request.task_category or "chat",
            preferred_model=request.model_name,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            additional_params=request.preferences,
        )

        omni_res = universal_omniroute_engine.execute(omni_req)

        return LLMResponse(
            content=omni_res.content,
            model_name=omni_res.model,
            provider_name=omni_res.provider,
            usage=omni_res.usage,
            finish_reason="stop",
            metadata={"latency_ms": omni_res.latency_ms, "cost": omni_res.cost},
        )

    def execute_stream(self, request: LLMRequest) -> Iterator[LLMResponse]:
        yield self.execute_request(request)
