from unittest.mock import MagicMock

import pytest
from aios.registry import ServiceRegistry
from aios.services.persistence import (
    DelayedQueueManager,
    PersistenceConfigurationService,
    PersistenceRegistry,
    PersistenceService,
    PriorityQueueManager,
    QueueDiagnostics,
    QueueHealthMonitor,
    QueueManager,
    QueuePriority,
    QueueRecommendationEngine,
    QueueRecoveryManager,
    QueueRegistry,
    QueueScheduler,
    QueueStatisticsCollector,
    QueueWorkerCoordinator,
    RedisProvider,
    RedisQueueService,
    RepositoryRegistry,
    RetryQueueManager,
)
from aios.services.persistence_impl import (
    DelayedQueueManagerImpl,
    FakeRedisClient,
    PersistenceBootstrapper,
    PersistenceServiceImpl,
    PostgreSQLProvider,
    PriorityQueueManagerImpl,
    QueueDiagnosticsImpl,
    QueueHealthMonitorImpl,
    QueueManagerImpl,
    QueueRecommendationEngineImpl,
    QueueRecoveryManagerImpl,
    QueueRegistryImpl,
    QueueSchedulerImpl,
    QueueStatisticsCollectorImpl,
    QueueWorkerCoordinatorImpl,
    RedisConfigurationService,
    RedisConnectionManager,
    RedisProviderImpl,
    RedisQueueServiceImpl,
    RedisTransportImpl,
    RetryQueueManagerImpl,
)

from tests.test_persistence import SQLiteTransportForTests


@pytest.fixture
def queue_env():
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

    # 2. Setup Redis Queue Platform Mock
    redis_cfg = RedisConfigurationService()
    redis_conn = RedisConnectionManager(redis_cfg)
    redis_transport = RedisTransportImpl(redis_cfg, redis_conn)
    redis_provider = RedisProviderImpl(redis_transport)

    # Force simulated client
    redis_conn.client = FakeRedisClient()
    redis_transport.client = redis_conn.client

    queue_registry = QueueRegistryImpl()
    queue_stats = QueueStatisticsCollectorImpl()
    queue_diag = QueueDiagnosticsImpl(redis_provider)
    queue_health = QueueHealthMonitorImpl(redis_provider)
    queue_recommend = QueueRecommendationEngineImpl(queue_stats, queue_diag)
    priority_q_mgr = PriorityQueueManagerImpl()
    delayed_q_mgr = DelayedQueueManagerImpl()
    retry_q_mgr = RetryQueueManagerImpl(queue_registry, queue_stats)
    queue_recovery_mgr = QueueRecoveryManagerImpl(queue_stats)
    queue_worker_coordinator = QueueWorkerCoordinatorImpl()

    queue_manager = QueueManagerImpl(
        redis_provider,
        queue_registry,
        priority_q_mgr,
        delayed_q_mgr,
        retry_q_mgr,
        queue_stats,
        queue_diag,
    )
    queue_scheduler = QueueSchedulerImpl(queue_manager)
    redis_queue_service = RedisQueueServiceImpl(
        redis_provider, queue_registry, queue_manager, queue_stats
    )

    queue_registry.initialize()
    queue_stats.initialize()
    queue_diag.initialize()
    queue_health.initialize()
    queue_recommend.initialize()
    priority_q_mgr.initialize()
    delayed_q_mgr.initialize()
    retry_q_mgr.initialize()
    queue_recovery_mgr.initialize()
    queue_worker_coordinator.initialize()
    queue_manager.initialize()
    queue_scheduler.initialize()
    redis_queue_service.initialize()

    # Global Registry setup
    registry = ServiceRegistry()
    registry.register(PersistenceService, p_service)
    registry.register(RedisProvider, redis_provider)
    registry.register(QueueRegistry, queue_registry)
    registry.register(QueueStatisticsCollector, queue_stats)
    registry.register(QueueDiagnostics, queue_diag)
    registry.register(QueueHealthMonitor, queue_health)
    registry.register(QueueRecommendationEngine, queue_recommend)
    registry.register(PriorityQueueManager, priority_q_mgr)
    registry.register(DelayedQueueManager, delayed_q_mgr)
    registry.register(RetryQueueManager, retry_q_mgr)
    registry.register(QueueRecoveryManager, queue_recovery_mgr)
    registry.register(QueueWorkerCoordinator, queue_worker_coordinator)
    registry.register(QueueManager, queue_manager)
    registry.register(QueueScheduler, queue_scheduler)
    registry.register(RedisQueueService, redis_queue_service)

    yield {
        "p_service": p_service,
        "redis_provider": redis_provider,
        "queue_registry": queue_registry,
        "queue_stats": queue_stats,
        "queue_diag": queue_diag,
        "queue_health": queue_health,
        "queue_recommend": queue_recommend,
        "priority_q_mgr": priority_q_mgr,
        "delayed_q_mgr": delayed_q_mgr,
        "retry_q_mgr": retry_q_mgr,
        "queue_recovery_mgr": queue_recovery_mgr,
        "queue_worker_coordinator": queue_worker_coordinator,
        "queue_manager": queue_manager,
        "queue_scheduler": queue_scheduler,
        "redis_queue_service": redis_queue_service,
    }
    ServiceRegistry._global_registry = None


def test_queue_ownership_registry(queue_env):
    reg = queue_env["queue_registry"]

    all_types = reg.get_all_types()
    assert "engineering" in all_types
    assert "automation" in all_types
    assert "workflow" in all_types
    assert "ai_provider" in all_types
    assert "workspace" in all_types
    assert "background_maintenance" in all_types
    assert "runtime_validation" in all_types

    cfg = reg.get_configuration("ai_provider")
    assert cfg["owner_service"] == "ProviderService"
    assert cfg["priority"] == QueuePriority.CRITICAL
    assert cfg["visibility_timeout"] == 10.0
    assert cfg["dlq_name"] == "ai_dlq"


def test_enqueue_dequeue_and_acknowledgement(queue_env):
    mgr = queue_env["queue_manager"]
    stats = queue_env["queue_stats"]

    # Enqueue job
    enqueued = mgr.enqueue("workflow", "job-1", {"data": "workflow_run"})
    assert enqueued is True
    assert stats.enqueues.get("workflow:NORMAL", 0) == 1

    # Dequeue job
    job = mgr.dequeue("workflow", "worker-1")
    assert job is not None
    assert job["job_id"] == "job-1"
    assert job["status"] == "processing"
    assert job["worker_id"] == "worker-1"

    # Heartbeat updates visibility timeout
    hb = mgr.heartbeat("workflow", "job-1", "worker-1")
    assert hb is True

    # Acknowledge completion -> cancels/deletes the job
    acked = mgr.acknowledge("workflow", "job-1", "worker-1")
    assert acked is True
    assert stats.acks.get("workflow", 0) == 1

    # Next dequeue should find nothing
    job_empty = mgr.dequeue("workflow", "worker-1")
    assert job_empty is None


def test_priority_ordering(queue_env):
    mgr = queue_env["queue_manager"]

    # Enqueue multiple jobs with different priorities
    mgr.enqueue("engineering", "job-low", {"desc": "low"}, priority=QueuePriority.LOW)
    mgr.enqueue(
        "engineering", "job-critical", {"desc": "critical"}, priority=QueuePriority.CRITICAL
    )
    mgr.enqueue("engineering", "job-high", {"desc": "high"}, priority=QueuePriority.HIGH)

    # Dequeue -> should retrieve highest priority first (job-critical)
    job1 = mgr.dequeue("engineering", "worker-1")
    assert job1["job_id"] == "job-critical"

    job2 = mgr.dequeue("engineering", "worker-1")
    assert job2["job_id"] == "job-high"

    job3 = mgr.dequeue("engineering", "worker-1")
    assert job3["job_id"] == "job-low"


def test_delayed_jobs(queue_env):
    mgr = queue_env["queue_manager"]

    # Enqueue a job delayed by 100 seconds
    mgr.enqueue("workspace", "job-delayed", {"val": "delayed"}, delay=100.0)

    # Dequeue immediately -> should not find the job
    job = mgr.dequeue("workspace", "worker-1")
    assert job is None

    # Enqueue with 0 delay
    mgr.enqueue("workspace", "job-immediate", {"val": "now"}, delay=0.0)

    # Dequeue -> should find job-immediate
    job_now = mgr.dequeue("workspace", "worker-1")
    assert job_now["job_id"] == "job-immediate"


def test_retry_and_dead_letter_queue(queue_env):
    mgr = queue_env["queue_manager"]
    retry_q = queue_env["retry_q_mgr"]
    stats = queue_env["queue_stats"]

    mgr.enqueue("engineering", "job-retry", {"job": "data"})

    # Simulates job dequeue
    job = mgr.dequeue("engineering", "worker-1")
    assert job is not None

    # Dequeue worker signals execution failure -> triggers retry strategy
    # "engineering" config retry policy: max_retries=3
    should_retry = retry_q.handle_failure(job, "Connection timeout error")
    assert should_retry is True
    assert job["retry_count"] == 1
    assert job["status"] == "pending"

    # Accumulate failures to exceed limit
    retry_q.handle_failure(job, "Connection timeout error")
    retry_q.handle_failure(job, "Connection timeout error")

    # Exceed limit
    should_retry_last = retry_q.handle_failure(job, "Connection timeout error")
    assert should_retry_last is False
    assert job["status"] == "dlq"
    assert stats.dlqs.get("engineering", 0) == 1


def test_pause_resume_and_purge(queue_env):
    mgr = queue_env["queue_manager"]

    mgr.enqueue("automation", "job-auto", {"act": "run"})
    mgr.pause("automation")

    # Dequeue when paused -> should return None
    job_paused = mgr.dequeue("automation", "worker-1")
    assert job_paused is None

    # Resume and dequeue -> succeeds
    mgr.resume("automation")
    job_resumed = mgr.dequeue("automation", "worker-1")
    assert job_resumed["job_id"] == "job-auto"

    # Purge queue
    mgr.enqueue("automation", "job-purge", {"act": "purge"})
    mgr.purge("automation")
    assert mgr.peek("automation") is None


def test_redis_outage_fallback(queue_env):
    mgr = queue_env["queue_manager"]
    provider = queue_env["redis_provider"]

    # Outage simulated
    provider.transport.execute_command = MagicMock(
        side_effect=RuntimeError("Redis connection lost")
    )

    # Enqueue succeeds under fallback
    enqueued = mgr.enqueue("workflow", "job-fallback", {"info": "outage"})
    assert enqueued is True

    # Dequeue succeeds under fallback
    job = mgr.dequeue("workflow", "worker-1")
    assert job is not None
    assert job["job_id"] == "job-fallback"


def test_observability_and_recommendations(queue_env):
    mgr = queue_env["queue_manager"]
    stats = queue_env["queue_stats"]
    diag = queue_env["queue_diag"]
    recommend = queue_env["queue_recommend"]

    mgr.enqueue("workflow", "job-obs", {"data": "test"})
    mgr.dequeue("workflow", "worker-1")

    metrics = stats.get_metrics()
    assert metrics["enqueues"]["workflow:NORMAL"] == 1

    diag_info = diag.get_diagnostics()
    assert diag_info["status"] in ("healthy", "degraded")

    recs = recommend.get_recommendations()
    assert len(recs) > 0
