import pytest
from aios.services.model import LLMRequest, ModelRegistry, ProviderFactory
from aios.services.model_impl import (
    ClaudeProvider,
    GeminiProvider,
    LocalModelService,
    MockProvider,
    OllamaProvider,
    OpenAIProvider,
)


def test_model_registry():
    registry = ModelRegistry()

    # Verify standard mappings
    assert registry.get_provider_for_model("claude-3-5-sonnet") == "claude"
    assert registry.get_provider_for_model("gpt-4o") == "openai"
    assert registry.get_provider_for_model("gemini-1.5-pro") == "gemini"
    assert registry.get_provider_for_model("llama3") == "ollama"
    assert registry.get_provider_for_model("mock-model") == "mock"

    # Register new mapping
    registry.register_model("custom-llm", "openai")
    assert registry.get_provider_for_model("custom-llm") == "openai"

    # Unregistered model raises ValueError
    with pytest.raises(ValueError, match="is not registered"):
        registry.get_provider_for_model("unregistered-model")


def test_provider_factory():
    factory = ProviderFactory()
    mock_provider = MockProvider()

    factory.register_provider(mock_provider)
    assert factory.get_provider("mock") == mock_provider
    assert "mock" in factory.list_providers()

    with pytest.raises(ValueError, match="is not registered"):
        factory.get_provider("unknown-provider")


def test_individual_mock_providers():
    req = LLMRequest(prompt="hello", system_instruction="act nice")

    # Mock
    mock = MockProvider()
    res_mock = mock.generate(req)
    assert res_mock.provider_name == "mock"
    assert "[MockProvider]" in res_mock.content

    # OpenAI
    openai = OpenAIProvider()
    res_openai = openai.generate(req)
    assert res_openai.provider_name == "openai"
    assert "[OpenAIProvider]" in res_openai.content

    # Claude
    claude = ClaudeProvider()
    res_claude = claude.generate(req)
    assert res_claude.provider_name == "claude"
    assert "[ClaudeProvider]" in res_claude.content

    # Gemini
    gemini = GeminiProvider()
    res_gemini = gemini.generate(req)
    assert res_gemini.provider_name == "gemini"
    assert "[GeminiProvider]" in res_gemini.content

    # Ollama
    ollama = OllamaProvider()
    res_ollama = ollama.generate(req)
    assert res_ollama.provider_name == "ollama"
    assert "[OllamaProvider]" in res_ollama.content


def test_local_model_service():
    service = LocalModelService(default_model="mock-model")
    service.initialize()

    # execute_prompt
    resp_prompt = service.execute_prompt("test prompt")
    assert "[MockProvider]" in resp_prompt

    # execute_request routing to Claude
    req_claude = LLMRequest(prompt="hello claude", model_name="claude-3-5-sonnet")
    resp_claude = service.execute_request(req_claude)
    assert resp_claude.provider_name == "claude"
    assert "[ClaudeProvider]" in resp_claude.content

    # execute_request routing to OpenAI
    req_openai = LLMRequest(prompt="hello openai", model_name="gpt-4o")
    resp_openai = service.execute_request(req_openai)
    assert resp_openai.provider_name == "openai"
    assert "[OpenAIProvider]" in resp_openai.content
