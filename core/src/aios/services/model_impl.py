import logging
import os
import time
from typing import Iterator, Optional

import httpx

from aios.config import load_config
from aios.services.model import (
    LLMProvider,
    LLMRequest,
    LLMResponse,
    ModelRegistry,
    ModelService,
    ProviderFactory,
)

logger = logging.getLogger(__name__)


class LLMProviderError(Exception):
    """Structured error returned from LLM providers."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_body: Optional[str] = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body


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
            finish_reason="stop",
            metadata={},
        )

    def validate_request(self, request: LLMRequest) -> bool:
        return True

    def generate_stream(self, request: LLMRequest) -> Iterator[LLMResponse]:
        yield self.generate(request)


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
            finish_reason="stop",
            metadata={},
        )

    def validate_request(self, request: LLMRequest) -> bool:
        return True

    def generate_stream(self, request: LLMRequest) -> Iterator[LLMResponse]:
        yield self.generate(request)


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
            finish_reason="stop",
            metadata={},
        )

    def validate_request(self, request: LLMRequest) -> bool:
        return True

    def generate_stream(self, request: LLMRequest) -> Iterator[LLMResponse]:
        yield self.generate(request)


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
            finish_reason="stop",
            metadata={},
        )

    def validate_request(self, request: LLMRequest) -> bool:
        return True

    def generate_stream(self, request: LLMRequest) -> Iterator[LLMResponse]:
        yield self.generate(request)


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
            finish_reason="stop",
            metadata={},
        )

    def validate_request(self, request: LLMRequest) -> bool:
        return True

    def generate_stream(self, request: LLMRequest) -> Iterator[LLMResponse]:
        yield self.generate(request)


class OpenRouterProvider(LLMProvider):
    """Production-ready OpenRouter LLM Provider implementing unified adapter."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://openrouter.ai/api/v1",
        timeout: int = 30,
        max_retries: int = 3,
    ) -> None:
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._max_retries = max_retries

    @property
    def name(self) -> str:
        return "openrouter"

    def generate(self, request: LLMRequest) -> LLMResponse:
        if not self.validate_request(request):
            raise LLMProviderError("Request validation failed.")

        if not self._api_key:
            raise LLMProviderError(
                "OpenRouter API key is missing. "
                "Please set the OPENROUTER_API_KEY environment variable."
            )

        endpoint = f"{self._base_url}/chat/completions"

        messages = []
        if request.system_instruction:
            messages.append({"role": "system", "content": request.system_instruction})
        messages.append({"role": "user", "content": request.prompt})

        payload = {
            "model": request.model_name or "qwen/qwen3-coder",
            "messages": messages,
            "temperature": request.temperature,
        }
        if request.max_tokens is not None:
            payload["max_tokens"] = request.max_tokens

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/Anzar0904/Aios",
            "X-Title": "Personal AI OS",
        }

        last_exception = None
        for attempt in range(self._max_retries):
            try:
                logger.info(f"OpenRouter API call attempt {attempt + 1}/{self._max_retries}")
                with httpx.Client(timeout=float(self._timeout)) as client:
                    response = client.post(endpoint, json=payload, headers=headers)

                if response.status_code in (429, 500, 502, 503, 504):
                    logger.warning(
                        f"Transient HTTP error {response.status_code} "
                        f"received on attempt {attempt + 1}"
                    )
                    time.sleep(2**attempt)
                    continue

                if response.status_code != 200:
                    raise LLMProviderError(
                        message=f"OpenRouter API returned error status {response.status_code}",
                        status_code=response.status_code,
                        response_body=response.text,
                    )

                data = response.json()
                choice = data["choices"][0]
                message_content = choice["message"]["content"]
                finish_reason = choice.get("finish_reason")
                usage = data.get("usage", {})

                return LLMResponse(
                    content=message_content,
                    model_name=data.get("model", request.model_name or "qwen/qwen3-coder"),
                    provider_name=self.name,
                    usage={
                        "prompt_tokens": usage.get("prompt_tokens", 0),
                        "completion_tokens": usage.get("completion_tokens", 0),
                        "total_tokens": usage.get("total_tokens", 0),
                    },
                    finish_reason=finish_reason,
                    metadata=data,
                )

            except (httpx.TimeoutException, httpx.NetworkError) as e:
                logger.warning(f"Network error on attempt {attempt + 1}: {e}")
                last_exception = e
                time.sleep(2**attempt)

        if last_exception:
            raise LLMProviderError(
                message=(
                    f"Failed to connect to OpenRouter after {self._max_retries} "
                    f"attempts: {last_exception}"
                )
            )
        else:
            raise LLMProviderError("Failed to execute OpenRouter request (retries exhausted).")

    def validate_request(self, request: LLMRequest) -> bool:
        if request.temperature < 0.0 or request.temperature > 2.0:
            return False
        if request.max_tokens is not None and request.max_tokens <= 0:
            return False
        return True

    def generate_stream(self, request: LLMRequest) -> Iterator[LLMResponse]:
        yield self.generate(request)


class LocalModelService(ModelService):
    """Concrete implementation of ModelService coordinating model routing

    across multiple registered providers via registries and factories.
    """

    def __init__(self, default_model: str = None, config_path: str = "config/config.toml") -> None:
        self.registry = ModelRegistry()
        self.factory = ProviderFactory()
        self._default_model = default_model
        self._config_path = config_path

    def initialize(self) -> None:
        logger.info("Initializing LocalModelService")
        from pathlib import Path

        config = load_config(Path(self._config_path))

        if not self._default_model:
            self._default_model = config.llm.default_model or "mock-model"

        self.factory.register_provider(MockProvider())
        self.factory.register_provider(OpenAIProvider())
        self.factory.register_provider(ClaudeProvider())
        self.factory.register_provider(GeminiProvider())
        self.factory.register_provider(OllamaProvider())

        api_key = os.environ.get("OPENROUTER_API_KEY")
        self.factory.register_provider(
            OpenRouterProvider(
                api_key=api_key,
                base_url=config.llm.openrouter.base_url,
                timeout=config.llm.openrouter.timeout,
            )
        )

        # Register default model dynamically
        if self._default_model != "mock-model":
            self.registry.register_model(self._default_model, config.llm.provider)

        # Handle slash-based OpenRouter fallback in ModelRegistry lookup if needed
        # We can dynamically overwrite ModelRegistry.get_provider_for_model in self
        orig_get = self.registry.get_provider_for_model

        def dynamic_get_provider(model_name: str) -> str:
            try:
                return orig_get(model_name)
            except ValueError:
                if "/" in model_name:
                    return "openrouter"
                raise

        self.registry.get_provider_for_model = dynamic_get_provider

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

    def execute_stream(self, request: LLMRequest) -> Iterator[LLMResponse]:
        model_name = request.model_name or self._default_model
        provider_name = self.registry.get_provider_for_model(model_name)
        provider = self.factory.get_provider(provider_name)

        if not provider.validate_request(request):
            raise ValueError(f"Request validation failed for provider '{provider_name}'")

        if not request.model_name:
            request.model_name = model_name

        return provider.generate_stream(request)
