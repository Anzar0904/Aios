from aios.providers.adapters import MockProvider
from aios.providers.interface import (
    ModelInfo,
    universal_model_registry,
    universal_provider_registry,
)
from aios.services.model import LLMRequest
from aios.services.model_impl import LocalModelService


def test_model_registry():
    universal_model_registry.register_model(
        ModelInfo(provider="openai", model_id="gpt-4o", display_name="GPT-4o", family="GPT")
    )
    assert universal_model_registry.get_model("gpt-4o").provider == "openai"


def test_provider_registry():
    universal_provider_registry.register(MockProvider())
    assert universal_provider_registry.lookup("mock").name == "mock"


def test_individual_mock_providers():
    mock = MockProvider()
    res_mock = mock.generate(model="mock-model", prompt="hello")
    assert "[MockProvider]" in res_mock


def test_local_model_service():
    from unittest.mock import MagicMock, patch

    service = LocalModelService(default_model="mock-model")
    service.initialize()

    mock_res = MagicMock()
    mock_res.status_code = 200
    mock_res.json.return_value = {"choices": [{"message": {"content": "mocked response"}}]}

    with patch("httpx.Client.post", return_value=mock_res):
        resp_prompt = service.execute_prompt("test prompt")
        assert resp_prompt is not None

        req_claude = LLMRequest(prompt="hello claude", model_name="claude-3-5-sonnet")
        resp_claude = service.execute_request(req_claude)
        assert resp_claude.provider_name == "claude"
