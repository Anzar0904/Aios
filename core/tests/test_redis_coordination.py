from unittest.mock import MagicMock

import pytest
from aios.registry import ServiceRegistry
from aios.services.persistence import (
    CoordinationDiagnostics,
    CoordinationHealthMonitor,
    CoordinationRecommendationEngine,
    CoordinationStatisticsCollector,
    DeadlockDetector,
    DistributedLockManager,
    LockLeaseManager,
    LockPolicy,
    LockRecoveryManager,
    LockRegistry,
    MutexManager,
    PersistenceConfigurationService,
    PersistenceRegistry,
    PersistenceService,
    RedisCoordinationService,
    RedisProvider,
    RepositoryRegistry,
)
from aios.services.persistence_impl import (
    CoordinationDiagnosticsImpl,
    CoordinationHealthMonitorImpl,
    CoordinationRecommendationEngineImpl,
    CoordinationStatisticsCollectorImpl,
    DeadlockDetectorImpl,
    DistributedLockManagerImpl,
    FakeRedisClient,
    LockLeaseManagerImpl,
    LockRecoveryManagerImpl,
    LockRegistryImpl,
    MutexManagerImpl,
    PersistenceBootstrapper,
    PersistenceServiceImpl,
    PostgreSQLProvider,
    RedisConfigurationService,
    RedisConnectionManager,
    RedisCoordinationServiceImpl,
    RedisProviderImpl,
    RedisTransportImpl,
)

from tests.test_persistence import SQLiteTransportForTests


@pytest.fixture
def coordination_env():
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

    # 2. Setup Redis Coordination Platform Mock
    redis_cfg = RedisConfigurationService()
    redis_conn = RedisConnectionManager(redis_cfg)
    redis_transport = RedisTransportImpl(redis_cfg, redis_conn)
    redis_provider = RedisProviderImpl(redis_transport)

    # Force simulated client
    redis_conn.client = FakeRedisClient()
    redis_transport.client = redis_conn.client

    lock_registry = LockRegistryImpl()
    deadlock_detector = DeadlockDetectorImpl()
    coord_stats = CoordinationStatisticsCollectorImpl()
    coord_diag = CoordinationDiagnosticsImpl(redis_provider)
    coord_health = CoordinationHealthMonitorImpl(redis_provider)
    coord_recommend = CoordinationRecommendationEngineImpl(coord_stats, coord_diag)
    lock_lease_mgr = LockLeaseManagerImpl(
        redis_provider, lock_registry, deadlock_detector, coord_stats, coord_diag
    )
    lock_recovery_mgr = LockRecoveryManagerImpl(coord_stats)
    mutex_mgr = MutexManagerImpl(lock_lease_mgr, coord_stats)
    dist_lock_mgr = DistributedLockManagerImpl(lock_lease_mgr, deadlock_detector, coord_stats)
    redis_coordination_service = RedisCoordinationServiceImpl(
        redis_provider, lock_registry, lock_lease_mgr, dist_lock_mgr
    )

    lock_registry.initialize()
    deadlock_detector.initialize()
    coord_stats.initialize()
    coord_diag.initialize()
    coord_health.initialize()
    coord_recommend.initialize()
    lock_lease_mgr.initialize()
    lock_recovery_mgr.initialize()
    mutex_mgr.initialize()
    dist_lock_mgr.initialize()
    redis_coordination_service.initialize()

    # Global Registry setup
    registry = ServiceRegistry()
    registry.register(PersistenceService, p_service)
    registry.register(RedisProvider, redis_provider)
    registry.register(LockRegistry, lock_registry)
    registry.register(DeadlockDetector, deadlock_detector)
    registry.register(CoordinationStatisticsCollector, coord_stats)
    registry.register(CoordinationDiagnostics, coord_diag)
    registry.register(CoordinationHealthMonitor, coord_health)
    registry.register(CoordinationRecommendationEngine, coord_recommend)
    registry.register(LockLeaseManager, lock_lease_mgr)
    registry.register(LockRecoveryManager, lock_recovery_mgr)
    registry.register(MutexManager, mutex_mgr)
    registry.register(DistributedLockManager, dist_lock_mgr)
    registry.register(RedisCoordinationService, redis_coordination_service)

    yield {
        "p_service": p_service,
        "redis_provider": redis_provider,
        "lock_registry": lock_registry,
        "deadlock_detector": deadlock_detector,
        "coord_stats": coord_stats,
        "coord_diag": coord_diag,
        "coord_health": coord_health,
        "coord_recommend": coord_recommend,
        "lock_lease_mgr": lock_lease_mgr,
        "lock_recovery_mgr": lock_recovery_mgr,
        "mutex_mgr": mutex_mgr,
        "dist_lock_mgr": dist_lock_mgr,
        "redis_coordination_service": redis_coordination_service,
    }
    ServiceRegistry._global_registry = None


def test_lock_ownership_registry(coordination_env):
    reg = coordination_env["lock_registry"]

    all_types = reg.get_all_types()
    assert "workspace" in all_types
    assert "workflow" in all_types
    assert "automation" in all_types
    assert "provider" in all_types
    assert "engineering" in all_types
    assert "configuration" in all_types
    assert "temporary_execution" in all_types

    cfg = reg.get_configuration("workspace")
    assert cfg["owner_service"] == "WorkspaceService"
    assert cfg["lease_duration"] == 60.0
    assert cfg["renewal_strategy"] == "heartbeat"


def test_lock_acquisition_exclusive_shared_reentrant(coordination_env):
    mgr = coordination_env["dist_lock_mgr"]
    coordination_env["lock_lease_mgr"]

    # 1. Exclusive Lock
    acquired1 = mgr.acquire("workspace", "lock-1", "owner-a", LockPolicy.EXCLUSIVE)
    assert acquired1 is True

    # Try acquiring again by different owner -> must fail
    acquired2 = mgr.acquire("workspace", "lock-1", "owner-b", LockPolicy.EXCLUSIVE, timeout=0.1)
    assert acquired2 is False

    # Release exclusive lock
    released = mgr.release("workspace", "lock-1", "owner-a")
    assert released is True

    # 2. Shared Lock
    shared1 = mgr.acquire("provider", "lock-shared", "owner-a", LockPolicy.SHARED)
    assert shared1 is True

    # Another owner should also acquire shared lock successfully
    shared2 = mgr.acquire("provider", "lock-shared", "owner-b", LockPolicy.SHARED)
    assert shared2 is True

    # Release shared lock
    mgr.release("provider", "lock-shared", "owner-a")
    mgr.release("provider", "lock-shared", "owner-b")

    # 3. Reentrant Lock
    reentrant1 = mgr.acquire("engineering", "lock-reentrant", "owner-a", LockPolicy.REENTRANT)
    assert reentrant1 is True

    reentrant2 = mgr.acquire("engineering", "lock-reentrant", "owner-a", LockPolicy.REENTRANT)
    assert reentrant2 is True  # same owner succeeds

    mgr.release("engineering", "lock-reentrant", "owner-a")
    mgr.release("engineering", "lock-reentrant", "owner-a")


def test_lease_management_and_heartbeats(coordination_env):
    mgr = coordination_env["dist_lock_mgr"]
    lease_mgr = coordination_env["lock_lease_mgr"]

    # Acquire lease
    acquired = mgr.acquire("configuration", "lock-cfg", "owner-a", LockPolicy.LEASE)
    assert acquired is True

    # Ownership verification
    assert lease_mgr.verify_ownership("configuration", "lock-cfg", "owner-a") is True
    assert lease_mgr.verify_ownership("configuration", "lock-cfg", "owner-b") is False

    # Renew lease (heartbeat)
    renewed = mgr.renew("configuration", "lock-cfg", "owner-a")
    assert renewed is True

    # Force release
    force_ok = lease_mgr.force_release("configuration", "lock-cfg")
    assert force_ok is True
    assert mgr.is_locked("configuration", "lock-cfg") is False


def test_deadlock_detection_and_recovery(coordination_env):
    deadlock = coordination_env["deadlock_detector"]
    coordination_env["dist_lock_mgr"]

    # Manually configure a cycle: Node A waits for Node B, Node B waits for Node A
    deadlock.lock_owners["workflow:lock-a"] = "owner-b"
    deadlock.lock_owners["workflow:lock-b"] = "owner-a"

    deadlock.register_wait("owner-a", "lock-a", "workflow")
    deadlock.register_wait("owner-b", "lock-b", "workflow")

    # Detect deadlock
    cycles = deadlock.detect_deadlocks()
    assert len(cycles) > 0
    cycle_nodes = cycles[0]["cycle"]
    assert "owner-a" in cycle_nodes
    assert "owner-b" in cycle_nodes

    # Recommendations
    recs = deadlock.get_deadlock_recommendations()
    assert len(recs) > 0
    assert "Deadlock cycle detected" in recs[0]["issue"]


def test_redis_outage_fallback(coordination_env):
    mgr = coordination_env["dist_lock_mgr"]
    provider = coordination_env["redis_provider"]
    lease_mgr = coordination_env["lock_lease_mgr"]

    # Simulate connection outage on low-level client
    provider.transport.execute_command = MagicMock(
        side_effect=RuntimeError("Redis connection lost")
    )

    # Operations should fallback gracefully to local locks
    acquired = mgr.acquire("workspace", "lock-outage", "owner-a", LockPolicy.EXCLUSIVE)
    assert acquired is True

    # Verification should work under outage
    assert lease_mgr.verify_ownership("workspace", "lock-outage", "owner-a") is True

    released = mgr.release("workspace", "lock-outage", "owner-a")
    assert released is True


def test_observability_and_recommendations(coordination_env):
    mgr = coordination_env["dist_lock_mgr"]
    stats = coordination_env["coord_stats"]
    diag = coordination_env["coord_diag"]
    recommend = coordination_env["coord_recommend"]

    mgr.acquire("workspace", "lock-obs", "owner-a", LockPolicy.EXCLUSIVE)
    metrics = stats.get_metrics()
    assert metrics["acquisitions"]["workspace:exclusive:True"] == 1

    diag_info = diag.get_diagnostics()
    assert diag_info["status"] in ("healthy", "degraded")

    recs = recommend.get_recommendations()
    assert len(recs) > 0
