"""
bootstrap_modules/redis_builder.py

Constructs and registers the Redis platform:
  - Connection/Transport/Provider
  - Distributed Cache
  - Distributed Sessions
  - Distributed Lock/Coordination
  - Distributed Queue
  - Rate Limiting
  - Redis Runtime Intelligence
"""

from __future__ import annotations

import logging
import os

logger = logging.getLogger(__name__)


def build_redis_platform(registry, p_service, ri_telem):  # noqa: ANN001
    """Wire and register the full Redis platform into *registry*."""
    from aios.services.persistence import (
        CacheDiagnostics,
        CacheHealthMonitor,
        CacheInvalidationManager,
        CachePolicyManager,
        CacheRebuildService,
        CacheRecommendationEngine,
        CacheStatisticsCollector,
        CacheWarmupService,
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
        PriorityQueueManager,
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
        RetryQueueManager,
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

    # ── Redis Platform Foundation ─────────────────────────────────────────
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

    for svc in (
        redis_cfg,
        redis_conn,
        redis_transport,
        redis_provider,
        redis_telem_foundation,
        redis_stats_foundation,
        redis_diag_foundation,
        redis_health_foundation,
        redis_validator_foundation,
        redis_report_foundation,
        redis_service,
    ):
        svc.initialize()

    # ── Cache Platform ────────────────────────────────────────────────────
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

    for svc in (
        cache_policy_mgr,
        cache_stats,
        cache_diag,
        cache_health,
        cache_recommend,
        cache_inval,
        redis_cache_service,
        cache_warmup,
        cache_rebuild,
    ):
        svc.initialize()

    cache_warmup.warmup_all_background()

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

    # ── Session Platform ──────────────────────────────────────────────────
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

    for svc in (
        session_registry,
        session_stats,
        session_diag,
        session_health,
        session_recommend,
        session_store,
        session_expiration,
        session_recovery,
        session_manager,
        redis_session_service,
    ):
        svc.initialize()

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

    # ── Distributed Coordination ──────────────────────────────────────────
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

    for svc in (
        lock_registry,
        deadlock_detector,
        coord_stats,
        coord_diag,
        coord_health,
        coord_recommend,
        lock_lease_mgr,
        lock_recovery_mgr,
        mutex_mgr,
        dist_lock_mgr,
        redis_coordination_service,
    ):
        svc.initialize()

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

    # ── Queue Platform ────────────────────────────────────────────────────
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

    for svc in (
        queue_registry,
        queue_stats,
        queue_diag,
        queue_health,
        queue_recommend,
        priority_q_mgr,
        delayed_q_mgr,
        retry_q_mgr,
        queue_recovery_mgr,
        queue_worker_coordinator,
        queue_manager,
        queue_scheduler,
        redis_queue_service,
    ):
        svc.initialize()

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

    # ── Rate Limiting & Job State Machine ──────────────────────────────────
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

    for svc in (
        job_state_machine,
        quota_registry,
        token_bucket_mgr,
        sliding_window_mgr,
        fixed_window_mgr,
        quota_sync_mgr,
        rate_limit_recovery_mgr,
        rate_limit_stats,
        rate_limit_diag,
        rate_limit_health,
        rate_limit_recommend,
        rate_limit_manager,
        redis_rate_limit_service,
    ):
        svc.initialize()

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

    # ── Redis Runtime Intelligence ─────────────────────────────────────────
    redis_aggregator = RedisRuntimeAggregatorImpl(
        cache_stats, session_stats, coord_stats, queue_stats, rate_limit_stats, redis_conn
    )
    redis_telem_intel = RedisRuntimeTelemetryImpl(redis_aggregator)
    redis_health_analyzer = RedisRuntimeHealthAnalyzerImpl(
        cache_health, session_health, coord_health, queue_health, rate_limit_health
    )
    redis_capacity_analyzer = RedisCapacityAnalyzerImpl(redis_aggregator)
    redis_perf_analyzer = RedisPerformanceAnalyzerImpl(redis_aggregator)
    redis_recommend_engine = RedisRecommendationEngineImpl(
        cache_recommend, session_recommend, coord_recommend, queue_recommend, rate_limit_recommend
    )
    redis_diagnostics = RedisRuntimeDiagnosticsImpl(
        cache_diag, session_diag, coord_diag, queue_diag, rate_limit_diag
    )
    redis_stats_collector = RedisRuntimeStatisticsCollectorImpl(redis_aggregator)
    redis_reporter = RedisRuntimeReporterImpl(redis_aggregator)
    redis_validator_intel = RedisRuntimeValidatorImpl()

    redis_intelligence_service = RedisRuntimeIntelligenceServiceImpl(
        redis_telem_intel,
        redis_aggregator,
        redis_health_analyzer,
        redis_capacity_analyzer,
        redis_perf_analyzer,
        redis_recommend_engine,
        redis_diagnostics,
        redis_stats_collector,
        redis_reporter,
        redis_validator_intel,
    )

    for svc in (
        redis_aggregator,
        redis_telem_intel,
        redis_health_analyzer,
        redis_capacity_analyzer,
        redis_perf_analyzer,
        redis_recommend_engine,
        redis_diagnostics,
        redis_stats_collector,
        redis_reporter,
        redis_validator_intel,
        redis_intelligence_service,
    ):
        svc.initialize()

    ri_telem.redis_telemetry = redis_intelligence_service

    registry.register(RedisRuntimeTelemetry, redis_telem_intel)
    registry.register(RedisRuntimeAggregator, redis_aggregator)
    registry.register(RedisRuntimeHealthAnalyzer, redis_health_analyzer)
    registry.register(RedisCapacityAnalyzer, redis_capacity_analyzer)
    registry.register(RedisPerformanceAnalyzer, redis_perf_analyzer)
    registry.register(RedisRecommendationEngine, redis_recommend_engine)
    registry.register(RedisRuntimeDiagnostics, redis_diagnostics)
    registry.register(RedisRuntimeStatisticsCollector, redis_stats_collector)
    registry.register(RedisRuntimeReporter, redis_reporter)
    registry.register(RedisRuntimeValidator, redis_validator_intel)
    registry.register(RedisRuntimeIntelligenceService, redis_intelligence_service)

    return {
        "redis_provider": redis_provider,
        "cache_stats": cache_stats,
    }
