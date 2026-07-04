import json
from unittest.mock import MagicMock, patch
from contextlib import contextmanager

import httpx
import pytest

from aios.services.model import LLMRequest
from aios.services.model_impl import (
    LLMProviderError,
    OmniRouteProvider,
)


@contextmanager
def mock_stream_context(response):
    yield response


def test_omniroute_metadata_mapping():
    provider_free = OmniRouteProvider(routing_policy="FREE_ONLY")

    # Coding tasks map to auto/coding:free
    assert provider_free._map_model_name("claude-3-5-sonnet") == "auto/coding:free"
    assert provider_free._map_model_name("coding-model") == "auto/coding:free"
    assert provider_free._map_model_name("developer_agent") == "auto/coding:free"

    # Reasoning / Research tasks map to auto/reasoning:free
    assert provider_free._map_model_name("gpt-4o") == "auto/reasoning:free"
    assert provider_free._map_model_name("gemini-1.5-pro") == "auto/reasoning:free"
    assert provider_free._map_model_name("research") == "auto/reasoning:free"

    # Conversation tasks map to auto/chat:free
    assert provider_free._map_model_name("llama3") == "auto/chat:free"
    assert provider_free._map_model_name("chat-model") == "auto/chat:free"
    assert provider_free._map_model_name("conversation") == "auto/chat:free"

    # Already prefixed with auto
    assert provider_free._map_model_name("auto/coding") == "auto/coding:free"
    assert provider_free._map_model_name("auto/coding:fast") == "auto/coding:free"
    assert provider_free._map_model_name("auto") == "auto/chat:free"

    # Future routing mode
    provider_hybrid = OmniRouteProvider(routing_policy="HYBRID")
    assert provider_hybrid._map_model_name("claude-3-5-sonnet") == "auto/coding"


def test_omniroute_authentication_headers():
    # With API key
    provider_auth = OmniRouteProvider(api_key="omni-sk-test", base_url="http://localhost:20128/v1")
    
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "choices": [{"message": {"content": "Auth check response"}, "finish_reason": "stop"}],
        "usage": {"prompt_tokens": 5, "completion_tokens": 5},
    }

    with patch("httpx.Client.post", return_value=mock_resp) as mock_post:
        req = LLMRequest(prompt="hello auth", model_name="gpt-4o")
        provider_auth.generate(req)
        
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert kwargs["headers"]["Authorization"] == "Bearer omni-sk-test"

    # Without API key
    provider_no_auth = OmniRouteProvider(api_key=None, base_url="http://localhost:20128/v1")
    with patch("httpx.Client.post", return_value=mock_resp) as mock_post_no_auth:
        req = LLMRequest(prompt="hello no auth", model_name="gpt-4o")
        provider_no_auth.generate(req)
        
        mock_post_no_auth.assert_called_once()
        args, kwargs = mock_post_no_auth.call_args
        assert "Authorization" not in kwargs["headers"]


def test_omniroute_successful_generate():
    provider = OmniRouteProvider(api_key="omni-key", base_url="http://localhost:20128/v1")

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "choices": [{"message": {"content": "OmniRoute response"}, "finish_reason": "stop"}],
        "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
        "model": "meta-llama/llama-3-8b-instruct",
    }

    with patch("httpx.Client.post", return_value=mock_resp) as mock_post:
        req = LLMRequest(prompt="test prompt", model_name="auto/chat", temperature=0.8, max_tokens=150)
        res = provider.generate(req)

        assert res.content == "OmniRoute response"
        assert res.model_name == "meta-llama/llama-3-8b-instruct"
        assert res.provider_name == "omniroute"
        assert res.usage["prompt_tokens"] == 10
        assert res.usage["completion_tokens"] == 20
        assert res.finish_reason == "stop"

        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert kwargs["json"]["model"] == "auto/chat:free"
        assert kwargs["json"]["temperature"] == 0.8
        assert kwargs["json"]["max_tokens"] == 150


def test_omniroute_transient_error_retry():
    provider = OmniRouteProvider(api_key="omni-key", max_retries=3)

    resp_500 = MagicMock()
    resp_500.status_code = 500

    resp_200 = MagicMock()
    resp_200.status_code = 200
    resp_200.json.return_value = {
        "choices": [{"message": {"content": "Recovered from 500"}, "finish_reason": "stop"}],
        "usage": {"prompt_tokens": 5, "completion_tokens": 5},
    }

    with patch("httpx.Client.post", side_effect=[resp_500, resp_200]) as mock_post:
        with patch("time.sleep") as mock_sleep:
            req = LLMRequest(prompt="retry test")
            res = provider.generate(req)

            assert res.content == "Recovered from 500"
            assert mock_post.call_count == 2
            mock_sleep.assert_called_once_with(1)  # 2 ** 0 = 1s sleep


def test_omniroute_exhausted_retries():
    provider = OmniRouteProvider(api_key="omni-key", max_retries=3)

    resp_502 = MagicMock()
    resp_502.status_code = 502

    with patch("httpx.Client.post", return_value=resp_502) as mock_post:
        with patch("time.sleep") as mock_sleep:
            req = LLMRequest(prompt="exhaust retries")
            with pytest.raises(LLMProviderError, match="retries exhausted"):
                provider.generate(req)
            assert mock_post.call_count == 3


def test_omniroute_timeout_handling():
    provider = OmniRouteProvider(api_key="omni-key", max_retries=2)

    with patch("httpx.Client.post", side_effect=httpx.TimeoutException("Timeout occurred")):
        with patch("time.sleep") as mock_sleep:
            req = LLMRequest(prompt="timeout test")
            with pytest.raises(LLMProviderError, match="Failed to connect to OmniRoute"):
                provider.generate(req)


def test_omniroute_streaming():
    provider = OmniRouteProvider(api_key="omni-key", streaming_enabled=True)

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.iter_lines.return_value = [
        b"data: " + json.dumps({"choices": [{"delta": {"content": "Hello"}, "finish_reason": None}], "model": "free-model-1"}).encode("utf-8"),
        b"",
        b"data: " + json.dumps({"choices": [{"delta": {"content": " world"}, "finish_reason": "stop"}], "model": "free-model-1"}).encode("utf-8"),
        b"data: [DONE]"
    ]

    with patch("httpx.Client.stream", return_value=mock_stream_context(mock_resp)) as mock_stream:
        req = LLMRequest(prompt="stream test")
        generator = provider.generate_stream(req)
        responses = list(generator)

        assert len(responses) == 2
        assert responses[0].content == "Hello"
        assert responses[0].model_name == "free-model-1"
        assert responses[1].content == " world"
        assert responses[1].finish_reason == "stop"


def test_omniroute_health_checks():
    provider = OmniRouteProvider(base_url="http://localhost:20128/v1")

    # Case 1: /api/health/ping responds 200
    mock_ping_resp = MagicMock()
    mock_ping_resp.status_code = 200

    with patch("httpx.Client.get", return_value=mock_ping_resp) as mock_get:
        assert provider.check_health() is True
        mock_get.assert_called_once_with("http://localhost:20128/api/health/ping", headers={})

    # Case 2: /api/health/ping fails, but fallback /v1/models succeeds
    mock_ping_fail = MagicMock()
    mock_ping_fail.status_code = 500
    mock_models_success = MagicMock()
    mock_models_success.status_code = 200

    with patch("httpx.Client.get", side_effect=[mock_ping_fail, mock_models_success]) as mock_get:
        assert provider.check_health() is True
        assert mock_get.call_count == 2
        mock_get.assert_any_call("http://localhost:20128/api/health/ping", headers={})
        mock_get.assert_any_call("http://localhost:20128/v1/models", headers={})

    # Case 3: Both fail
    with patch("httpx.Client.get", side_effect=Exception("Connection refused")):
        assert provider.check_health() is False


def test_omniroute_metadata_propagation():
    provider = OmniRouteProvider(base_url="http://localhost:20128/v1")
    req = LLMRequest(
        prompt="coding prompt",
        task_category="coding",
        preferences={"reasoning_depth": "high", "tool_calling": True}
    )

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "choices": [{"message": {"content": "done"}}],
        "model": "gpt-4o",
    }

    with patch("httpx.Client.post", return_value=mock_resp) as mock_post:
        provider.generate(req)
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        headers = kwargs["headers"]
        payload = kwargs["json"]

        # Verify headers
        assert headers["X-OmniRoute-Task-Category"] == "coding"
        assert "X-OmniRoute-Preference-Reasoning-Depth" in headers
        assert headers["X-OmniRoute-Preference-Reasoning-Depth"] == "high"
        assert headers["X-OmniRoute-Preference-Tool-Calling"] == "True"

        # Verify payload metadata
        assert payload["metadata"]["task_category"] == "coding"
        assert payload["metadata"]["preferences"]["reasoning_depth"] == "high"


def test_omniroute_response_diagnostics():
    provider = OmniRouteProvider(base_url="http://localhost:20128/v1")
    req = LLMRequest(prompt="hello", model_name="claude-3-5-sonnet")

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.headers = {
        "X-OmniRoute-Provider": "anthropic",
        "X-OmniRoute-Model": "claude-3-5-sonnet-v2",
        "X-OmniRoute-Fallback": "Yes",
        "X-OmniRoute-Fallback-Reason": "quota_exhaustion",
        "X-OmniRoute-Latency": "1.45",
    }
    mock_resp.json.return_value = {
        "choices": [{"message": {"content": "response"}}],
        "model": "claude-3-5-sonnet-v2",
    }

    with patch("httpx.Client.post", return_value=mock_resp):
        res = provider.generate(req)
        diag = res.metadata["diagnostics"]
        assert diag["selected_provider"] == "anthropic"
        assert diag["selected_model"] == "claude-3-5-sonnet-v2"
        assert diag["fallback_used"] == "Yes"
        assert diag["fallback_reason"] == "quota_exhaustion"
        assert diag["latency"] == 1.45


def test_omniroute_config_loading(tmp_path):
    from aios.config import load_config
    config_file = tmp_path / "config.toml"
    config_file.write_text("""
[runtime]
name = "Personal AI OS"
version = "1.0.0"
debug = false

[llm]
provider = "omniroute"
default_model = "auto/chat"

[llm.omniroute]
base_url = "http://localhost:9999/v1"
api_key = "test-api-key"
routing_policy = "FREE_ONLY"
timeout = 15
retry_count = 5
streaming_enabled = false
offline_mode = true
""")

    cfg = load_config(config_file)
    assert cfg.llm.provider == "omniroute"
    assert cfg.llm.omniroute.base_url == "http://localhost:9999/v1"
    assert cfg.llm.omniroute.api_key == "test-api-key"
    assert cfg.llm.omniroute.routing_policy == "FREE_ONLY"
    assert cfg.llm.omniroute.timeout == 15
    assert cfg.llm.omniroute.retry_count == 5
    assert cfg.llm.omniroute.streaming_enabled is False
    assert cfg.llm.omniroute.offline_mode is True

