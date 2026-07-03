import abc
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from aios.services.base import ServiceLifecycle


@dataclass
class LLMRequest:
    """Represents a unified prompt execution request to an LLM provider."""

    prompt: str
    system_instruction: Optional[str] = None
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    model_name: Optional[str] = None


@dataclass
class LLMResponse:
    """Represents a unified response from an LLM provider."""

    content: str
    model_name: str
    provider_name: str
    usage: Dict[str, int] = field(default_factory=dict)


class LLMProvider(abc.ABC):
    """Abstract interface for all underlying LLM providers."""

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Returns the identifier name of the provider."""
        pass

    @abc.abstractmethod
    def generate(self, request: LLMRequest) -> LLMResponse:
        """Executes content generation based on the request."""
        pass

    @abc.abstractmethod
    def validate_request(self, request: LLMRequest) -> bool:
        """Validates if the request is supported by the provider."""
        pass


class ModelRegistry:
    """Registry mapping model identifiers to provider names."""

    def __init__(self) -> None:
        self._model_to_provider: Dict[str, str] = {}
        # Register standard model mappings
        self.register_model("claude-3-5-sonnet", "claude")
        self.register_model("claude-3-opus", "claude")
        self.register_model("gpt-4o", "openai")
        self.register_model("gpt-3.5-turbo", "openai")
        self.register_model("gemini-1.5-pro", "gemini")
        self.register_model("gemini-1.5-flash", "gemini")
        self.register_model("llama3", "ollama")
        self.register_model("mistral", "ollama")
        self.register_model("mock-model", "mock")

    def register_model(self, model_name: str, provider_name: str) -> None:
        self._model_to_provider[model_name] = provider_name

    def get_provider_for_model(self, model_name: str) -> str:
        if model_name not in self._model_to_provider:
            raise ValueError(f"Model '{model_name}' is not registered in ModelRegistry.")
        return self._model_to_provider[model_name]

    def list_supported_models(self) -> List[str]:
        return list(self._model_to_provider.keys())


class ProviderFactory:
    """Factory for managing and retrieving LLMProvider instances."""

    def __init__(self) -> None:
        self._providers: Dict[str, LLMProvider] = {}

    def register_provider(self, provider: LLMProvider) -> None:
        self._providers[provider.name] = provider

    def get_provider(self, provider_name: str) -> LLMProvider:
        if provider_name not in self._providers:
            raise ValueError(f"Provider '{provider_name}' is not registered in ProviderFactory.")
        return self._providers[provider_name]

    def list_providers(self) -> List[str]:
        return list(self._providers.keys())


class ModelService(ServiceLifecycle, abc.ABC):
    """Unified interface for executing prompts against LLM providers via adapters."""

    @abc.abstractmethod
    def execute_prompt(self, prompt: str, system_instruction: str | None = None) -> str:
        """Executes a text prompt and returns the generated content (backward compatibility)."""
        pass

    @abc.abstractmethod
    def execute_request(self, request: LLMRequest) -> LLMResponse:
        """Executes a unified LLMRequest against the matched provider."""
        pass
