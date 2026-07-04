from typing import Dict, List, Optional

from aios.providers.models import ProviderCapabilities, ProviderInfo


class ProviderRegistry:
    def __init__(self) -> None:
        self._providers: Dict[str, ProviderInfo] = {}
        self._initialize_defaults()

    def _initialize_defaults(self) -> None:
        # OpenRouter
        self.register_provider(
            ProviderInfo(
                name="openrouter",
                supported_models=[
                    "qwen/qwen3-coder",
                    "anthropic/claude-3-5-sonnet",
                    "meta-llama/llama-3-8b-instruct",
                ],
                context_window=128000,
                capabilities=ProviderCapabilities(
                    streaming=True, vision=True, function_calling=True
                ),
                cost_per_million_input=0.15,
                cost_per_million_output=0.60,
                is_local=False,
            )
        )

        # OpenAI
        self.register_provider(
            ProviderInfo(
                name="openai",
                supported_models=["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"],
                context_window=128000,
                capabilities=ProviderCapabilities(
                    streaming=True, vision=True, function_calling=True
                ),
                cost_per_million_input=5.00,
                cost_per_million_output=15.00,
                is_local=False,
            )
        )

        # Anthropic
        self.register_provider(
            ProviderInfo(
                name="anthropic",
                supported_models=["claude-3-5-sonnet", "claude-3-opus", "claude-3-haiku"],
                context_window=200000,
                capabilities=ProviderCapabilities(
                    streaming=True, vision=True, function_calling=True
                ),
                cost_per_million_input=3.00,
                cost_per_million_output=15.00,
                is_local=False,
            )
        )

        # Gemini
        self.register_provider(
            ProviderInfo(
                name="gemini",
                supported_models=["gemini-1.5-pro", "gemini-1.5-flash"],
                context_window=1000000,
                capabilities=ProviderCapabilities(
                    streaming=True, vision=True, function_calling=True
                ),
                cost_per_million_input=1.25,
                cost_per_million_output=3.75,
                is_local=False,
            )
        )

        # Ollama
        self.register_provider(
            ProviderInfo(
                name="ollama",
                supported_models=["llama3", "mistral", "phi3", "codellama"],
                context_window=8192,
                capabilities=ProviderCapabilities(
                    streaming=True, vision=False, function_calling=False
                ),
                cost_per_million_input=0.0,
                cost_per_million_output=0.0,
                is_local=True,
            )
        )

        # LM Studio
        self.register_provider(
            ProviderInfo(
                name="lmstudio",
                supported_models=["luna-7b", "hermes-2-pro"],
                context_window=4096,
                capabilities=ProviderCapabilities(
                    streaming=True, vision=False, function_calling=False
                ),
                cost_per_million_input=0.0,
                cost_per_million_output=0.0,
                is_local=True,
            )
        )

        # Mock
        self.register_provider(
            ProviderInfo(
                name="mock",
                supported_models=["mock-model"],
                context_window=1000000,
                capabilities=ProviderCapabilities(
                    streaming=True, vision=True, function_calling=True
                ),
                cost_per_million_input=0.0,
                cost_per_million_output=0.0,
                is_local=True,
            )
        )

        # OmniRoute
        self.register_provider(
            ProviderInfo(
                name="omniroute",
                supported_models=[
                    "auto",
                    "auto/coding",
                    "auto/reasoning",
                    "auto/chat",
                    "auto/multimodal",
                    "auto/vision",
                    "auto/fast",
                    "auto/cheap",
                    "auto/smart",
                    "auto/lkgp",
                    "claude-3-5-sonnet",
                    "gpt-4o",
                    "gemini-1.5-pro",
                    "llama3",
                    "mock-model",
                ],
                context_window=1000000,
                capabilities=ProviderCapabilities(
                    streaming=True, vision=True, function_calling=True
                ),
                cost_per_million_input=0.0,
                cost_per_million_output=0.0,
                is_local=False,  # External gateway capability
            )
        )


    def register_provider(self, info: ProviderInfo) -> None:

        self._providers[info.name] = info

    def get_provider(self, name: str) -> Optional[ProviderInfo]:
        return self._providers.get(name)

    def list_providers(self) -> List[ProviderInfo]:
        return list(self._providers.values())
