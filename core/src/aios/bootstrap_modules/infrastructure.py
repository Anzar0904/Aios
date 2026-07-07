"""
bootstrap_modules/infrastructure.py

Constructs and registers the foundation infrastructure platforms:
- SQL Core Persistence (connection setup, diagnostic tools, and migration bootstrapping)
- Runtime Intelligence platform
- Redis Platform (transport, connection, caching, sessions, locks, queues, rate-limits,
  and redis intelligence)
- Qdrant Vector database platform (config, connection manager, transport, collection manager,
  runtime service)
"""

from __future__ import annotations

import logging
import os
from pathlib import Path

# SQL imports
# Runtime Intelligence imports
# Redis imports
# Qdrant imports
# Qdrant Runtime Intelligence imports
from aios.services.persistence import (
    CacheDiagnostics,
    CacheHealthMonitor,
    CacheInvalidationManager,
    CachePolicyManager,
    CacheRebuildService,
    CacheRecommendationEngine,
    CacheStatisticsCollector,
    CacheWarmupService,
    CollectionManager,
    CoordinationDiagnostics,
    CoordinationHealthMonitor,
    CoordinationRecommendationEngine,
    CoordinationStatisticsCollector,
    DeadlockDetector,
    DelayedQueueManager,
    DistributedLockManager,
    FixedWindowManager,
    JobStateMachine,
    LockLeaseManager,
    LockRecoveryManager,
    LockRegistry,
    MutexManager,
    PersistenceConfigurationService,
    PersistenceRegistry,
    PersistenceService,
    PriorityQueueManager,
    QdrantCapacityAnalyzer,
    QdrantDiagnosticsEngine,
    QdrantHealthAnalyzer,
    QdrantPerformanceAnalyzer,
    QdrantProvider,
    QdrantRecommendationEngine,
    QdrantRuntimeCoordinator,
    QdrantRuntimeReporter,
    QdrantRuntimeService,
    QdrantRuntimeTelemetry,
    QdrantRuntimeValidator,
    QdrantStatisticsCollector,
    QdrantTransport,
    QueueDiagnostics,
    QueueHealthMonitor,
    QueueManager,
    QueueRecommendationEngine,
    QueueRecoveryManager,
    QueueRegistry,
    QueueScheduler,
    QueueStatisticsCollector,
    QueueWorkerCoordinator,
    QuotaRegistry,
    QuotaSynchronizationManager,
    RateLimitDiagnostics,
    RateLimitHealthMonitor,
    RateLimitManager,
    RateLimitRecommendationEngine,
    RateLimitRecoveryManager,
    RateLimitStatisticsCollector,
    RedisCacheService,
    RedisCapacityAnalyzer,
    RedisCoordinationService,
    RedisPerformanceAnalyzer,
    RedisProvider,
    RedisQueueService,
    RedisRateLimitService,
    RedisRecommendationEngine,
    RedisRuntimeAggregator,
    RedisRuntimeDiagnostics,
    RedisRuntimeHealthAnalyzer,
    RedisRuntimeIntelligenceService,
    RedisRuntimeReporter,
    RedisRuntimeService,
    RedisRuntimeStatisticsCollector,
    RedisRuntimeTelemetry,
    RedisRuntimeValidator,
    RedisSessionService,
    RedisTransport,
    RepositoryRegistry,
    RetryQueueManager,
    RuntimeIntelligenceService,
    SessionDiagnostics,
    SessionExpirationManager,
    SessionHealthMonitor,
    SessionManager,
    SessionRecommendationEngine,
    SessionRecoveryManager,
    SessionRegistry,
    SessionStatisticsCollector,
    SessionStore,
    SlidingWindowManager,
    TokenBucketManager,
)
from aios.services.persistence_impl import (
    CacheDiagnosticsImpl,
    CacheHealthMonitorImpl,
    CacheInvalidationManagerImpl,
    CachePolicyManagerImpl,
    CacheRebuildServiceImpl,
    CacheRecommendationEngineImpl,
    CacheStatisticsCollectorImpl,
    CacheWarmupServiceImpl,
    CollectionManagerImpl,
    CoordinationDiagnosticsImpl,
    CoordinationHealthMonitorImpl,
    CoordinationRecommendationEngineImpl,
    CoordinationStatisticsCollectorImpl,
    DeadlockDetectorImpl,
    DelayedQueueManagerImpl,
    DistributedLockManagerImpl,
    FixedWindowManagerImpl,
    JobStateMachineImpl,
    LockLeaseManagerImpl,
    LockRecoveryManagerImpl,
    LockRegistryImpl,
    MutexManagerImpl,
    PersistenceBootstrapper,
    PersistenceDiagnostics,
    PersistenceHealthMonitor,
    PersistenceReportGenerator,
    PersistenceServiceImpl,
    PersistenceValidator,
    PostgreSQLProvider,
    PriorityQueueManagerImpl,
    QdrantCapacityAnalyzerImpl,
    QdrantConfigurationService,
    QdrantConnectionManager,
    QdrantDiagnosticsEngineImpl,
    QdrantHealthAnalyzerImpl,
    QdrantPerformanceAnalyzerImpl,
    QdrantProviderImpl,
    QdrantRecommendationEngineImpl,
    QdrantRuntimeCoordinatorImpl,
    QdrantRuntimeReporterImpl,
    QdrantRuntimeServiceImpl,
    QdrantRuntimeTelemetryImpl,
    QdrantRuntimeValidatorImpl,
    QdrantStatisticsCollectorImpl,
    QdrantTransportImpl,
    QueueDiagnosticsImpl,
    QueueHealthMonitorImpl,
    QueueManagerImpl,
    QueueRecommendationEngineImpl,
    QueueRecoveryManagerImpl,
    QueueRegistryImpl,
    QueueSchedulerImpl,
    QueueStatisticsCollectorImpl,
    QueueWorkerCoordinatorImpl,
    QuotaRegistryImpl,
    QuotaSynchronizationManagerImpl,
    RateLimitDiagnosticsImpl,
    RateLimitHealthMonitorImpl,
    RateLimitManagerImpl,
    RateLimitRecommendationEngineImpl,
    RateLimitRecoveryManagerImpl,
    RateLimitStatisticsCollectorImpl,
    RedisCacheServiceImpl,
    RedisCapacityAnalyzerImpl,
    RedisConfigurationService,
    RedisConnectionManager,
    RedisCoordinationServiceImpl,
    RedisDiagnostics,
    RedisHealthMonitor,
    RedisPerformanceAnalyzerImpl,
    RedisProviderImpl,
    RedisQueueServiceImpl,
    RedisRateLimitServiceImpl,
    RedisRecommendationEngineImpl,
    RedisReportGenerator,
    RedisRuntimeAggregatorImpl,
    RedisRuntimeDiagnosticsImpl,
    RedisRuntimeHealthAnalyzerImpl,
    RedisRuntimeIntelligenceServiceImpl,
    RedisRuntimeReporterImpl,
    RedisRuntimeServiceImpl,
    RedisRuntimeStatisticsCollectorImpl,
    RedisRuntimeTelemetryImpl,
    RedisRuntimeValidatorImpl,
    RedisSessionServiceImpl,
    RedisStatistics,
    RedisTelemetry,
    RedisTransportImpl,
    RedisValidator,
    RetryQueueManagerImpl,
    RuntimeCapacityAnalyzer,
    RuntimeDiagnosticsEngine,
    RuntimeHealthMonitor,
    RuntimeIntelligenceServiceImpl,
    RuntimeLifecycleMonitor,
    RuntimePerformanceAnalyzer,
    RuntimeQueryProfiler,
    RuntimeRecommendationEngine,
    RuntimeReportGenerator,
    RuntimeRepositoryProfiler,
    RuntimeStatisticsEngine,
    RuntimeTelemetryCollector,
    RuntimeTransactionProfiler,
    SessionDiagnosticsImpl,
    SessionExpirationManagerImpl,
    SessionHealthMonitorImpl,
    SessionManagerImpl,
    SessionRecommendationEngineImpl,
    SessionRecoveryManagerImpl,
    SessionRegistryImpl,
    SessionStatisticsCollectorImpl,
    SessionStoreImpl,
    SlidingWindowManagerImpl,
    TokenBucketManagerImpl,
)
from aios.services.persistence_impl_modules.sqlite import SQLiteProvider

logger = logging.getLogger(__name__)


def bootstrap_infrastructure(registry, config_path: Path) -> dict:  # noqa: C901, ANN001
    """Wires, initializes and registers foundation infrastructure components."""
    # ── 1. SQL PERSISTENCE FOUNDATION ──
    from aios.config import load_config

    os_config = load_config(config_path)

    p_config = PersistenceConfigurationService()
    if os_config.persistence.policy:
        from aios.services.persistence import PersistencePolicy

        p_config.policy = PersistencePolicy(os_config.persistence.policy.upper())
    if os_config.persistence.provider_name:
        p_config.provider_name = os_config.persistence.provider_name
    if os_config.persistence.host:
        p_config.host = os_config.persistence.host
    if os_config.persistence.port:
        p_config.port = os_config.persistence.port
    if os_config.persistence.database:
        p_config.database = os_config.persistence.database
    if os_config.persistence.user:
        p_config.user = os_config.persistence.user
    if os_config.persistence.password:
        p_config.password = os_config.persistence.password
    p_registry = PersistenceRegistry()
    p_repos = RepositoryRegistry()

    p_registry.register_provider("postgresql", PostgreSQLProvider)
    p_registry.register_provider("sqlite", SQLiteProvider)

    p_service = PersistenceServiceImpl(p_config, p_registry, p_repos)
    p_health = PersistenceHealthMonitor(p_service)
    p_diagnostics = PersistenceDiagnostics(p_config, p_service)
    p_validator = PersistenceValidator()
    p_report = PersistenceReportGenerator(os.getcwd(), p_health, p_diagnostics)

    p_config.initialize()
    p_registry.initialize()
    p_repos.initialize()
    p_service.initialize()
    p_health.initialize()
    p_diagnostics.initialize()
    p_validator.initialize()
    p_report.initialize()

    # Connect to database for migrations
    p_service.start()

    # Bootstrapper migrations
    bootstrapper = PersistenceBootstrapper(p_service)
    bootstrapper.initialize()
    bootstrapper.start()

    # ── 2. RUNTIME INTELLIGENCE PLATFORM ──
    ri_telem = RuntimeTelemetryCollector()
    ri_perf = RuntimePerformanceAnalyzer(ri_telem)
    ri_capacity = RuntimeCapacityAnalyzer(ri_telem)
    ri_query_prof = RuntimeQueryProfiler()
    ri_tx_prof = RuntimeTransactionProfiler()
    ri_repo_prof = RuntimeRepositoryProfiler()
    ri_lifecycle = RuntimeLifecycleMonitor()
    ri_stats = RuntimeStatisticsEngine(p_service)
    ri_diag = RuntimeDiagnosticsEngine()
    ri_recommend = RuntimeRecommendationEngine(
        ri_telem, ri_perf, ri_capacity, ri_query_prof, ri_tx_prof, ri_repo_prof
    )
    ri_health = RuntimeHealthMonitor(p_service, ri_telem)
    ri_report = RuntimeReportGenerator(os.getcwd(), None)

    ri_service = RuntimeIntelligenceServiceImpl(
        ri_health,
        ri_telem,
        ri_stats,
        ri_diag,
        ri_capacity,
        ri_recommend,
        ri_perf,
        ri_query_prof,
        ri_tx_prof,
        ri_repo_prof,
        ri_lifecycle,
        ri_report,
    )
    ri_report.intelligence = ri_service
    p_service.ri_service = ri_service

    # Initialize all Runtime Intelligence classes
    ri_telem.initialize()
    ri_perf.initialize()
    ri_capacity.initialize()
    ri_query_prof.initialize()
    ri_tx_prof.initialize()
    ri_repo_prof.initialize()
    ri_lifecycle.initialize()
    ri_stats.initialize()
    ri_diag.initialize()
    ri_recommend.initialize()
    ri_health.initialize()
    ri_report.initialize()
    ri_service.initialize()

    # Register in DI container
    registry.register(PersistenceConfigurationService, p_config)
    registry.register(PersistenceRegistry, p_registry)
    registry.register(RepositoryRegistry, p_repos)
    registry.register(PersistenceService, p_service)
    registry.register(PersistenceHealthMonitor, p_health)
    registry.register(PersistenceDiagnostics, p_diagnostics)
    registry.register(PersistenceValidator, p_validator)
    registry.register(PersistenceReportGenerator, p_report)

    registry.register(RuntimeTelemetryCollector, ri_telem)
    registry.register(RuntimePerformanceAnalyzer, ri_perf)
    registry.register(RuntimeCapacityAnalyzer, ri_capacity)
    registry.register(RuntimeQueryProfiler, ri_query_prof)
    registry.register(RuntimeTransactionProfiler, ri_tx_prof)
    registry.register(RuntimeRepositoryProfiler, ri_repo_prof)
    registry.register(RuntimeLifecycleMonitor, ri_lifecycle)
    registry.register(RuntimeStatisticsEngine, ri_stats)
    registry.register(RuntimeDiagnosticsEngine, ri_diag)
    registry.register(RuntimeRecommendationEngine, ri_recommend)
    registry.register(RuntimeHealthMonitor, ri_health)
    registry.register(RuntimeReportGenerator, ri_report)
    registry.register(RuntimeIntelligenceService, ri_service)

    # ── 3. REDIS PLATFORM FOUNDATION ──
    redis_cfg = RedisConfigurationService()
    redis_conn = RedisConnectionManager(redis_cfg)
    redis_transport = RedisTransportImpl(redis_cfg, redis_conn)
    redis_provider = RedisProviderImpl(redis_transport)
    redis_telem_foundation = RedisTelemetry()
    redis_stats_foundation = RedisStatistics(redis_telem_foundation)
    redis_diag_foundation = RedisDiagnostics(redis_conn)
    redis_health_foundation = RedisHealthMonitor(redis_transport)
    redis_validator_foundation = RedisValidator()
    redis_report_foundation = RedisReportGenerator(os.getcwd(), None)

    redis_service = RedisRuntimeServiceImpl(
        redis_cfg,
        redis_transport,
        redis_provider,
        redis_health_foundation,
        redis_diag_foundation,
        redis_telem_foundation,
        redis_stats_foundation,
        redis_validator_foundation,
        redis_report_foundation,
    )
    redis_report_foundation.runtime_service = redis_service

    # Initialize all Redis Platform classes
    redis_cfg.initialize()
    redis_conn.initialize()
    redis_transport.initialize()
    redis_provider.initialize()
    redis_telem_foundation.initialize()
    redis_stats_foundation.initialize()
    redis_diag_foundation.initialize()
    redis_health_foundation.initialize()
    redis_validator_foundation.initialize()
    redis_report_foundation.initialize()
    redis_service.initialize()

    # ── 4. RUNTIME CACHE PLATFORM ──
    cache_policy_mgr = CachePolicyManagerImpl()
    cache_stats = CacheStatisticsCollectorImpl()
    cache_diag = CacheDiagnosticsImpl(redis_provider)
    cache_health = CacheHealthMonitorImpl(redis_provider)
    cache_recommend = CacheRecommendationEngineImpl(cache_stats, cache_diag)
    cache_inval = CacheInvalidationManagerImpl(redis_provider, cache_stats)
    redis_cache_service = RedisCacheServiceImpl(
        redis_provider, cache_policy_mgr, cache_stats, cache_diag
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

    # Trigger Startup Cache Warmup in background
    cache_warmup.warmup_all_background()

    # Register in DI container
    registry.register(RedisConfigurationService, redis_cfg)
    registry.register(RedisConnectionManager, redis_conn)
    registry.register(RedisTransport, redis_transport)
    registry.register(RedisProvider, redis_provider)
    registry.register(RedisTelemetry, redis_telem_foundation)
    registry.register(RedisStatistics, redis_stats_foundation)
    registry.register(RedisDiagnostics, redis_diag_foundation)
    registry.register(RedisHealthMonitor, redis_health_foundation)
    registry.register(RedisValidator, redis_validator_foundation)
    registry.register(RedisReportGenerator, redis_report_foundation)
    registry.register(RedisRuntimeService, redis_service)

    registry.register(CachePolicyManager, cache_policy_mgr)
    registry.register(CacheStatisticsCollector, cache_stats)
    registry.register(CacheDiagnostics, cache_diag)
    registry.register(CacheHealthMonitor, cache_health)
    registry.register(CacheRecommendationEngine, cache_recommend)
    registry.register(CacheInvalidationManager, cache_inval)
    registry.register(CacheWarmupService, cache_warmup)
    registry.register(CacheRebuildService, cache_rebuild)
    registry.register(RedisCacheService, redis_cache_service)

    # ── 5. RUNTIME SESSION PLATFORM ──
    session_registry = SessionRegistryImpl()
    session_stats = SessionStatisticsCollectorImpl()
    session_diag = SessionDiagnosticsImpl(redis_provider)
    session_health = SessionHealthMonitorImpl(redis_provider)
    session_recommend = SessionRecommendationEngineImpl(session_stats, session_diag)
    session_store = SessionStoreImpl(redis_provider, session_registry, session_stats, session_diag)
    session_expiration = SessionExpirationManagerImpl(session_store, session_registry)
    session_recovery = SessionRecoveryManagerImpl(p_service, redis_provider, session_stats)
    session_manager = SessionManagerImpl(
        session_store, session_recovery, session_registry, session_stats
    )
    redis_session_service = RedisSessionServiceImpl(
        redis_provider,
        session_registry,
        session_store,
        session_manager,
        session_stats,
        session_diag,
    )

    session_registry.initialize()
    session_stats.initialize()
    session_diag.initialize()
    session_health.initialize()
    session_recommend.initialize()
    session_store.initialize()
    session_expiration.initialize()
    session_recovery.initialize()
    session_manager.initialize()
    redis_session_service.initialize()

    registry.register(SessionRegistry, session_registry)
    registry.register(SessionStatisticsCollector, session_stats)
    registry.register(SessionDiagnostics, session_diag)
    registry.register(SessionHealthMonitor, session_health)
    registry.register(SessionRecommendationEngine, session_recommend)
    registry.register(SessionStore, session_store)
    registry.register(SessionExpirationManager, session_expiration)
    registry.register(SessionRecoveryManager, session_recovery)
    registry.register(SessionManager, session_manager)
    registry.register(RedisSessionService, redis_session_service)

    # ── 6. DISTRIBUTED COORDINATION PLATFORM ──
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

    # ── 7. QUEUE PLATFORM ──
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

    # ── 8. RATE LIMITING & JOB STATE MACHINE ──
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
        rate_limit_diag,
    )
    redis_rate_limit_service = RedisRateLimitServiceImpl(
        redis_provider, quota_registry, rate_limit_manager, rate_limit_stats
    )

    job_state_machine.initialize()
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

    # ── 9. REDIS RUNTIME INTELLIGENCE ──
    redis_aggregator = RedisRuntimeAggregatorImpl(
        cache_stats, session_stats, coord_stats, queue_stats, rate_limit_stats, redis_conn
    )
    redis_telem_impl = RedisRuntimeTelemetryImpl(redis_aggregator)
    redis_health_analyzer = RedisRuntimeHealthAnalyzerImpl(
        cache_health, session_health, coord_health, queue_health, rate_limit_health
    )
    redis_capacity_analyzer = RedisCapacityAnalyzerImpl(redis_aggregator)
    redis_perf_analyzer = RedisPerformanceAnalyzerImpl(redis_aggregator)
    redis_recommend_engine = RedisRecommendationEngineImpl(
        cache_recommend,
        session_recommend,
        coord_recommend,
        queue_recommend,
        rate_limit_recommend,
    )
    redis_diagnostics = RedisRuntimeDiagnosticsImpl(
        cache_diag, session_diag, coord_diag, queue_diag, rate_limit_diag
    )
    redis_stats_collector = RedisRuntimeStatisticsCollectorImpl(redis_aggregator)
    redis_reporter = RedisRuntimeReporterImpl(redis_aggregator)
    redis_validator_impl = RedisRuntimeValidatorImpl()

    redis_intelligence_service = RedisRuntimeIntelligenceServiceImpl(
        redis_telem_impl,
        redis_aggregator,
        redis_health_analyzer,
        redis_capacity_analyzer,
        redis_perf_analyzer,
        redis_recommend_engine,
        redis_diagnostics,
        redis_stats_collector,
        redis_reporter,
        redis_validator_impl,
    )

    redis_aggregator.initialize()
    redis_telem_impl.initialize()
    redis_health_analyzer.initialize()
    redis_capacity_analyzer.initialize()
    redis_perf_analyzer.initialize()
    redis_recommend_engine.initialize()
    redis_diagnostics.initialize()
    redis_stats_collector.initialize()
    redis_reporter.initialize()
    redis_validator_impl.initialize()
    redis_intelligence_service.initialize()

    # Link Redis Runtime Intelligence into global telemetry collector
    ri_telem.redis_telemetry = redis_intelligence_service

    registry.register(RedisRuntimeTelemetry, redis_telem_impl)
    registry.register(RedisRuntimeAggregator, redis_aggregator)
    registry.register(RedisRuntimeHealthAnalyzer, redis_health_analyzer)
    registry.register(RedisCapacityAnalyzer, redis_capacity_analyzer)
    registry.register(RedisPerformanceAnalyzer, redis_perf_analyzer)
    registry.register(RedisRecommendationEngine, redis_recommend_engine)
    registry.register(RedisRuntimeDiagnostics, redis_diagnostics)
    registry.register(RedisRuntimeStatisticsCollector, redis_stats_collector)
    registry.register(RedisRuntimeReporter, redis_reporter)
    registry.register(RedisRuntimeValidator, redis_validator_impl)
    registry.register(RedisRuntimeIntelligenceService, redis_intelligence_service)

    # ── 10. QDRANT/VECTOR PLATFORM ──
    qdrant_cfg = QdrantConfigurationService()
    qdrant_conn = QdrantConnectionManager(qdrant_cfg)
    qdrant_transport = QdrantTransportImpl(qdrant_cfg, qdrant_conn)
    qdrant_provider = QdrantProviderImpl(qdrant_transport)
    col_manager = CollectionManagerImpl(qdrant_provider, qdrant_cfg)
    qdrant_service = QdrantRuntimeServiceImpl(qdrant_provider, col_manager, qdrant_cfg)

    qdrant_cfg.initialize()
    qdrant_conn.initialize()
    qdrant_transport.initialize()
    qdrant_provider.initialize()
    col_manager.initialize()
    qdrant_service.initialize()

    # Start connection manager
    qdrant_conn.start()

    registry.register(QdrantConfigurationService, qdrant_cfg)
    registry.register(QdrantConnectionManager, qdrant_conn)
    registry.register(QdrantTransport, qdrant_transport)
    registry.register(QdrantProvider, qdrant_provider)
    registry.register(CollectionManager, col_manager)
    registry.register(QdrantRuntimeService, qdrant_service)

    # ── 11. QDRANT RUNTIME INTELLIGENCE ──
    qdrant_telemetry_service = QdrantRuntimeTelemetryImpl(registry)
    qdrant_health_analyzer = QdrantHealthAnalyzerImpl(qdrant_telemetry_service)
    qdrant_capacity_analyzer = QdrantCapacityAnalyzerImpl(qdrant_telemetry_service)
    qdrant_performance_analyzer = QdrantPerformanceAnalyzerImpl(qdrant_telemetry_service)
    qdrant_diagnostics = QdrantDiagnosticsEngineImpl(qdrant_telemetry_service)
    qdrant_recommendation_engine = QdrantRecommendationEngineImpl(
        qdrant_diagnostics, qdrant_capacity_analyzer, qdrant_performance_analyzer
    )
    qdrant_stats_collector = QdrantStatisticsCollectorImpl(qdrant_telemetry_service)
    qdrant_validator = QdrantRuntimeValidatorImpl()

    qdrant_coordinator = QdrantRuntimeCoordinatorImpl(
        qdrant_telemetry_service,
        qdrant_health_analyzer,
        qdrant_capacity_analyzer,
        qdrant_performance_analyzer,
        qdrant_recommendation_engine,
        qdrant_diagnostics,
        qdrant_stats_collector,
        None,
        qdrant_validator,
    )
    qdrant_reporter = QdrantRuntimeReporterImpl(qdrant_coordinator)
    qdrant_coordinator.reporter = qdrant_reporter

    qdrant_telemetry_service.initialize()
    qdrant_telemetry_service.start()
    qdrant_health_analyzer.initialize()
    qdrant_health_analyzer.start()
    qdrant_capacity_analyzer.initialize()
    qdrant_capacity_analyzer.start()
    qdrant_performance_analyzer.initialize()
    qdrant_performance_analyzer.start()
    qdrant_diagnostics.initialize()
    qdrant_diagnostics.start()
    qdrant_recommendation_engine.initialize()
    qdrant_recommendation_engine.start()
    qdrant_stats_collector.initialize()
    qdrant_stats_collector.start()
    qdrant_reporter.initialize()
    qdrant_reporter.start()
    qdrant_validator.initialize()
    qdrant_validator.start()
    qdrant_coordinator.initialize()
    qdrant_coordinator.start()

    ri_service.qdrant_telemetry = qdrant_coordinator

    registry.register(QdrantRuntimeTelemetry, qdrant_telemetry_service)
    registry.register(QdrantHealthAnalyzer, qdrant_health_analyzer)
    registry.register(QdrantCapacityAnalyzer, qdrant_capacity_analyzer)
    registry.register(QdrantPerformanceAnalyzer, qdrant_performance_analyzer)
    registry.register(QdrantRecommendationEngine, qdrant_recommendation_engine)
    registry.register(QdrantDiagnosticsEngine, qdrant_diagnostics)
    registry.register(QdrantStatisticsCollector, qdrant_stats_collector)
    registry.register(QdrantRuntimeReporter, qdrant_reporter)
    registry.register(QdrantRuntimeValidator, qdrant_validator)
    registry.register(QdrantRuntimeCoordinator, qdrant_coordinator)

    return {
        "p_config": p_config,
        "p_registry": p_registry,
        "p_repos": p_repos,
        "p_service": p_service,
        "p_health": p_health,
        "p_diagnostics": p_diagnostics,
        "p_validator": p_validator,
        "p_report": p_report,
        "ri_service": ri_service,
        "ri_telem": ri_telem,
        "redis_provider": redis_provider,
        "redis_conn": redis_conn,
        "redis_telem": redis_telem_foundation,
        "redis_health": redis_health_foundation,
        "redis_diag": redis_diag_foundation,
        "redis_stats": redis_stats_foundation,
        "qdrant_provider": qdrant_provider,
        "col_manager": col_manager,
        "qdrant_service": qdrant_service,
    }
