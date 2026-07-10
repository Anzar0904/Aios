from pathlib import Path
from typing import Any, Iterator, List, Optional

from aios.cli import execute_builtin_cli_command
from aios.providers.adapters import MockProvider
from aios.providers.benchmark import (
    generate_reports,
    run_parallel_health_checks,
    run_provider_benchmark,
)
from aios.providers.interface import (
    AIProvider,
    AIProviderRegistry,
    CapabilityRegistry,
    ModelInfo,
    ModelRegistry,
    OmniRouteEngine,
    OmniRouteRequest,
    ProviderCost,
    ProviderCostRegistry,
    ProviderHealthRegistry,
    ProviderQuotaRegistry,
    RoutingEngine,
    RoutingRequest,
    universal_model_registry,
    universal_provider_registry,
)
from aios.providers.models import ProviderCapabilities


class FakeProvider(AIProvider):
    def __init__(self, name: str, should_fail: bool = False, fail_count: int = 0) -> None:
        self._name = name
        self.should_fail = should_fail
        self.fail_count = fail_count
        self.call_count = 0

    @property
    def name(self) -> str:
        return self._name

    def generate(
        self, model: str, prompt: str, system_prompt: Optional[str] = None, **kwargs: Any
    ) -> str:
        self.call_count += 1
        if self.should_fail:
            raise RuntimeError(f"Provider {self._name} failed")
        if self.fail_count > 0 and self.call_count <= self.fail_count:
            raise RuntimeError(f"Transient error in {self._name}")
        return f"Response from {self._name} for {prompt}"

    def stream(
        self, model: str, prompt: str, system_prompt: Optional[str] = None, **kwargs: Any
    ) -> Iterator[str]:
        yield self.generate(model, prompt, system_prompt, **kwargs)

    def embeddings(self, model: str, text: str, **kwargs: Any) -> List[float]:
        return [0.1] * 100

    def health(self) -> bool:
        return not self.should_fail

    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(chat=True, coding=True, reasoning=True)


def test_capability_registry() -> None:
    prov_reg = AIProviderRegistry()
    cap_reg = CapabilityRegistry(prov_reg)

    p = FakeProvider("test-cap")
    prov_reg.register(p)

    caps = cap_reg.get_capabilities("test-cap")
    assert caps is not None
    assert caps.chat is True
    assert caps.coding is True


def test_health_scoring() -> None:
    reg = ProviderHealthRegistry()

    # Check success
    reg.update_health_success("test-health", latency_ms=150.0)
    h = reg.get_health("test-health")
    assert h.available is True
    assert h.health_score > 90.0

    # Check failure and timeout tracking
    reg.update_health_failure("test-health", "timeout error")
    h = reg.get_health("test-health")
    assert len(h.timeout_history) == 1
    assert h.last_failure_request > 0.0


def test_routing_policies() -> None:
    prov_reg = AIProviderRegistry()
    model_reg = ModelRegistry(prov_reg)
    cap_reg = CapabilityRegistry(prov_reg)
    health_reg = ProviderHealthRegistry(prov_reg)
    cost_reg = ProviderCostRegistry(prov_reg)
    quota_reg = ProviderQuotaRegistry(prov_reg)

    p_cheap = FakeProvider("cheap")
    p_fast = FakeProvider("fast")
    p_quality = FakeProvider("quality")
    p_local = FakeProvider("local")

    prov_reg.register(p_cheap)
    prov_reg.register(p_fast)
    prov_reg.register(p_quality)
    prov_reg.register(p_local)

    # Register models
    model_reg.register_model(
        ModelInfo(provider="cheap", model_id="cheap-m", display_name="Cheap", family="Cheap")
    )
    model_reg.register_model(
        ModelInfo(provider="fast", model_id="fast-m", display_name="Fast", family="Fast")
    )
    model_reg.register_model(
        ModelInfo(
            provider="quality",
            model_id="quality-m",
            display_name="Quality",
            family="Quality",
            supports_reasoning=True,
        )
    )
    model_reg.register_model(
        ModelInfo(provider="local", model_id="local-m", display_name="Local", family="Local")
    )

    # Register capabilities
    cap_reg.register_provider_capabilities("cheap", ProviderCapabilities(chat=True))
    cap_reg.register_provider_capabilities("fast", ProviderCapabilities(chat=True))
    cap_reg.register_provider_capabilities(
        "quality", ProviderCapabilities(chat=True, reasoning=True)
    )
    cap_reg.register_provider_capabilities("local", ProviderCapabilities(chat=True))

    # Setup costs
    cost_reg.register_model_cost(
        "cheap-m",
        ProviderCost(
            input_cost_per_million_tokens=1.0,
            output_cost_per_million_tokens=1.0,
        ),
    )
    cost_reg.register_model_cost(
        "fast-m",
        ProviderCost(
            input_cost_per_million_tokens=10.0,
            output_cost_per_million_tokens=10.0,
        ),
    )
    cost_reg.register_model_cost(
        "quality-m",
        ProviderCost(
            input_cost_per_million_tokens=50.0,
            output_cost_per_million_tokens=50.0,
        ),
    )
    cost_reg.register_model_cost(
        "local-m",
        ProviderCost(
            input_cost_per_million_tokens=0.0,
            output_cost_per_million_tokens=0.0,
        ),
    )

    # Setup health / latency
    health_reg.update_health_success("cheap", latency_ms=1000.0)
    health_reg.update_health_success("fast", latency_ms=50.0)
    health_reg.update_health_success("quality", latency_ms=300.0)
    health_reg.update_health_success("local", latency_ms=150.0)

    engine = RoutingEngine(
        provider_registry=prov_reg,
        capability_registry=cap_reg,
        health_registry=health_reg,
        cost_registry=cost_reg,
        quota_registry=quota_reg,
        model_registry=model_reg,
    )

    # 1. Cost-first
    dec = engine.route(RoutingRequest(task_type="chat", routing_policy="cost-first"))
    assert dec.provider == "local"  # Cost is 0.0

    # Let's exclude local to see cheap vs fast
    dec = engine.route(
        RoutingRequest(
            task_type="chat",
            routing_policy="cost-first",
            excluded_providers=["local"],
        )
    )
    assert dec.provider == "cheap"

    # 2. Speed-first
    dec = engine.route(RoutingRequest(task_type="chat", routing_policy="speed-first"))
    assert dec.provider == "fast"

    # 3. Quality-first
    dec = engine.route(RoutingRequest(task_type="chat", routing_policy="quality-first"))
    assert dec.provider == "quality"


def test_fallback_and_retries() -> None:
    prov_reg = AIProviderRegistry()
    model_reg = ModelRegistry(prov_reg)
    cap_reg = CapabilityRegistry(prov_reg)
    health_reg = ProviderHealthRegistry(prov_reg)
    cost_reg = ProviderCostRegistry(prov_reg)
    quota_reg = ProviderQuotaRegistry(prov_reg)

    p_fail = FakeProvider("failing", should_fail=True)
    p_trans = FakeProvider("transient", fail_count=1)
    p_ok = FakeProvider("ok")

    prov_reg.register(p_fail)
    prov_reg.register(p_trans)
    prov_reg.register(p_ok)

    model_reg.register_model(
        ModelInfo(provider="failing", model_id="fail-m", display_name="Fail", family="Fail")
    )
    model_reg.register_model(
        ModelInfo(provider="transient", model_id="trans-m", display_name="Trans", family="Trans")
    )
    model_reg.register_model(
        ModelInfo(provider="ok", model_id="ok-m", display_name="Ok", family="Ok")
    )

    health_reg.update_health_success("failing", latency_ms=100.0)
    health_reg.update_health_success("transient", latency_ms=100.0)
    health_reg.update_health_success("ok", latency_ms=100.0)

    routing_engine = RoutingEngine(
        provider_registry=prov_reg,
        capability_registry=cap_reg,
        health_registry=health_reg,
        cost_registry=cost_reg,
        quota_registry=quota_reg,
        model_registry=model_reg,
    )

    omni_engine = OmniRouteEngine(
        provider_registry=prov_reg,
        capability_registry=cap_reg,
        health_registry=health_reg,
        cost_registry=cost_reg,
        quota_registry=quota_reg,
        routing_engine=routing_engine,
        model_registry=model_reg,
    )

    # Test retry on transient failure
    req = OmniRouteRequest(
        prompt="hello",
        preferred_provider="transient",
        preferred_model="trans-m",
        additional_params={"max_retries": 2},
    )
    res = omni_engine.execute(req)
    assert res.provider == "transient"
    assert p_trans.call_count == 2

    # Test fallback to ok when failing persistently
    req = OmniRouteRequest(
        prompt="hello",
        preferred_provider="failing",
        preferred_model="fail-m",
        additional_params={"max_retries": 1},
    )
    res = omni_engine.execute(req)
    assert res.provider == "ok"


def test_cli_and_report_generation(tmp_path: Path) -> None:
    if not universal_provider_registry.lookup("mock"):
        universal_provider_registry.register(MockProvider())
    if not universal_model_registry.get_model("mock-model"):
        universal_model_registry.register_model(
            ModelInfo(
                provider="mock",
                model_id="mock-model",
                display_name="Mock",
                family="Mock",
            )
        )

    # Setup some dummy analytics
    from aios.providers.benchmark import record_metric

    record_metric("mock", "mock-model", 100, 100, 0.001, 150.0, True)

    # Test parallel health run
    results = run_parallel_health_checks()
    assert len(results) > 0

    # Test benchmark run
    res = run_provider_benchmark("mock", "mock-model")
    assert res["success"] is True

    # Verify reports generated
    generate_reports()
    assert Path("docs/providers/health_report.md").is_file()
    assert Path("docs/providers/benchmark_report.md").is_file()

    # Verify CLI execution (doesn't exit)
    assert (
        execute_builtin_cli_command(["providers", "list"], exit_on_complete=False) is True
    )
    assert (
        execute_builtin_cli_command(["providers", "status"], exit_on_complete=False) is True
    )
    assert (
        execute_builtin_cli_command(["providers", "analytics"], exit_on_complete=False) is True
    )
