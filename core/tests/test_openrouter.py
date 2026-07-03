import os
from unittest.mock import MagicMock, patch

import httpx
import pytest
from aios.services.model import LLMRequest
from aios.services.model_impl import (
    LLMProviderError,
    LocalModelService,
    OpenRouterProvider,
)


def test_openrouter_api_key_missing():
    provider = OpenRouterProvider(api_key=None)
    req = LLMRequest(prompt="hello")
    with pytest.raises(LLMProviderError, match="OpenRouter API key is missing"):
        provider.generate(req)


def test_openrouter_validation():
    provider = OpenRouterProvider(api_key="sk-test")
    # Valid
    assert provider.validate_request(LLMRequest(prompt="hello", temperature=0.7)) is True

    # Invalid temp
    assert provider.validate_request(LLMRequest(prompt="hello", temperature=2.5)) is False

    # Invalid max_tokens
    assert provider.validate_request(LLMRequest(prompt="hello", max_tokens=-10)) is False


def test_openrouter_successful_generate():
    provider = OpenRouterProvider(api_key="sk-test", base_url="https://openrouter.ai/api/v1")

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "choices": [{"message": {"content": "Hello from model"}, "finish_reason": "stop"}],
        "usage": {"prompt_tokens": 10, "completion_tokens": 15},
        "model": "qwen/qwen3-coder",
    }

    with patch("httpx.Client.post", return_value=mock_resp) as mock_post:
        req = LLMRequest(
            prompt="hello", system_instruction="be code", temperature=0.5, max_tokens=100
        )
        res = provider.generate(req)

        assert res.content is not None
        assert res.content == "Hello from model"
        assert res.model_name == "qwen/qwen3-coder"
        assert res.provider_name == "openrouter"
        assert res.usage["prompt_tokens"] == 10
        assert res.finish_reason == "stop"

        # Check payload
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert kwargs["json"]["temperature"] == 0.5
        assert kwargs["json"]["max_tokens"] == 100
        assert kwargs["json"]["messages"][0] == {"role": "system", "content": "be code"}
        assert kwargs["json"]["messages"][1] == {"role": "user", "content": "hello"}


def test_openrouter_transient_error_retry():
    provider = OpenRouterProvider(
        api_key="sk-test", base_url="https://openrouter.ai/api/v1", max_retries=3
    )

    # First attempt: 502 Bad Gateway
    # Second attempt: 200 OK
    resp_502 = MagicMock()
    resp_502.status_code = 502

    resp_200 = MagicMock()
    resp_200.status_code = 200
    resp_200.json.return_value = {
        "choices": [{"message": {"content": "Retry success"}, "finish_reason": "stop"}],
        "usage": {"prompt_tokens": 5, "completion_tokens": 5},
    }

    with patch("httpx.Client.post", side_effect=[resp_502, resp_200]) as mock_post:
        with patch("time.sleep") as mock_sleep:
            req = LLMRequest(prompt="hello retry")
            res = provider.generate(req)

            assert res.content == "Retry success"
            assert mock_post.call_count == 2
            mock_sleep.assert_called_once_with(1)  # 2 ** 0 = 1s sleep


def test_openrouter_exhausted_retries():
    provider = OpenRouterProvider(
        api_key="sk-test", base_url="https://openrouter.ai/api/v1", max_retries=3
    )

    resp_500 = MagicMock()
    resp_500.status_code = 500

    with patch("httpx.Client.post", return_value=resp_500) as mock_post:
        with patch("time.sleep"):
            req = LLMRequest(prompt="hello fail")
            with pytest.raises(LLMProviderError, match="Failed to execute OpenRouter request"):
                provider.generate(req)
            assert mock_post.call_count == 3


def test_openrouter_network_error():
    provider = OpenRouterProvider(
        api_key="sk-test", base_url="https://openrouter.ai/api/v1", max_retries=2
    )

    with patch("httpx.Client.post", side_effect=httpx.ConnectError("Network down")):
        with patch("time.sleep"):
            req = LLMRequest(prompt="hello offline")
            with pytest.raises(LLMProviderError, match="Failed to connect to OpenRouter"):
                provider.generate(req)


def test_local_model_service_openrouter_routing(tmp_path):
    config_file = tmp_path / "config.toml"
    config_file.write_text("""
[llm]
provider = "openrouter"
default_model = "qwen/qwen3-coder"

[llm.openrouter]
base_url = "https://openrouter.ai/api/v1"
timeout = 15
""")

    with patch.dict(os.environ, {"OPENROUTER_API_KEY": "sk-test-env"}):
        service = LocalModelService(config_path=str(config_file))
        service.initialize()

        # Check default model from config
        assert service._default_model == "qwen/qwen3-coder"

        # Check provider mapped dynamically for "qwen/qwen3-coder"
        assert service.registry.get_provider_for_model("qwen/qwen3-coder") == "openrouter"

        # Check dynamic slash fallback for any custom model
        assert service.registry.get_provider_for_model("meta-llama/llama-3") == "openrouter"
