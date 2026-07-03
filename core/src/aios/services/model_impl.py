import logging

from aios.services.model import (
    LLMProvider,
    LLMRequest,
    LLMResponse,
    ModelRegistry,
    ModelService,
    ProviderFactory,
)

logger = logging.getLogger(__name__)


class MockProvider(LLMProvider):
    @property
    def name(self) -> str:
        return "mock"

    def generate(self, request: LLMRequest) -> LLMResponse:
        content = f"[MockProvider] Response to prompt: '{request.prompt}'"
        if request.system_instruction:
            content = f"Instruction: {request.system_instruction}\n{content}"
        return LLMResponse(
            content=content,
            model_name=request.model_name or "mock-model",
            provider_name=self.name,
            usage={"prompt_tokens": 10, "completion_tokens": 20},
        )

    def validate_request(self, request: LLMRequest) -> bool:
        return True


class OpenAIProvider(LLMProvider):
    @property
    def name(self) -> str:
        return "openai"

    def generate(self, request: LLMRequest) -> LLMResponse:
        content = f"[OpenAIProvider] Mock response to prompt: '{request.prompt}'"
        if request.system_instruction:
            content = f"System: {request.system_instruction}\n{content}"
        return LLMResponse(
            content=content,
            model_name=request.model_name or "gpt-4o",
            provider_name=self.name,
            usage={"prompt_tokens": 12, "completion_tokens": 25},
        )

    def validate_request(self, request: LLMRequest) -> bool:
        return True


class ClaudeProvider(LLMProvider):
    @property
    def name(self) -> str:
        return "claude"

    def generate(self, request: LLMRequest) -> LLMResponse:
        content = f"[ClaudeProvider] Mock response to prompt: '{request.prompt}'"
        if request.system_instruction:
            content = f"System: {request.system_instruction}\n{content}"
        return LLMResponse(
            content=content,
            model_name=request.model_name or "claude-3-5-sonnet",
            provider_name=self.name,
            usage={"prompt_tokens": 15, "completion_tokens": 30},
        )

    def validate_request(self, request: LLMRequest) -> bool:
        return True


class GeminiProvider(LLMProvider):
    @property
    def name(self) -> str:
        return "gemini"

    def generate(self, request: LLMRequest) -> LLMResponse:
        content = f"[GeminiProvider] Mock response to prompt: '{request.prompt}'"
        if request.system_instruction:
            content = f"System: {request.system_instruction}\n{content}"
        return LLMResponse(
            content=content,
            model_name=request.model_name or "gemini-1.5-pro",
            provider_name=self.name,
            usage={"prompt_tokens": 8, "completion_tokens": 18},
        )

    def validate_request(self, request: LLMRequest) -> bool:
        return True


class OllamaProvider(LLMProvider):
    @property
    def name(self) -> str:
        return "ollama"

    def generate(self, request: LLMRequest) -> LLMResponse:
        content = f"[OllamaProvider] Mock local response to prompt: '{request.prompt}'"
        if request.system_instruction:
            content = f"System: {request.system_instruction}\n{content}"
        return LLMResponse(
            content=content,
            model_name=request.model_name or "llama3",
            provider_name=self.name,
            usage={"prompt_tokens": 0, "completion_tokens": 0},
        )

    def validate_request(self, request: LLMRequest) -> bool:
        return True


class LocalModelService(ModelService):
    """Concrete implementation of ModelService coordinating model routing

    across multiple registered providers via registries and factories.
    """

    def __init__(self, default_model: str = "mock-model") -> None:
        self.registry = ModelRegistry()
        self.factory = ProviderFactory()
        self._default_model = default_model

    def initialize(self) -> None:
        logger.info("Initializing LocalModelService")
        self.factory.register_provider(MockProvider())
        self.factory.register_provider(OpenAIProvider())
        self.factory.register_provider(ClaudeProvider())
        self.factory.register_provider(GeminiProvider())
        self.factory.register_provider(OllamaProvider())

    def execute_prompt(self, prompt: str, system_instruction: str | None = None) -> str:
        req = LLMRequest(
            prompt=prompt,
            system_instruction=system_instruction,
            model_name=self._default_model,
        )
        res = self.execute_request(req)
        return res.content

    def execute_request(self, request: LLMRequest) -> LLMResponse:
        model_name = request.model_name or self._default_model

        provider_name = self.registry.get_provider_for_model(model_name)

        provider = self.factory.get_provider(provider_name)

        if not provider.validate_request(request):
            raise ValueError(f"Request validation failed for provider '{provider_name}'")

        logger.info(f"Routing request to provider '{provider_name}' for model '{model_name}'")

        if not request.model_name:
            request.model_name = model_name

        return provider.generate(request)
