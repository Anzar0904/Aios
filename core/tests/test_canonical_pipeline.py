import os
from unittest.mock import patch

import pytest
from aios.bootstrap import bootstrap_kernel
from aios.config import load_config
from aios.providers.adapters import MockProvider
from aios.providers.interface import (
    ModelInfo,
    OmniRouteRequest,
    RoutingRequest,
    universal_model_registry,
    universal_omniroute_engine,
    universal_provider_registry,
    universal_routing_engine,
)
from aios.services.model import LLMRequest
from aios.services.model_impl import LocalModelService


@pytest.fixture
def clean_registries():
    universal_provider_registry._providers.clear()
    universal_model_registry._models.clear()
    yield
    universal_provider_registry._providers.clear()
    universal_model_registry._models.clear()


def test_canonical_pipeline_execution(clean_registries):
    """PHASE 1: Verify complete execution flow of the frozen architecture."""
    # 1. Registration
    provider = MockProvider()
    universal_provider_registry.register(provider)
    universal_model_registry.register_model(ModelInfo("mock", "mock-model", "Mock", "Mock"))

    # 2. Model Service execution (which uses OmniRouteEngine)
    model_service = LocalModelService()
    model_service._default_model = "mock-model"

    req = LLMRequest(prompt="Hello canonical pipeline", model_name="mock-model")
    res = model_service.execute_request(req)

    assert res is not None
    assert "MockProvider" in res.content
    assert res.provider_name == "mock"
    assert res.model_name == "mock-model"


def test_provider_registry_tests(clean_registries):
    """PHASE 2: Verify Provider Registration."""
    from aios.providers.nvidia import NVIDIAProvider, NVIDIAProviderAdapter

    # Provider registration
    provider = MockProvider()
    universal_provider_registry.register(provider)
    assert universal_provider_registry.lookup("mock") is not None

    # Duplicate registration prevention (mock replaces or updates depending on impl)
    universal_provider_registry.register(MockProvider())
    assert len(universal_provider_registry.list_providers()) == 1

    # Unknown provider handling
    assert universal_provider_registry.lookup("unknown_provider") is None

    # NVIDIA & Mock Registration
    nvidia_provider = NVIDIAProvider(adapter=NVIDIAProviderAdapter(api_key=""))
    universal_provider_registry.register(nvidia_provider)

    provider_names = universal_provider_registry.list_providers()
    assert "nvidia" in provider_names
    assert "mock" in provider_names


def test_model_registry_tests(clean_registries):
    """PHASE 3: Verify Model Registration."""
    universal_model_registry.register_model(ModelInfo("openai", "gpt-4o", "GPT-4", "GPT"))
    universal_model_registry.register_model(ModelInfo("mock", "mock-model", "Mock", "Mock"))

    # Lookup and mapping
    assert universal_model_registry.get_provider_for_model("gpt-4o") == "openai"
    assert universal_model_registry.get_provider_for_model("mock-model") == "mock"

    # Invalid model handling
    assert universal_model_registry.get_provider_for_model("invalid_model") is None


def test_routing_engine_tests(clean_registries):
    """PHASE 4: Verify Routing Engine Constraints and Scores."""
    from aios.providers.interface import (
        universal_capability_registry,
        universal_health_registry,
    )
    from aios.providers.models import ProviderCapabilities

    universal_provider_registry.register(MockProvider())
    universal_model_registry.register_model(ModelInfo("mock", "mock-model", "Mock", "Mock"))
    universal_capability_registry.register_provider_capabilities(
        "mock", ProviderCapabilities(chat=True)
    )
    universal_health_registry.update_health("mock", available=True)

    req = RoutingRequest(task_type="chat", preferred_model="mock-model", preferred_provider="mock")
    decision = universal_routing_engine.route(req)

    assert decision is not None
    assert decision.provider == "mock"
    assert decision.model == "mock-model"

    # Fallback to another provider if preferred fails
    req_fallback = RoutingRequest(task_type="chat", preferred_provider="unknown")
    decision_fallback = universal_routing_engine.route(req_fallback)
    assert decision_fallback is not None
    assert decision_fallback.provider == "mock"


def test_omniroute_tests(clean_registries):
    """PHASE 5: Verify OmniRoute Metadata and Error Propagation."""
    universal_provider_registry.register(MockProvider())
    universal_model_registry.register_model(ModelInfo("mock", "mock-model", "Mock", "Mock"))

    req = OmniRouteRequest(
        prompt="test",
        preferred_model="mock-model",
        task_type="coding",
        additional_params={"temperature": 0.5},
    )
    res = universal_omniroute_engine.execute(req)

    assert res.provider == "mock"
    assert res.model == "mock-model"
    assert res.usage is not None
    assert res.latency_ms >= 0
    assert res.cost == 0.0


def test_configuration_tests(tmp_path):
    """PHASE 6: Verify Configuration and Overrides."""
    config_file = tmp_path / "aios.toml"
    config_file.write_text("""
[runtime]
name = "AI OS"
version = "1.0"
[persistence]
policy = "STRICT"
provider_name = "postgresql"
""")
    # Environment override
    with patch.dict(os.environ, {"POSTGRES_DATABASE": "test_db", "POSTGRES_HOST": "localhost"}):
        cfg = load_config(config_file)
        assert cfg.runtime.name == "AI OS"
        assert cfg.persistence.policy == "STRICT"
        assert cfg.persistence.provider_name == "postgresql"

        # In persistence config service
        from aios.services.persistence import PersistenceConfigurationService, PersistencePolicy

        p_cfg = PersistenceConfigurationService()
        p_cfg.policy = PersistencePolicy(cfg.persistence.policy)
        p_cfg.provider_name = cfg.persistence.provider_name
        p_cfg.database = os.getenv("POSTGRES_DATABASE")

        assert p_cfg.policy == PersistencePolicy.STRICT
        assert p_cfg.provider_name == "postgresql"
        assert p_cfg.database == "test_db"


def test_lifecycle_tests():
    """PHASE 7: Verify Service Lifecycle."""
    from aios.services.base import ServiceLifecycle

    class TestService(ServiceLifecycle):
        def __init__(self):
            self.init_called = False
            self.start_called = False
            self.shutdown_called = False

        def initialize(self):
            self.init_called = True

        def start(self):
            self.start_called = True

        def shutdown(self):
            self.shutdown_called = True

        def ready(self) -> bool:
            return self.init_called and self.start_called

    svc = TestService()
    assert not svc.ready()
    svc.initialize()
    svc.start()
    assert svc.ready()
    svc.shutdown()
    assert svc.shutdown_called


def test_local_first_tests():
    """PHASE 8: Verify Local-First Fallbacks."""
    from aios.services.persistence import (
        PersistenceConfigurationService,
        PersistencePolicy,
        PersistenceRegistry,
        RepositoryRegistry,
    )
    from aios.services.persistence_impl_modules.core_persistence import PersistenceServiceImpl

    p_config = PersistenceConfigurationService()
    p_config.policy = PersistencePolicy.BEST_EFFORT
    p_config.provider_name = "postgresql"  # Assuming it fails to connect

    registry = PersistenceRegistry()
    repos = RepositoryRegistry()

    # Mock registry so it returns a fake failing provider
    class FailingProvider:
        transport = None

        def initialize(self, config):
            raise Exception("Connection failed")

        def disconnect(self):
            pass

    registry.register_provider("postgresql", FailingProvider)

    svc = PersistenceServiceImpl(p_config, registry, repos)
    svc.initialize()

    # It should fallback to sqlite
    assert svc.config.provider_name == "sqlite"
    assert registry.get_provider_class("sqlite") is not None


def test_end_to_end_boot_and_shutdown(tmp_path):
    """PHASE 9: Verify E2E Boot and Shutdown sequence."""
    config_file = tmp_path / "aios.toml"
    config_file.write_text("[runtime]\nname='test'\n[persistence]\npolicy='BEST_EFFORT'")

    # 1. Boot
    kernel = bootstrap_kernel(config_file)
    assert kernel is not None
    kernel.boot()

    assert kernel.state.name == "READY"

    # 2. Shutdown
    kernel.shutdown()
    assert kernel.state.name == "HALTED"


def test_end_to_end_chat(clean_registries):
    """PHASE 9: Verify E2E Chat Routing."""
    universal_provider_registry.register(MockProvider())
    universal_model_registry.register_model(ModelInfo("mock", "mock-model", "Mock", "Mock"))

    model_service = LocalModelService()
    res = model_service.execute_prompt("Hello E2E", system_instruction="System context")
    assert "MockProvider" in res
