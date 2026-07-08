import time
import pytest
from unittest.mock import MagicMock

from aios.registry import ServiceRegistry
from aios.services.persistence import (
    PersistenceConfigurationService,
    PersistenceRegistry,
    RepositoryRegistry,
    PersistenceService,
    RedisProvider,
    JobState,
    JobStateMachine,
    QuotaRegistry,
    RateLimitManager,
    TokenBucketManager,
    SlidingWindowManager,
    FixedWindowManager,
    QuotaSynchronizationManager,
    RateLimitRecoveryManager,
    RateLimitStatisticsCollector,
    RateLimitHealthMonitor,
    RateLimitDiagnostics,
    RateLimitRecommendationEngine,
    RedisRateLimitService,
)

from aios.services.persistence_impl import (
    PostgreSQLProvider,
    PersistenceServiceImpl,
    PersistenceBootstrapper,
    RedisConfigurationService,
    RedisConnectionManager,
    RedisTransportImpl,
    RedisProviderImpl,
    FakeRedisClient,
    JobStateMachineImpl,
    QuotaRegistryImpl,
    TokenBucketManagerImpl,
    SlidingWindowManagerImpl,
    FixedWindowManagerImpl,
    QuotaSynchronizationManagerImpl,
    RateLimitRecoveryManagerImpl,
    RateLimitStatisticsCollectorImpl,
    RateLimitDiagnosticsImpl,
    RateLimitHealthMonitorImpl,
    RateLimitRecommendationEngineImpl,
    RateLimitManagerImpl,
    RedisRateLimitServiceImpl,
)

from tests.test_persistence import SQLiteTransportForTests


@pytest.fixture
def rate_limit_env():
    # 1. Setup SQLite database mock
    p_config = PersistenceConfigurationService()
    p_registry = PersistenceRegistry()
    p_registry.register_provider("postgresql", PostgreSQLProvider)
    p_repos = RepositoryRegistry()

    transport = SQLiteTransportForTests(p_config)
    provider = PostgreSQLProvider(transport=transport)

    p_service = PersistenceServiceImpl(p_config, p_registry, p_repos)
    p_service.active_provider = provider
    provider.initialize(p_config)
    provider.connect()

    bootstrapper = PersistenceBootstrapper(p_service)
    bootstrapper.initialize()
    bootstrapper.start()

    # 2. Setup Redis Rate Limiting Mock
    redis_cfg = RedisConfigurationService()
    redis_conn = RedisConnectionManager(redis_cfg)
    redis_transport = RedisTransportImpl(redis_cfg, redis_conn)
    redis_provider = RedisProviderImpl(redis_transport)

    # Force simulated client
    redis_conn.client = FakeRedisClient()
    redis_transport.client = redis_conn.client

    job_state_machine = JobStateMachineImpl(redis_provider)
    quota_registry = QuotaRegistryImpl()
    token_bucket_mgr = TokenBucketManagerImpl(redis_provider)
    sliding_window_mgr = SlidingWindowManagerImpl(redis_provider)
    fixed_window_mgr = FixedWindowManagerImpl(redis_provider)
    quota_sync_mgr = QuotaSynchronizationManagerImpl()
    rate_limit_recovery_mgr = RateLimitRecoveryManagerImpl()
    rate_limit_stats = RateLimitStatisticsCollectorImpl()
    rate_limit_diag = RateLimitDiagnosticsImpl(redis_provider)
    rate_limit_health = RateLimitHealthMonitorImpl(redis_provider)
    rate_limit_recommend = RateLimitRecommendationEngineImpl(rate_limit_stats, rate_limit_diag)
    
    rate_limit_manager = RateLimitManagerImpl(
        redis_provider,
        quota_registry,
        token_bucket_mgr,
        sliding_window_mgr,
        fixed_window_mgr,
        quota_sync_mgr,
        rate_limit_recovery_mgr,
        rate_limit_stats,
        rate_limit_diag
    )
    redis_rate_limit_service = RedisRateLimitServiceImpl(
        redis_provider,
        quota_registry,
        rate_limit_manager,
        rate_limit_stats
    )

    quota_registry.initialize()
    token_bucket_mgr.initialize()
    sliding_window_mgr.initialize()
    fixed_window_mgr.initialize()
    quota_sync_mgr.initialize()
    rate_limit_recovery_mgr.initialize()
    rate_limit_stats.initialize()
    rate_limit_diag.initialize()
    rate_limit_health.initialize()
    rate_limit_recommend.initialize()
    rate_limit_manager.initialize()
    redis_rate_limit_service.initialize()

    # Global Registry setup
    registry = ServiceRegistry()
    registry.register(PersistenceService, p_service)
    registry.register(RedisProvider, redis_provider)
    registry.register(JobStateMachine, job_state_machine)
    registry.register(QuotaRegistry, quota_registry)
    registry.register(TokenBucketManager, token_bucket_mgr)
    registry.register(SlidingWindowManager, sliding_window_mgr)
    registry.register(FixedWindowManager, fixed_window_mgr)
    registry.register(QuotaSynchronizationManager, quota_sync_mgr)
    registry.register(RateLimitRecoveryManager, rate_limit_recovery_mgr)
    registry.register(RateLimitStatisticsCollector, rate_limit_stats)
    registry.register(RateLimitDiagnostics, rate_limit_diag)
    registry.register(RateLimitHealthMonitor, rate_limit_health)
    registry.register(RateLimitRecommendationEngine, rate_limit_recommend)
    registry.register(RateLimitManager, rate_limit_manager)
    registry.register(RedisRateLimitService, redis_rate_limit_service)

    yield {
        "p_service": p_service,
        "redis_provider": redis_provider,
        "job_state_machine": job_state_machine,
        "quota_registry": quota_registry,
        "token_bucket_mgr": token_bucket_mgr,
        "sliding_window_mgr": sliding_window_mgr,
        "fixed_window_mgr": fixed_window_mgr,
        "rate_limit_stats": rate_limit_stats,
        "rate_limit_diag": rate_limit_diag,
        "rate_limit_health": rate_limit_health,
        "rate_limit_recommend": rate_limit_recommend,
        "rate_limit_manager": rate_limit_manager,
        "redis_rate_limit_service": redis_rate_limit_service,
    }
    ServiceRegistry._global_registry = None


def test_quota_registry(rate_limit_env):
    reg = rate_limit_env["quota_registry"]
    
    all_types = reg.get_all_types()
    assert "ai_provider" in all_types
    assert "workspace" in all_types
    assert "project" in all_types
    assert "automation" in all_types
    assert "workflow" in all_types
    assert "engineering" in all_types
    assert "runtime_validation" in all_types

    cfg = reg.get_configuration("ai_provider")
    assert cfg["owner_service"] == "ProviderService"
    assert cfg["algorithm"] == "token_bucket"
    assert cfg["capacity"] == 10
    assert cfg["refill_rate"] == 2.0


def test_token_bucket_limiting(rate_limit_env):
    mgr = rate_limit_env["rate_limit_manager"]
    stats = rate_limit_env["rate_limit_stats"]

    # Limit capacity is 10
    for _ in range(10):
        assert mgr.allow_request("ai_provider", "user-1") is True

    # 11th request should be throttled
    assert mgr.allow_request("ai_provider", "user-1") is False
    assert stats.throttles.get("ai_provider", 0) == 1


def test_sliding_window_limiting(rate_limit_env):
    mgr = rate_limit_env["rate_limit_manager"]

    # Limit capacity is 30 in 60s for runtime_validation
    for _ in range(30):
        assert mgr.allow_request("runtime_validation", "user-2") is True

    # 31st request throttled
    assert mgr.allow_request("runtime_validation", "user-2") is False


def test_fixed_window_limiting(rate_limit_env):
    mgr = rate_limit_env["rate_limit_manager"]

    # Limit capacity is 500 in 3600s for project
    for _ in range(10):
        assert mgr.allow_request("project", "user-3") is True


def test_job_state_machine_transitions(rate_limit_env):
    jsm = rate_limit_env["job_state_machine"]

    # Transition states
    assert jsm.transition_to("job-abc", JobState.CREATED) is True
    assert jsm.get_state("job-abc") == JobState.CREATED

    assert jsm.transition_to("job-abc", JobState.RUNNING) is True
    assert jsm.get_state("job-abc") == JobState.RUNNING

    assert jsm.transition_to("job-abc", JobState.SUCCEEDED) is True
    assert jsm.get_state("job-abc") == JobState.SUCCEEDED


def test_redis_outage_fallback(rate_limit_env):
    mgr = rate_limit_env["rate_limit_manager"]
    provider = rate_limit_env["redis_provider"]

    # Outage simulated
    provider.transport.execute_command = MagicMock(side_effect=RuntimeError("Redis connection lost"))

    # Under fallback, capacity degrades to 50% (5 for ai_provider)
    for _ in range(5):
        assert mgr.allow_request("ai_provider", "user-fallback") is True

    # 6th request is throttled
    assert mgr.allow_request("ai_provider", "user-fallback") is False


def test_observability_and_recommendations(rate_limit_env):
    mgr = rate_limit_env["rate_limit_manager"]
    stats = rate_limit_env["rate_limit_stats"]
    diag = rate_limit_env["rate_limit_diag"]
    recommend = rate_limit_env["rate_limit_recommend"]

    mgr.allow_request("workflow", "user-obs")

    metrics = stats.get_metrics()
    assert metrics["requests"]["workflow:allowed"] == 1

    diag_info = diag.get_diagnostics()
    assert diag_info["status"] in ("healthy", "degraded")

    recs = recommend.get_recommendations()
    assert len(recs) > 0
