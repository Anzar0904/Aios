import os
from typing import Dict, List, Optional, Any

from aios.providers.models import (
    ProviderMetadata,
    ProviderCapabilities,
    ProviderStatus,
    DIInitializeMixin,
)


class ProviderRegistry(DIInitializeMixin):
    """Production provider registry storing metadata, capabilities, and configurations."""

    def __init__(self) -> None:
        self._providers: Dict[str, ProviderMetadata] = {}
        self._initialize_defaults()

    def _initialize_defaults(self) -> None:
        # Claude Code Adapter
        self.register_provider(
            ProviderMetadata(
                name="claude_code",
                version="3.5",
                capabilities=ProviderCapabilities(
                    streaming=True,
                    vision=True,
                    function_calling=True,
                    tools=True,
                    code_generation=True,
                    editing=True,
                    long_context=True
                ),
                priority=1,
                status=ProviderStatus.ONLINE,
                context_window=200000,
                cost_per_million_input=3.00,
                cost_per_million_output=15.00,
                auth_type="api_key",
                supported_models=["claude-3-5-sonnet", "claude-3-opus", "claude-code"],
                is_local=False
            )
        )

        # Gemini CLI Adapter
        self.register_provider(
            ProviderMetadata(
                name="gemini_cli",
                version="1.5",
                capabilities=ProviderCapabilities(
                    streaming=False,
                    vision=True,
                    function_calling=True,
                    tools=True,
                    code_generation=True,
                    reasoning=True,
                    long_context=True
                ),
                priority=2,
                status=ProviderStatus.ONLINE,
                context_window=1000000,
                cost_per_million_input=1.25,
                cost_per_million_output=3.75,
                auth_type="none",
                supported_models=["gemini-1.5-pro", "gemini-1.5-flash", "gemini-cli"],
                is_local=False
            )
        )

        # OpenAI Adapter
        self.register_provider(
            ProviderMetadata(
                name="openai",
                version="4.0",
                capabilities=ProviderCapabilities(
                    streaming=True,
                    vision=True,
                    function_calling=True,
                    tools=True,
                    structured_output=True,
                    code_generation=True
                ),
                priority=3,
                status=ProviderStatus.ONLINE,
                context_window=128000,
                cost_per_million_input=5.00,
                cost_per_million_output=15.00,
                auth_type="api_key",
                supported_models=["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"],
                is_local=False
            )
        )

        # OmniRoute Gateway mapping (for backward compatibility)
        self.register_provider(
            ProviderMetadata(
                name="omniroute",
                version="1.0.0",
                capabilities=ProviderCapabilities(
                    streaming=True, vision=True, function_calling=True, tools=True
                ),
                priority=0,
                status=ProviderStatus.ONLINE,
                context_window=1000000,
                cost_per_million_input=0.0,
                cost_per_million_output=0.0,
                auth_type="api_key",
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
                is_local=False
            )
        )

        # Ollama local (for backward compatibility)
        self.register_provider(
            ProviderMetadata(
                name="ollama",
                version="0.1.0",
                capabilities=ProviderCapabilities(
                    streaming=True, vision=False, function_calling=False
                ),
                priority=4,
                status=ProviderStatus.ONLINE,
                context_window=8192,
                cost_per_million_input=0.0,
                cost_per_million_output=0.0,
                auth_type="none",
                supported_models=["llama3", "mistral", "phi3", "codellama"],
                is_local=True
            )
        )

        # LMStudio local (for backward compatibility)
        self.register_provider(
            ProviderMetadata(
                name="lmstudio",
                version="0.1.0",
                capabilities=ProviderCapabilities(
                    streaming=True, vision=False, function_calling=False
                ),
                priority=5,
                status=ProviderStatus.ONLINE,
                context_window=4096,
                cost_per_million_input=0.0,
                cost_per_million_output=0.0,
                auth_type="none",
                supported_models=["luna-7b", "hermes-2-pro"],
                is_local=True
            )
        )

        # Mock (for backward compatibility / fallback)
        self.register_provider(
            ProviderMetadata(
                name="mock",
                version="1.0.0",
                capabilities=ProviderCapabilities(
                    streaming=True, vision=True, function_calling=True
                ),
                priority=99,
                status=ProviderStatus.ONLINE,
                context_window=1000000,
                cost_per_million_input=0.0,
                cost_per_million_output=0.0,
                auth_type="none",
                supported_models=["mock-model"],
                is_local=True
            )
        )

    def register_provider(self, metadata: ProviderMetadata) -> None:
        self._providers[metadata.name] = metadata

    def get_provider(self, name: str) -> Optional[ProviderMetadata]:
        # Handle aliases like 'anthropic' -> 'claude_code'
        if name == "anthropic" or name == "claude":
            name = "claude_code"
        elif name == "gemini":
            name = "gemini_cli"
        return self._providers.get(name)

    def list_providers(self) -> List[ProviderMetadata]:
        return list(self._providers.values())


class ProviderConfigurationService(DIInitializeMixin):
    """Manages credentials and engineering profile configuration preferences."""

    def __init__(self) -> None:
        self._configs: Dict[str, Dict[str, Any]] = {}
        self._preferences: Dict[str, Any] = {
            "preferred_provider": "openai",
            "fallback_providers": ["claude_code", "gemini_cli"],
            "max_cost": 10.0,
            "min_quality": 7.0,
            "preferred_latency": 2.0,
            "preferred_context_size": 8192,
            "routing_strategy": "hybrid"
        }

    def get_config(self, provider_name: str) -> Dict[str, Any]:
        return self._configs.get(provider_name, {})

    def set_config(self, provider_name: str, config: Dict[str, Any]) -> None:
        self._configs[provider_name] = config

    def get_preferences(self) -> Dict[str, Any]:
        return self._preferences

    def set_preferences(self, preferences: Dict[str, Any]) -> None:
        self._preferences.update(preferences)


class ProviderDiscoveryService(DIInitializeMixin):
    """Discovers available local CLI commands and remote API keys."""

    def __init__(self, registry: ProviderRegistry, config_service: ProviderConfigurationService) -> None:
        self._registry = registry
        self._config_service = config_service

    def discover_providers(self) -> None:
        for p in self._registry.list_providers():
            # Check environment keys
            key_name = f"{p.name.upper()}_API_KEY"
            if p.name == "claude_code":
                key = os.environ.get("CLAUDE_CODE_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")
            elif p.name == "gemini_cli":
                key = os.environ.get("GEMINI_API_KEY") or "cli_active"
            else:
                key = os.environ.get(key_name)

            cfg = self._config_service.get_config(p.name)
            api_key = key or cfg.get("api_key")

            if p.auth_type == "none" or api_key:
                p.status = ProviderStatus.ONLINE
                p.configuration["api_key"] = api_key
            else:
                p.status = ProviderStatus.OFFLINE


class ProviderManager(DIInitializeMixin):
    """Conductor coordinating discovery, registration, and health monitoring."""

    def __init__(
        self,
        registry: ProviderRegistry,
        config_service: ProviderConfigurationService,
        discovery_service: ProviderDiscoveryService,
        health_monitor: Any,
        quota_manager: Any
    ) -> None:
        self.registry = registry
        self.config_service = config_service
        self.discovery_service = discovery_service
        self.health_monitor = health_monitor
        self.quota_manager = quota_manager

    def initialize(self) -> None:
        self.discovery_service.discover_providers()
