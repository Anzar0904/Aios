import os
import time
import pytest
import subprocess
from unittest.mock import MagicMock, patch

from aios.services.model import LLMRequest, LLMResponse
from aios.services.model_impl import (
    LLMProviderError,
    OpenAIProvider,
    ClaudeProvider,
    GeminiProvider,
)
from aios.providers import (
    ProviderRegistry,
    ProviderConfigurationService,
    ProviderDiscoveryService,
    ProviderHealthMonitor,
    ProviderQuotaManager,
    ProviderRateLimitManager,
    ProviderTokenUsageTracker,
    ProviderLatencyAnalyzer,
    ProviderCostAnalyzer,
    ProviderSuccessAnalyzer,
    ProviderFailureAnalyzer,
    RoutingPolicyEngine,
    CapabilityRouter,
    PriorityRouter,
    LatencyRouter,
    CostRouter,
    WeightedRouter,
    HybridRouter,
    ProviderSelector,
    RetryManager,
    TimeoutManager,
    CircuitBreaker,
    AutomaticFailoverEngine,
    CheckpointManager,
    ResumeManager,
    ProviderValidator,
    ProviderReportGenerator,
    ProviderRouter,
    ProviderConfig,
    ProviderMetricsCollector,
    ProviderMetadata,
    ProviderCapabilities,
    ProviderStatus,
)


@pytest.fixture
def clean_registry():
    return ProviderRegistry()


@pytest.fixture
def health_monitor(clean_registry):
    return ProviderHealthMonitor(registry=clean_registry)


def test_provider_registration(clean_registry):
    providers = clean_registry.list_providers()
    assert len(providers) >= 4
    
    openai_p = clean_registry.get_provider("openai")
    assert openai_p is not None
    assert openai_p.name == "openai"
    assert openai_p.capabilities.streaming is True


def test_capability_routing(clean_registry):
    cap_router = CapabilityRouter()
    providers = clean_registry.list_providers()

    req_vision = LLMRequest(prompt="test", preferences={"vision": True})
    filtered = cap_router.filter_by_capabilities(providers, req_vision)
    for p in filtered:
        assert p.capabilities.vision is True


def test_priority_and_cost_routing(clean_registry):
    p_router = PriorityRouter()
    c_router = CostRouter()
    providers = clean_registry.list_providers()

    p_sorted = p_router.route(providers)
    assert p_sorted[0].priority <= p_sorted[-1].priority

    c_sorted = c_router.route(providers)
    assert c_sorted[0].cost_per_million_input <= c_sorted[-1].cost_per_million_input


def test_health_monitor_recording(health_monitor):
    health_monitor.record_success("openai", 1.2)
    health_monitor.record_success("openai", 0.8)
    assert health_monitor.get_average_latency("openai") == 1.0
    assert health_monitor.get_success_rate("openai") == 1.0

    health_monitor.record_failure("openai", "Connection timeout")
    assert health_monitor.get_success_rate("openai") == 2.0 / 3.0
    assert health_monitor.is_healthy("openai") is True


def test_circuit_breaker():
    breaker = CircuitBreaker(failure_threshold=2, recovery_time=2.0)
    assert breaker.is_open("openai") is False

    breaker.record_failure("openai")
    breaker.record_failure("openai")
    assert breaker.is_open("openai") is True

    time.sleep(2.1)
    assert breaker.is_open("openai") is False


def test_rate_limit_and_quota_managers(health_monitor):
    rl = health_monitor.rate_limit_manager
    qm = health_monitor.quota_manager

    assert rl.is_rate_limited("openai") is False
    rl.trigger_rate_limit("openai", retry_after=1.0)
    assert rl.is_rate_limited("openai") is True

    assert qm.is_quota_exhausted("openai") is False
    qm.record_cost("openai", 12.0)
    assert qm.is_quota_exhausted("openai") is True


def test_checkpoint_and_resume_managers():
    cm = CheckpointManager()
    rm = ResumeManager(cm)

    chk_id = cm.save_checkpoint("task_1", "openai", "Prompt text context", 1)
    data = rm.resume(chk_id)
    assert data["task_id"] == "task_1"
    assert data["provider_name"] == "openai"
    assert data["context"] == "Prompt text context"


def test_provider_validator():
    val = ProviderValidator()
    
    req_valid = LLMRequest(prompt="hello")
    assert len(val.validate_request(req_valid)) == 0

    req_invalid = LLMRequest(prompt="")
    assert len(val.validate_request(req_invalid)) > 0


def test_openai_adapter_execution():
    adapter = OpenAIProvider(api_key="sk-test-key")
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "choices": [{"message": {"content": "OpenAI generated text"}, "finish_reason": "stop"}],
        "usage": {"prompt_tokens": 10, "completion_tokens": 15, "total_tokens": 25},
        "model": "gpt-4o"
    }

    with patch("httpx.Client.post", return_value=mock_resp):
        req = LLMRequest(prompt="Hello OpenAI")
        res = adapter.generate(req)
        assert res.content == "OpenAI generated text"
        assert res.usage["prompt_tokens"] == 10


def test_claude_adapter_execution():
    adapter = ClaudeProvider(api_key="sk-ant-key")
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "content": [{"text": "Claude generated response"}],
        "usage": {"input_tokens": 8, "output_tokens": 12},
        "model": "claude-3-5-sonnet"
    }

    with patch("httpx.Client.post", return_value=mock_resp):
        req = LLMRequest(prompt="Hello Claude")
        res = adapter.generate(req)
        assert res.content == "Claude generated response"


def test_gemini_cli_adapter_execution():
    adapter = GeminiProvider(api_key="cli_active")
    mock_completed = MagicMock()
    mock_completed.returncode = 0
    mock_completed.stdout = "Gemini CLI stdout response"
    mock_completed.stderr = ""

    with patch("subprocess.run", return_value=mock_completed):
        req = LLMRequest(prompt="Hello Gemini CLI")
        res = adapter.generate(req)
        assert res.content == "Gemini CLI stdout response"
