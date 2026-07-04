from unittest.mock import MagicMock

from aios.providers import (
    ProviderConfig,
    ProviderHealthMonitor,
    ProviderMetricsCollector,
    ProviderRegistry,
    ProviderRouter,
)
from aios.services.model import LLMRequest, LLMResponse, ProviderFactory


def test_provider_selector_constraints():
    config = ProviderConfig(offline_mode=True)
    registry = ProviderRegistry()
    health = ProviderHealthMonitor()

    router = ProviderRouter(config, registry, health, ProviderMetricsCollector(), None)

    p_name, model_name = router.selector.select_best_provider(
        LLMRequest(prompt="test", model_name="gpt-4o")
    )
    assert p_name in ("ollama", "lmstudio")


def test_provider_health_and_metrics():
    health = ProviderHealthMonitor()
    assert health.is_healthy("openai") is True

    health.record_failure("openai")
    health.record_failure("openai")
    assert health.is_healthy("openai") is False

    metrics = ProviderMetricsCollector()
    metrics.record_usage("openai", "gpt-4o", 100, 200, 0.005)
    summary = metrics.get_summary()
    assert summary["total_tokens"] == 300
    assert summary["total_cost_usd"] == 0.005


def test_provider_fallback_execution():
    config = ProviderConfig(fallback_chain=["openai", "ollama"])
    registry = ProviderRegistry()
    health = ProviderHealthMonitor()
    metrics = ProviderMetricsCollector()

    factory = ProviderFactory()

    failing_openai = MagicMock()
    failing_openai.name = "openai"
    failing_openai.generate.side_effect = Exception("OpenAI down")

    succeeding_ollama = MagicMock()
    succeeding_ollama.name = "ollama"
    succeeding_ollama.generate.return_value = LLMResponse(
        content="local response",
        model_name="llama3",
        provider_name="ollama",
        usage={"prompt_tokens": 10, "completion_tokens": 20},
    )

    factory.register_provider(failing_openai)
    factory.register_provider(succeeding_ollama)

    router = ProviderRouter(config, registry, health, metrics, factory)

    response = router.route_request(LLMRequest(prompt="hello", model_name="gpt-4o"))
    assert response.provider_name == "ollama"
    assert response.content == "local response"
    assert health.get_success_rate("openai") == 0.0
    assert health.get_success_rate("ollama") == 1.0
