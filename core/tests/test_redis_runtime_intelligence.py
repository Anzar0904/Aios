import pytest
from aios.registry import ServiceRegistry
from aios.services.persistence import (
    PersistenceConfigurationService,
    PersistenceRegistry,
    PersistenceService,
    RedisCapacityAnalyzer,
    RedisPerformanceAnalyzer,
    RedisProvider,
    RedisRecommendationEngine,
    RedisRuntimeAggregator,
    RedisRuntimeDiagnostics,
    RedisRuntimeHealthAnalyzer,
    RedisRuntimeIntelligenceService,
    RedisRuntimeReporter,
    RedisRuntimeStatisticsCollector,
    RedisRuntimeTelemetry,
    RedisRuntimeValidator,
    RepositoryRegistry,
    RuntimeIntelligenceService,
)
from aios.services.persistence_impl import (
    CacheDiagnosticsImpl,
    CacheHealthMonitorImpl,
    CacheRecommendationEngineImpl,
    CacheStatisticsCollectorImpl,
    CoordinationDiagnosticsImpl,
    CoordinationHealthMonitorImpl,
    CoordinationRecommendationEngineImpl,
    CoordinationStatisticsCollectorImpl,
    FakeRedisClient,
    PersistenceBootstrapper,
    PersistenceServiceImpl,
    PostgreSQLProvider,
    QueueDiagnosticsImpl,
    QueueHealthMonitorImpl,
    QueueRecommendationEngineImpl,
    QueueStatisticsCollectorImpl,
    RateLimitDiagnosticsImpl,
    RateLimitHealthMonitorImpl,
    RateLimitRecommendationEngineImpl,
    RateLimitStatisticsCollectorImpl,
    RedisCapacityAnalyzerImpl,
    RedisConfigurationService,
    RedisConnectionManager,
    RedisPerformanceAnalyzerImpl,
    RedisProviderImpl,
    RedisRecommendationEngineImpl,
    RedisRuntimeAggregatorImpl,
    RedisRuntimeDiagnosticsImpl,
    RedisRuntimeHealthAnalyzerImpl,
    RedisRuntimeIntelligenceServiceImpl,
    RedisRuntimeReporterImpl,
    RedisRuntimeStatisticsCollectorImpl,
    RedisRuntimeTelemetryImpl,
    RedisRuntimeValidatorImpl,
    RedisTransportImpl,
    SessionDiagnosticsImpl,
    SessionHealthMonitorImpl,
    SessionRecommendationEngineImpl,
    SessionStatisticsCollectorImpl,
)

from tests.test_persistence import SQLiteTransportForTests


@pytest.fixture
def intelligence_env():
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

    # 2. Setup Redis Subsystems and Mocks
    redis_cfg = RedisConfigurationService()
    redis_conn = RedisConnectionManager(redis_cfg)
    redis_transport = RedisTransportImpl(redis_cfg, redis_conn)
    redis_provider = RedisProviderImpl(redis_transport)

    # Force simulated client
    redis_conn.client = FakeRedisClient()
    redis_transport.client = redis_conn.client

    cache_stats = CacheStatisticsCollectorImpl()
    cache_health = CacheHealthMonitorImpl(redis_provider)
    cache_diag = CacheDiagnosticsImpl(redis_provider)
    cache_rec = CacheRecommendationEngineImpl(cache_stats, cache_diag)

    session_stats = SessionStatisticsCollectorImpl()
    session_health = SessionHealthMonitorImpl(redis_provider)
    session_diag = SessionDiagnosticsImpl(redis_provider)
    session_rec = SessionRecommendationEngineImpl(session_stats, session_diag)

    coord_stats = CoordinationStatisticsCollectorImpl()
    coord_health = CoordinationHealthMonitorImpl(redis_provider)
    coord_diag = CoordinationDiagnosticsImpl(redis_provider)
    coord_rec = CoordinationRecommendationEngineImpl(coord_stats, coord_diag)

    queue_stats = QueueStatisticsCollectorImpl()
    queue_health = QueueHealthMonitorImpl(redis_provider)
    queue_diag = QueueDiagnosticsImpl(redis_provider)
    queue_rec = QueueRecommendationEngineImpl(queue_stats, queue_diag)

    rate_limit_stats = RateLimitStatisticsCollectorImpl()
    rate_limit_health = RateLimitHealthMonitorImpl(redis_provider)
    rate_limit_diag = RateLimitDiagnosticsImpl(redis_provider)
    rate_limit_rec = RateLimitRecommendationEngineImpl(rate_limit_stats, rate_limit_diag)

    # Redis Runtime Intelligence instantiations
    redis_aggregator = RedisRuntimeAggregatorImpl(
        cache_stats, session_stats, coord_stats, queue_stats, rate_limit_stats, redis_conn
    )
    redis_telem = RedisRuntimeTelemetryImpl(redis_aggregator)
    redis_health_analyzer = RedisRuntimeHealthAnalyzerImpl(
        cache_health, session_health, coord_health, queue_health, rate_limit_health
    )
    redis_capacity_analyzer = RedisCapacityAnalyzerImpl(redis_aggregator)
    redis_perf_analyzer = RedisPerformanceAnalyzerImpl(redis_aggregator)
    redis_recommend_engine = RedisRecommendationEngineImpl(
        cache_rec, session_rec, coord_rec, queue_rec, rate_limit_rec
    )
    redis_diagnostics = RedisRuntimeDiagnosticsImpl(
        cache_diag, session_diag, coord_diag, queue_diag, rate_limit_diag
    )
    redis_stats_collector = RedisRuntimeStatisticsCollectorImpl(redis_aggregator)
    redis_reporter = RedisRuntimeReporterImpl(redis_aggregator)
    redis_validator = RedisRuntimeValidatorImpl()

    redis_intelligence_service = RedisRuntimeIntelligenceServiceImpl(
        redis_telem,
        redis_aggregator,
        redis_health_analyzer,
        redis_capacity_analyzer,
        redis_perf_analyzer,
        redis_recommend_engine,
        redis_diagnostics,
        redis_stats_collector,
        redis_reporter,
        redis_validator,
    )

    # Initialize all Redis Runtime Intelligence classes
    redis_aggregator.initialize()
    redis_telem.initialize()
    redis_health_analyzer.initialize()
    redis_capacity_analyzer.initialize()
    redis_perf_analyzer.initialize()
    redis_recommend_engine.initialize()
    redis_diagnostics.initialize()
    redis_stats_collector.initialize()
    redis_reporter.initialize()
    redis_validator.initialize()
    redis_intelligence_service.initialize()

    # Global Registry setup
    registry = ServiceRegistry()
    registry.register(PersistenceService, p_service)
    registry.register(RedisProvider, redis_provider)

    # Instantiate global Runtime Intelligence (Sprint 4)
    from aios.services.persistence_impl import (
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
    )

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
    ri_report = RuntimeReportGenerator(".", None)

    global_ri = RuntimeIntelligenceServiceImpl(
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
    ri_report.intelligence = global_ri
    p_service.ri_service = global_ri

    # Link global Runtime Intelligence to our telemetry
    global_ri.telemetry.redis_telemetry = redis_intelligence_service

    registry.register(RuntimeIntelligenceService, global_ri)
    registry.register(RedisRuntimeTelemetry, redis_telem)
    registry.register(RedisRuntimeAggregator, redis_aggregator)
    registry.register(RedisRuntimeHealthAnalyzer, redis_health_analyzer)
    registry.register(RedisCapacityAnalyzer, redis_capacity_analyzer)
    registry.register(RedisPerformanceAnalyzer, redis_perf_analyzer)
    registry.register(RedisRecommendationEngine, redis_recommend_engine)
    registry.register(RedisRuntimeDiagnostics, redis_diagnostics)
    registry.register(RedisRuntimeStatisticsCollector, redis_stats_collector)
    registry.register(RedisRuntimeReporter, redis_reporter)
    registry.register(RedisRuntimeValidator, redis_validator)
    registry.register(RedisRuntimeIntelligenceService, redis_intelligence_service)

    yield {
        "p_service": p_service,
        "redis_provider": redis_provider,
        "redis_aggregator": redis_aggregator,
        "redis_telem": redis_telem,
        "redis_health_analyzer": redis_health_analyzer,
        "redis_capacity_analyzer": redis_capacity_analyzer,
        "redis_perf_analyzer": redis_perf_analyzer,
        "redis_recommend_engine": redis_recommend_engine,
        "redis_diagnostics": redis_diagnostics,
        "redis_stats_collector": redis_stats_collector,
        "redis_reporter": redis_reporter,
        "redis_validator": redis_validator,
        "redis_intelligence_service": redis_intelligence_service,
        "global_ri": global_ri,
    }
    ServiceRegistry._global_registry = None


def test_telemetry_aggregation(intelligence_env):
    agg = intelligence_env["redis_aggregator"]
    metrics = agg.aggregate_metrics()
    assert "cache" in metrics
    assert "session" in metrics
    assert "coordination" in metrics
    assert "queue" in metrics
    assert "rate_limit" in metrics


def test_health_scoring_and_analysis(intelligence_env):
    analyzer = intelligence_env["redis_health_analyzer"]
    health = analyzer.analyze_health()
    assert "overall_score" in health
    assert health["overall_score"] >= 0.0
    assert "cache" in health


def test_capacity_and_performance_analysis(intelligence_env):
    cap = intelligence_env["redis_capacity_analyzer"]
    perf = intelligence_env["redis_perf_analyzer"]

    c_analysis = cap.analyze_capacity()
    assert c_analysis["capacity_score"] == 95.0
    assert c_analysis["memory_utilization"] == "optimal"

    p_analysis = perf.analyze_performance()
    assert p_analysis["performance_score"] == 98.0
    assert p_analysis["average_latency_ms"] == 0.45


def test_diagnostics_and_recommendations(intelligence_env):
    diag = intelligence_env["redis_diagnostics"]
    recommend = intelligence_env["redis_recommend_engine"]

    d_info = diag.get_diagnostics()
    assert "cache" in d_info
    assert "session" in d_info

    diag.log_error(
        "Simulated out-of-memory hazard",
        severity="CRITICAL",
        remediation="Increase maxmemory limit",
    )
    d_info_new = diag.get_diagnostics()
    assert len(d_info_new["custom_errors"]) == 1

    recs = recommend.generate_recommendations()
    assert len(recs) > 0


def test_global_runtime_intelligence_forwarding(intelligence_env):
    global_ri = intelligence_env["global_ri"]
    print("global_ri.telemetry.redis_telemetry TYPE:", type(global_ri.telemetry.redis_telemetry))

    # Retrieve unified global telemetry -> must include "redis_telemetry" section
    global_telem = global_ri.get_telemetry()
    assert "redis_telemetry" in global_telem
    assert "cache" in global_telem["redis_telemetry"]

    # Unified global health -> must include "redis_health" section
    global_health = global_ri.get_health()
    assert "redis_health" in global_health

    # Unified global diagnostics -> must include "redis_diagnostics" section
    global_diag = global_ri.get_diagnostics()
    assert "redis_diagnostics" in global_diag

    # Unified learning payload -> must include "redis_learning" trends
    global_learning = global_ri.get_learning_payload()
    assert "redis_learning" in global_learning
