import os
import time
import pytest
from typing import Dict, Any, List

from aios.services.persistence import (
    PersistenceConfigurationService,
    PersistenceRegistry,
    RepositoryRegistry,
    PersistenceService,
    PersistenceStatus,
    PersistencePolicy,
    AIProviderRepository,
    ProviderCapabilityRepository,
    ProviderHealthRepository,
    ProviderTelemetryRepository,
    ProviderStatisticsRepository,
    ProviderQuotaRepository,
    ProviderRoutingRepository,
    ProviderSessionRepository,
    ProviderCheckpointRepository,
    ProviderFailoverRepository,
    AIUsageStatisticsRepository,
    AIMemoryRepository,
    AIMemoryPersistenceService,
)

from aios.services.persistence_impl import (
    PostgreSQLProvider,
    PersistenceServiceImpl,
    PersistenceBootstrapper,
    AIProviderRepositoryImpl,
    ProviderCapabilityRepositoryImpl,
    ProviderHealthRepositoryImpl,
    ProviderTelemetryRepositoryImpl,
    ProviderStatisticsRepositoryImpl,
    ProviderQuotaRepositoryImpl,
    ProviderRoutingRepositoryImpl,
    ProviderSessionRepositoryImpl,
    ProviderCheckpointRepositoryImpl,
    ProviderFailoverRepositoryImpl,
    AIUsageStatisticsRepositoryImpl,
    AIMemoryRepositoryImpl,
    AIMemoryValidator,
    AIMemoryTelemetry,
    AIMemoryStatistics,
    AIMemoryHealthMonitor,
    AIMemoryReportGenerator,
    AIMemoryPersistenceServiceImpl,
)

from tests.test_persistence import SQLiteTransportForTests


@pytest.fixture
def ai_setup():
    config = PersistenceConfigurationService()
    registry = PersistenceRegistry()
    registry.register_provider("postgresql", PostgreSQLProvider)
    repos = RepositoryRegistry()

    # Use SQLite transport in memory for testing
    transport = SQLiteTransportForTests(config)
    provider = PostgreSQLProvider(transport=transport)

    service = PersistenceServiceImpl(config, registry, repos)
    service.active_provider = provider
    provider.initialize(config)
    provider.connect()

    # Bootstrap schemas including Level 24-35 migrations
    bootstrapper = PersistenceBootstrapper(service)
    bootstrapper.initialize()
    bootstrapper.start()

    # Repositories
    ai_provider_repo = AIProviderRepositoryImpl(service)
    ai_cap_repo = ProviderCapabilityRepositoryImpl(service)
    ai_health_repo = ProviderHealthRepositoryImpl(service)
    ai_telem_repo = ProviderTelemetryRepositoryImpl(service)
    ai_stats_repo = ProviderStatisticsRepositoryImpl(service)
    ai_quota_repo = ProviderQuotaRepositoryImpl(service)
    ai_routing_repo = ProviderRoutingRepositoryImpl(service)
    ai_session_repo = ProviderSessionRepositoryImpl(service)
    ai_chk_repo = ProviderCheckpointRepositoryImpl(service)
    ai_failover_repo = ProviderFailoverRepositoryImpl(service)
    ai_usage_repo = AIUsageStatisticsRepositoryImpl(service)
    ai_mem_repo = AIMemoryRepositoryImpl(service)

    # Register in RepositoryRegistry
    repos.register_repository("ai_providers", ai_provider_repo)
    repos.register_repository("provider_capabilities", ai_cap_repo)
    repos.register_repository("provider_health", ai_health_repo)
    repos.register_repository("provider_telemetry", ai_telem_repo)
    repos.register_repository("provider_statistics", ai_stats_repo)
    repos.register_repository("provider_quotas", ai_quota_repo)
    repos.register_repository("provider_routing", ai_routing_repo)
    repos.register_repository("provider_sessions", ai_session_repo)
    repos.register_repository("provider_checkpoints", ai_chk_repo)
    repos.register_repository("provider_failovers", ai_failover_repo)
    repos.register_repository("ai_usage_statistics", ai_usage_repo)
    repos.register_repository("ai_memory", ai_mem_repo)

    # Instantiate auxiliary services
    validator = AIMemoryValidator()
    telemetry = AIMemoryTelemetry()
    stats_compiler = AIMemoryStatistics(service)
    health_monitor = AIMemoryHealthMonitor(service, telemetry, stats_compiler)
    report_generator = AIMemoryReportGenerator(os.getcwd(), health_monitor)

    persistence_service = AIMemoryPersistenceServiceImpl(
        service,
        ai_provider_repo,
        ai_cap_repo,
        ai_health_repo,
        ai_telem_repo,
        ai_stats_repo,
        ai_quota_repo,
        ai_routing_repo,
        ai_session_repo,
        ai_chk_repo,
        ai_failover_repo,
        ai_usage_repo,
        ai_mem_repo,
        validator,
        telemetry,
        stats_compiler,
        health_monitor,
        report_generator
    )

    # Initialize all
    ai_provider_repo.initialize()
    ai_cap_repo.initialize()
    ai_health_repo.initialize()
    ai_telem_repo.initialize()
    ai_stats_repo.initialize()
    ai_quota_repo.initialize()
    ai_routing_repo.initialize()
    ai_session_repo.initialize()
    ai_chk_repo.initialize()
    ai_failover_repo.initialize()
    ai_usage_repo.initialize()
    ai_mem_repo.initialize()

    validator.initialize()
    telemetry.initialize()
    stats_compiler.initialize()
    health_monitor.initialize()
    report_generator.initialize()
    persistence_service.initialize()

    return {
        "service": service,
        "persistence_service": persistence_service,
        "ai_provider_repo": ai_provider_repo,
        "ai_mem_repo": ai_mem_repo,
        "ai_chk_repo": ai_chk_repo,
        "ai_failover_repo": ai_failover_repo,
        "validator": validator,
        "telemetry": telemetry,
        "health_monitor": health_monitor,
    }


def test_ai_provider_repo_crud(ai_setup):
    repo = ai_setup["ai_provider_repo"]
    provider_data = {
        "id": "openai_test",
        "name": "openai_test",
        "version": "1.0",
        "priority": 10,
        "status": "online",
        "context_window": 16384,
        "cost_per_million_input": 1.5,
        "cost_per_million_output": 3.0,
        "auth_type": "api_key",
        "supported_models": ["gpt-test"],
        "is_local": False
    }

    # Save
    res = repo.save(provider_data)
    assert res.status == PersistenceStatus.SUCCESS

    # Get
    res_get = repo.get("openai_test")
    assert res_get.status == PersistenceStatus.SUCCESS
    assert res_get.payload["name"] == "openai_test"
    assert res_get.payload["supported_models"] == ["gpt-test"]

    # Delete
    res_del = repo.delete("openai_test")
    assert res_del.status == PersistenceStatus.SUCCESS

    # Get empty
    if repo.service.config.policy == PersistencePolicy.STRICT:
        with pytest.raises(RuntimeError):
            repo.get("openai_test")
    else:
        res_empty = repo.get("openai_test")
        assert res_empty.status == PersistenceStatus.UNKNOWN_FAILURE


def test_ai_memory_repo_crud(ai_setup):
    repo = ai_setup["ai_mem_repo"]
    p_service = ai_setup["persistence_service"]
    memory_data = {
        "id": "mem_123",
        "key": "user_preference",
        "value": "prefers_dark_mode",
        "metadata": {"tags": ["ui"]}
    }

    # Save
    res = repo.save(memory_data)
    assert res.status == PersistenceStatus.SUCCESS

    # Get
    res_get = repo.get("mem_123")
    assert res_get.status == PersistenceStatus.SUCCESS
    assert res_get.payload["key"] == "user_preference"
    assert res_get.payload["value"] == "prefers_dark_mode"
    assert res_get.payload["metadata"] == {"tags": ["ui"]}

    # Search via Persistence Service coordinator
    search_res = p_service.search_metadata("memory", {"key": "user_preference"})
    assert search_res.status == PersistenceStatus.SUCCESS
    assert len(search_res.payload) == 1
    assert search_res.payload[0]["value"] == "prefers_dark_mode"


def test_validation_policies(ai_setup):
    p_service = ai_setup["persistence_service"]
    invalid_data = {
        "id": "invalid_provider",
        "name": "",  # Empty name is invalid
        "version": "1.0",
        "priority": 1,
        "status": "online",
        "context_window": -100,  # Invalid context window
        "cost_per_million_input": -1.0,
        "cost_per_million_output": 0.0,
        "auth_type": "none",
        "supported_models": [],
        "is_local": True
    }

    # STRICT policy should raise error
    p_service.service.config.policy = PersistencePolicy.STRICT
    with pytest.raises(RuntimeError):
        p_service.record("providers", "invalid_provider", invalid_data)

    # BEST_EFFORT policy should return failure status without raising
    p_service.service.config.policy = PersistencePolicy.BEST_EFFORT
    res = p_service.record("providers", "invalid_provider", invalid_data)
    assert res.status == PersistenceStatus.VALIDATION_FAILED


def test_checkpoint_and_failover(ai_setup):
    chk_repo = ai_setup["ai_chk_repo"]
    failover_repo = ai_setup["ai_failover_repo"]

    # Test saving checkpoints
    chk_id = "chk_test_123"
    res_chk = chk_repo.save({
        "id": chk_id,
        "task_id": "task_1",
        "provider_name": "openai",
        "context": "Prompt test context",
        "retry_count": 1,
        "timestamp": time.time()
    })
    assert res_chk.status == PersistenceStatus.SUCCESS

    # Test failover log
    res_fail = failover_repo.save({
        "id": "fail_1",
        "failed_provider": "openai",
        "target_provider": "claude_code",
        "checkpoint_id": chk_id,
        "error_message": "Rate limit exceeded",
        "timestamp": time.time()
    })
    assert res_fail.status == PersistenceStatus.SUCCESS

    # Retrieve and check
    res_get = failover_repo.get("fail_1")
    assert res_get.status == PersistenceStatus.SUCCESS
    assert res_get.payload["target_provider"] == "claude_code"
    assert res_get.payload["checkpoint_id"] == chk_id
