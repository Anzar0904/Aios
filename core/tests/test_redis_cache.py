import os
import time
import pytest
from typing import Dict, Any, List
from unittest.mock import MagicMock

from aios.registry import ServiceRegistry
from aios.services.persistence import (
    PersistenceConfigurationService,
    PersistenceRegistry,
    RepositoryRegistry,
    PersistenceService,
    WorkspaceRepository,
    EngineeringProfileRepository,
    ConfigurationRepository,
    PersistenceStatus,
    CachePolicy,
    CachePolicyManager,
    CacheInvalidationManager,
    CacheWarmupService,
    CacheRebuildService,
    CacheStatisticsCollector,
    CacheHealthMonitor,
    CacheDiagnostics,
    CacheRecommendationEngine,
    RedisCacheService,
    RedisProvider,
)

from aios.services.persistence_impl import (
    PostgreSQLProvider,
    PersistenceServiceImpl,
    WorkspaceRepositoryImpl,
    EngineeringProfileRepositoryImpl,
    ConfigurationRepositoryImpl,
    PersistenceBootstrapper,
    RedisConfigurationService,
    RedisConnectionManager,
    RedisTransportImpl,
    RedisProviderImpl,
    RedisTelemetry,
    RedisStatistics,
    RedisDiagnostics,
    RedisHealthMonitor,
    RedisValidator,
    RedisReportGenerator,
    RedisRuntimeServiceImpl,
    FakeRedisClient,
    CachePolicyManagerImpl,
    CacheStatisticsCollectorImpl,
    CacheDiagnosticsImpl,
    CacheHealthMonitorImpl,
    CacheRecommendationEngineImpl,
    CacheInvalidationManagerImpl,
    CacheWarmupServiceImpl,
    CacheRebuildServiceImpl,
    RedisCacheServiceImpl,
)

from tests.test_persistence import SQLiteTransportForTests


@pytest.fixture
def test_env():
    # 1. Setup PostgreSQL/SQLite Mock
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
    bootstrapper.on_ready()

    # Repositories
    workspace_repo = WorkspaceRepositoryImpl(p_service)
    profile_repo = EngineeringProfileRepositoryImpl(p_service)
    config_repo = ConfigurationRepositoryImpl(p_service)

    p_repos.register_repository("workspaces", workspace_repo)
    p_repos.register_repository("engineering_profiles", profile_repo)
    p_repos.register_repository("configuration_profiles", config_repo)

    # 2. Setup Redis cache mock
    redis_cfg = RedisConfigurationService()
    redis_conn = RedisConnectionManager(redis_cfg)
    redis_transport = RedisTransportImpl(redis_cfg, redis_conn)
    redis_provider = RedisProviderImpl(redis_transport)

    # Force simulated client
    redis_conn.client = FakeRedisClient()
    redis_transport.client = redis_conn.client

    cache_policy_mgr = CachePolicyManagerImpl()
    cache_stats = CacheStatisticsCollectorImpl()
    cache_diag = CacheDiagnosticsImpl(redis_provider)
    cache_health = CacheHealthMonitorImpl(redis_provider)
    cache_recommend = CacheRecommendationEngineImpl(cache_stats, cache_diag)
    cache_inval = CacheInvalidationManagerImpl(redis_provider, cache_stats)
    redis_cache_service = RedisCacheServiceImpl(
        redis_provider,
        cache_policy_mgr,
        cache_stats,
        cache_diag
    )
    cache_warmup = CacheWarmupServiceImpl(p_service, redis_cache_service, cache_stats)
    cache_rebuild = CacheRebuildServiceImpl(p_service, redis_provider, cache_stats, cache_warmup)

    cache_policy_mgr.initialize()
    cache_stats.initialize()
    cache_diag.initialize()
    cache_health.initialize()
    cache_recommend.initialize()
    cache_inval.initialize()
    redis_cache_service.initialize()
    cache_warmup.initialize()
    cache_rebuild.initialize()

    # Register in Global Registry
    registry = ServiceRegistry()
    registry.register(PersistenceService, p_service)
    registry.register(RedisProvider, redis_provider)
    registry.register(CachePolicyManager, cache_policy_mgr)
    registry.register(CacheStatisticsCollector, cache_stats)
    registry.register(CacheDiagnostics, cache_diag)
    registry.register(CacheHealthMonitor, cache_health)
    registry.register(CacheRecommendationEngine, cache_recommend)
    registry.register(CacheInvalidationManager, cache_inval)
    registry.register(CacheWarmupService, cache_warmup)
    registry.register(CacheRebuildService, cache_rebuild)
    registry.register(RedisCacheService, redis_cache_service)

    # Cache policies default to READ_THROUGH
    cache_policy_mgr.set_policy("workspace", CachePolicy.READ_THROUGH)
    cache_policy_mgr.set_policy("profile", CachePolicy.READ_THROUGH)
    cache_policy_mgr.set_policy("configuration", CachePolicy.READ_THROUGH)

    yield {
        "p_service": p_service,
        "workspace_repo": workspace_repo,
        "profile_repo": profile_repo,
        "config_repo": config_repo,
        "redis_provider": redis_provider,
        "cache_policy_mgr": cache_policy_mgr,
        "cache_stats": cache_stats,
        "cache_diag": cache_diag,
        "cache_health": cache_health,
        "cache_recommend": cache_recommend,
        "cache_inval": cache_inval,
        "redis_cache_service": redis_cache_service,
        "cache_warmup": cache_warmup,
        "cache_rebuild": cache_rebuild,
    }
    ServiceRegistry._global_registry = None



def test_cache_policy_and_read_through(test_env):
    workspace_repo = test_env["workspace_repo"]
    cache_stats = test_env["cache_stats"]
    cache_policy_mgr = test_env["cache_policy_mgr"]

    # Explicit policy
    cache_policy_mgr.set_policy("workspace", CachePolicy.READ_THROUGH)

    ws = {
        "id": "ws-1",
        "name": "Test Workspace",
        "metadata": {"tags": ["test"]},
        "state": "active",
        "created_at": time.time(),
        "last_accessed": time.time(),
        "version": 1,
        "status": "active",
        "health": "good"
    }

    # Save to PostgreSQL
    workspace_repo.save(ws)

    # Reset cache metrics to isolate read test
    cache_stats.hits = 0
    cache_stats.misses = 0

    # First get -> Should miss cache and load from PostgreSQL, populating the cache
    res1 = workspace_repo.get("ws-1")
    assert res1 is not None
    assert res1["name"] == "Test Workspace"
    assert cache_stats.misses == 1
    assert cache_stats.hits == 0

    # Second get -> Should hit cache directly
    res2 = workspace_repo.get("ws-1")
    assert res2 is not None
    assert res2["name"] == "Test Workspace"
    assert cache_stats.misses == 1
    assert cache_stats.hits == 1


def test_cache_policy_write_through(test_env):
    workspace_repo = test_env["workspace_repo"]
    cache_stats = test_env["cache_stats"]
    cache_policy_mgr = test_env["cache_policy_mgr"]
    redis_cache_service = test_env["redis_cache_service"]

    # Explicit Write-Through Policy
    cache_policy_mgr.set_policy("workspace", CachePolicy.WRITE_THROUGH)

    ws = {
        "id": "ws-write-through",
        "name": "Write-Through Workspace",
        "metadata": {},
        "state": "active",
        "created_at": time.time(),
        "last_accessed": time.time(),
        "version": 1,
        "status": "active",
        "health": "good"
    }

    cache_stats.hits = 0
    cache_stats.misses = 0

    # Save -> Updates PostgreSQL AND immediately updates Cache
    workspace_repo.save(ws)

    # Read -> Should hit cache immediately because of Write-Through population
    res = workspace_repo.get("ws-write-through")
    assert res is not None
    assert res["name"] == "Write-Through Workspace"
    assert cache_stats.hits == 1
    assert cache_stats.misses == 0


def test_cache_policy_cache_aside(test_env):
    workspace_repo = test_env["workspace_repo"]
    cache_stats = test_env["cache_stats"]
    cache_policy_mgr = test_env["cache_policy_mgr"]

    # Explicit Cache-Aside Policy
    cache_policy_mgr.set_policy("workspace", CachePolicy.CACHE_ASIDE)

    ws = {
        "id": "ws-aside",
        "name": "Cache Aside Workspace",
        "metadata": {},
        "state": "active",
        "created_at": time.time(),
        "last_accessed": time.time(),
        "version": 1,
        "status": "active",
        "health": "good"
    }

    workspace_repo.save(ws)

    cache_stats.hits = 0
    cache_stats.misses = 0

    # First get -> cache miss, lazy load, populates cache
    res1 = workspace_repo.get("ws-aside")
    assert res1 is not None
    assert cache_stats.misses == 1
    assert cache_stats.hits == 0

    # Second get -> cache hit
    res2 = workspace_repo.get("ws-aside")
    assert res2 is not None
    assert cache_stats.hits == 1

    # Save updates under Cache-Aside -> invalidates cache key
    ws["name"] = "Updated Cache Aside Workspace"
    workspace_repo.save(ws)

    # Third get -> should miss cache and fetch new value from database
    cache_stats.hits = 0
    cache_stats.misses = 0
    res3 = workspace_repo.get("ws-aside")
    assert res3 is not None
    assert res3["name"] == "Updated Cache Aside Workspace"
    assert cache_stats.misses == 1
    assert cache_stats.hits == 0


def test_ttl_expiration(test_env):
    redis_provider = test_env["redis_provider"]
    redis_cache_service = test_env["redis_cache_service"]

    redis_cache_service.set("workspace", "temp-ws", {"val": "hello"}, ttl=1)
    
    # Check exists
    assert redis_provider.exists(redis_cache_service.make_key("workspace", "temp-ws")) is True

    # Wait for expiration
    time.sleep(1.1)

    # Should be expired
    assert redis_provider.get(redis_cache_service.make_key("workspace", "temp-ws")) is None


def test_cache_invalidation_manager(test_env):
    workspace_repo = test_env["workspace_repo"]
    cache_inval = test_env["cache_inval"]
    redis_cache_service = test_env["redis_cache_service"]

    redis_cache_service.set("workspace", "ws-1", {"name": "ws1"})
    redis_cache_service.set("workspace", "ws-2", {"name": "ws2"})

    # Invalidate one entity
    cache_inval.invalidate_entity("workspace", "ws-1")
    assert redis_cache_service.get("workspace", "ws-1", lambda: None) is None
    assert redis_cache_service.get("workspace", "ws-2", lambda: {"name": "ws2"})["name"] == "ws2"

    # Bulk invalidation
    redis_cache_service.set("workspace", "ws-1", {"name": "ws1"})
    key1 = redis_cache_service.make_key("workspace", "ws-1")
    key2 = redis_cache_service.make_key("workspace", "ws-2")
    
    deleted_count = cache_inval.invalidate_bulk([key1, key2])
    assert deleted_count == 2
    assert redis_cache_service.get("workspace", "ws-1", lambda: None) is None
    assert redis_cache_service.get("workspace", "ws-2", lambda: None) is None


def test_cache_warmup_service(test_env):
    workspace_repo = test_env["workspace_repo"]
    cache_warmup = test_env["cache_warmup"]
    redis_cache_service = test_env["redis_cache_service"]

    ws = {
        "id": "ws-warmup",
        "name": "Warmup Workspace",
        "metadata": {},
        "state": "active",
        "created_at": time.time(),
        "last_accessed": time.time(),
        "version": 1,
        "status": "active",
        "health": "good"
    }
    workspace_repo.save(ws)

    # Warm up subsystem
    cache_warmup.warm_subsystem("workspace")

    # Read -> Should hit cache immediately
    test_env["cache_stats"].hits = 0
    res = redis_cache_service.get("workspace", "ws-warmup", lambda: None)
    assert res is not None
    assert res["name"] == "Warmup Workspace"
    assert test_env["cache_stats"].hits == 1


def test_cache_rebuild_service(test_env):
    workspace_repo = test_env["workspace_repo"]
    cache_rebuild = test_env["cache_rebuild"]
    redis_cache_service = test_env["redis_cache_service"]
    redis_provider = test_env["redis_provider"]

    ws = {
        "id": "ws-rebuild",
        "name": "Rebuild Workspace",
        "metadata": {},
        "state": "active",
        "created_at": time.time(),
        "last_accessed": time.time(),
        "version": 1,
        "status": "active",
        "health": "good"
    }
    workspace_repo.save(ws)

    # Simulate connection drop
    redis_cache_service._disabled = True
    workspace_repo.save(ws) # Save with cache disabled

    # Reconnect and rebuild
    redis_cache_service._disabled = False
    rebuilt = cache_rebuild.rebuild_incremental()
    assert rebuilt > 0

    # Should hit cache now
    test_env["cache_stats"].hits = 0
    res = redis_cache_service.get("workspace", "ws-rebuild", lambda: None)
    assert res is not None
    assert res["name"] == "Rebuild Workspace"
    assert test_env["cache_stats"].hits == 1


def test_redis_unavailable_fallback(test_env):
    workspace_repo = test_env["workspace_repo"]
    redis_cache_service = test_env["redis_cache_service"]
    redis_provider = test_env["redis_provider"]

    ws = {
        "id": "ws-fallback",
        "name": "Fallback Workspace",
        "metadata": {},
        "state": "active",
        "created_at": time.time(),
        "last_accessed": time.time(),
        "version": 1,
        "status": "active",
        "health": "good"
    }
    workspace_repo.save(ws)

    # Mock low level Redis transport to raise an exception on set/get
    redis_provider.transport.execute_command = MagicMock(side_effect=RuntimeError("Redis is down"))

    # Operations should still succeed by falling back to PostgreSQL directly
    res = workspace_repo.get("ws-fallback")
    assert res is not None
    assert res["name"] == "Fallback Workspace"

    ws["name"] = "Fallback Workspace Updated"
    save_res = workspace_repo.save(ws)
    assert save_res.status == PersistenceStatus.SUCCESS

    res_updated = workspace_repo.get("ws-fallback")
    assert res_updated["name"] == "Fallback Workspace Updated"


def test_statistics_diagnostics_and_recommendations(test_env):
    redis_cache_service = test_env["redis_cache_service"]
    cache_stats = test_env["cache_stats"]
    cache_diag = test_env["cache_diag"]
    cache_recommend = test_env["cache_recommend"]

    # Trigger hits/misses
    redis_cache_service.get("workspace", "test-stats-id", lambda: {"val": 1})
    redis_cache_service.get("workspace", "test-stats-id", lambda: {"val": 1})

    # Stats check
    metrics = cache_stats.get_metrics()
    assert metrics["cache_hits"] == 1
    assert metrics["cache_misses"] == 1
    assert metrics["hit_ratio"] == 0.5

    # Diagnostics check
    diag = cache_diag.get_diagnostics()
    assert diag["status"] in ("healthy", "degraded")

    # Recommendations check
    recs = cache_recommend.get_recommendations()
    assert len(recs) > 0
    assert any(r["category"] in ("Connectivity", "Efficiency", "TTL Configuration", "Maintenance") for r in recs)


def test_backward_compatibility(test_env):
    workspace_repo = test_env["workspace_repo"]
    cache_policy_mgr = test_env["cache_policy_mgr"]
    cache_stats = test_env["cache_stats"]

    # Set policy to NO_CACHE
    cache_policy_mgr.set_policy("workspace", CachePolicy.NO_CACHE)

    ws = {
        "id": "ws-no-cache",
        "name": "No Cache Workspace",
        "metadata": {},
        "state": "active",
        "created_at": time.time(),
        "last_accessed": time.time(),
        "version": 1,
        "status": "active",
        "health": "good"
    }
    workspace_repo.save(ws)

    cache_stats.hits = 0
    cache_stats.misses = 0

    # Fetch -> Should bypass cache entirely (hits=0, misses=0)
    res = workspace_repo.get("ws-no-cache")
    assert res is not None
    assert cache_stats.hits == 0
    assert cache_stats.misses == 0
