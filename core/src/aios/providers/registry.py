import os
import json
from typing import Dict, List, Optional, Any

from aios.providers.models import (
    ProviderMetadata,
    ProviderCapabilities,
    ProviderStatus,
    DIInitializeMixin,
)
from aios.services.persistence import PersistenceStatus, AIProviderRepository, ProviderCapabilityRepository


class ProviderRegistry(DIInitializeMixin):
    """Production provider registry storing metadata, capabilities, and configurations."""

    def __init__(self, registry: Optional[Any] = None) -> None:
        self._providers: Dict[str, ProviderMetadata] = {}
        self._repo = None
        self._cap_repo = None
        if registry:
            try:
                self._repo = registry.get(AIProviderRepository)
                self._cap_repo = registry.get(ProviderCapabilityRepository)
            except Exception:
                pass
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
        if self._repo:
            try:
                self._repo.save({
                    "id": metadata.name,
                    "name": metadata.name,
                    "version": metadata.version,
                    "priority": metadata.priority,
                    "status": metadata.status.value if hasattr(metadata.status, "value") else str(metadata.status),
                    "context_window": metadata.context_window,
                    "cost_per_million_input": metadata.cost_per_million_input,
                    "cost_per_million_output": metadata.cost_per_million_output,
                    "auth_type": metadata.auth_type,
                    "supported_models": metadata.supported_models,
                    "is_local": metadata.is_local
                })
            except Exception:
                pass
        if self._cap_repo:
            try:
                self._cap_repo.save({
                    "id": f"cap_{metadata.name}",
                    "provider_name": metadata.name,
                    "capabilities": {
                        "streaming": metadata.capabilities.streaming,
                        "vision": metadata.capabilities.vision,
                        "function_calling": metadata.capabilities.function_calling,
                        "tools": metadata.capabilities.tools,
                        "structured_output": metadata.capabilities.structured_output,
                        "code_generation": metadata.capabilities.code_generation,
                        "editing": metadata.capabilities.editing,
                        "reasoning": metadata.capabilities.reasoning,
                        "long_context": metadata.capabilities.long_context
                    },
                    "timestamp": time.time()
                })
            except Exception:
                pass

    def get_provider(self, name: str) -> Optional[ProviderMetadata]:
        # Handle aliases like 'anthropic' -> 'claude_code'
        if name == "anthropic" or name == "claude":
            name = "claude_code"
        elif name == "gemini":
            name = "gemini_cli"

        if name in self._providers:
            return self._providers[name]

        if self._repo:
            try:
                res = self._repo.get(name)
                if res.status == PersistenceStatus.SUCCESS and res.payload:
                    p = res.payload
                    caps = ProviderCapabilities()
                    if self._cap_repo:
                        cap_res = self._cap_repo.get(f"cap_{name}")
                        if cap_res.status == PersistenceStatus.SUCCESS and cap_res.payload:
                            c_data = cap_res.payload.get("capabilities", {})
                            caps = ProviderCapabilities(
                                streaming=c_data.get("streaming", False),
                                vision=c_data.get("vision", False),
                                function_calling=c_data.get("function_calling", False),
                                tools=c_data.get("tools", False),
                                structured_output=c_data.get("structured_output", False),
                                code_generation=c_data.get("code_generation", False),
                                editing=c_data.get("editing", False),
                                reasoning=c_data.get("reasoning", False),
                                long_context=c_data.get("long_context", False)
                            )
                    metadata = ProviderMetadata(
                        name=p["name"],
                        version=p["version"],
                        priority=p["priority"],
                        status=ProviderStatus(p["status"]) if hasattr(ProviderStatus, p["status"]) else ProviderStatus.ONLINE,
                        context_window=p["context_window"],
                        cost_per_million_input=p["cost_per_million_input"],
                        cost_per_million_output=p["cost_per_million_output"],
                        auth_type=p["auth_type"],
                        supported_models=p["supported_models"],
                        is_local=p["is_local"],
                        capabilities=caps
                    )
                    self._providers[name] = metadata
                    return metadata
            except Exception:
                pass

        return None

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
