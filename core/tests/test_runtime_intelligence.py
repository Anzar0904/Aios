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
    RuntimeIntelligenceService,
)

from aios.services.persistence_impl import (
    PostgreSQLProvider,
    PersistenceServiceImpl,
    PersistenceBootstrapper,
    RuntimeIntelligenceServiceImpl,
    RuntimeHealthMonitor,
    RuntimeTelemetryCollector,
    RuntimeStatisticsEngine,
    RuntimeDiagnosticsEngine,
    RuntimeCapacityAnalyzer,
    RuntimeRecommendationEngine,
    RuntimePerformanceAnalyzer,
    RuntimeQueryProfiler,
    RuntimeTransactionProfiler,
    RuntimeRepositoryProfiler,
    RuntimeLifecycleMonitor,
    RuntimeCorrelationManager,
    RuntimeReportGenerator,
)

from tests.test_persistence import SQLiteTransportForTests


@pytest.fixture
def ri_setup():
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

    # Bootstrap schemas
    bootstrapper = PersistenceBootstrapper(service)
    bootstrapper.initialize()
    bootstrapper.on_ready()

    # Auxiliary classes
    ri_telem = RuntimeTelemetryCollector()
    ri_perf = RuntimePerformanceAnalyzer(ri_telem)
    ri_capacity = RuntimeCapacityAnalyzer(ri_telem)
    ri_query_prof = RuntimeQueryProfiler()
    ri_tx_prof = RuntimeTransactionProfiler()
    ri_repo_prof = RuntimeRepositoryProfiler()
    ri_lifecycle = RuntimeLifecycleMonitor()
    ri_stats = RuntimeStatisticsEngine(service)
    ri_diag = RuntimeDiagnosticsEngine()
    ri_recommend = RuntimeRecommendationEngine(ri_telem, ri_perf, ri_capacity, ri_query_prof, ri_tx_prof, ri_repo_prof)
    ri_health = RuntimeHealthMonitor(service, ri_telem)
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
        ri_report
    )
    ri_report.intelligence = ri_service
    service.ri_service = ri_service

    # Initialize all
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

    return {
        "service": service,
        "ri_service": ri_service,
        "telemetry": ri_telem,
        "performance": ri_perf,
        "stats": ri_stats,
        "diagnostics": ri_diag,
        "recommend": ri_recommend,
        "capacity": ri_capacity,
        "query_prof": ri_query_prof,
        "tx_prof": ri_tx_prof,
        "repo_prof": ri_repo_prof,
        "lifecycle": ri_lifecycle,
    }


def test_correlation_manager():
    # Test setting context
    corr_id = RuntimeCorrelationManager.set_context(
        workspace_id="ws_123",
        project_id="proj_456",
        repository="test_repo",
        operation="save"
    )
    assert corr_id is not None

    ctx = RuntimeCorrelationManager.get_context()
    assert ctx["correlation_id"] == corr_id
    assert ctx["workspace_id"] == "ws_123"
    assert ctx["project_id"] == "proj_456"
    assert ctx["repository"] == "test_repo"
    assert ctx["operation"] == "save"

    # Test clear
    RuntimeCorrelationManager.clear()
    ctx_cleared = RuntimeCorrelationManager.get_context()
    assert ctx_cleared["correlation_id"] is None


def test_telemetry_and_performance(ri_setup):
    telem = ri_setup["telemetry"]
    perf = ri_setup["performance"]

    # Record multiple query metrics
    telem.record_query(10.0, True)
    telem.record_query(20.0, True)
    telem.record_query(30.0, True)
    telem.record_query(100.0, False)

    # Check metrics
    m = perf.get_performance_metrics()
    assert m["average_latency_ms"] == 40.0
    assert m["p50_latency_ms"] == 30.0
    assert m["p95_latency_ms"] == 100.0


def test_statistics_engine(ri_setup):
    stats = ri_setup["stats"]

    # Record operations and cache activities
    stats.record_operation(True, "STRICT")
    stats.record_operation(False, "BEST_EFFORT")
    stats.record_cache(True, is_read=True)
    stats.record_cache(False, is_read=True)
    stats.record_cache(True, is_read=False)

    s = stats.get_statistics()
    assert s["total_operations"] == 2
    assert s["success_operations"] == 1
    assert s["failed_operations"] == 1
    assert s["cache_hit_ratio"] == 0.5
    assert s["write_throughs"] == 1
    assert s["policies_used"] == {"STRICT": 1, "BEST_EFFORT": 1}


def test_diagnostics_and_recommendations(ri_setup):
    diag = ri_setup["diagnostics"]
    recommend = ri_setup["recommend"]
    telem = ri_setup["telemetry"]

    # Log diagnostics errors of different severities
    diag.log_error("Connection timed out", "ERROR", "Verify database server port status.")
    diag.log_error("Fatal pool exhaustion", "CRITICAL", "Increase connection pool size limits.")

    d = diag.get_diagnostics()
    assert d["status"] == "critical"
    assert d["total_logged_errors"] == 2
    assert d["errors"][0]["severity"] == "ERROR"

    # Simulate connection failures to trigger recommendations
    telem.record_connection_status(5, 0, 10)  # active, idle, failures

    # Generate recommendations
    recs = recommend.generate_recommendations()
    assert len(recs) > 0
    categories = [r["category"] for r in recs]
    assert "Reliability" in categories


def test_report_generation(ri_setup):
    ri_service = ri_setup["ri_service"]
    
    # Execute report generation
    ri_service.generate_reports()

    # Verify Markdown files exist
    r_dir = os.path.join(os.getcwd(), "docs", "persistence")
    assert os.path.exists(os.path.join(r_dir, "RUNTIME_INTELLIGENCE_STATUS.md"))
    assert os.path.exists(os.path.join(r_dir, "RUNTIME_INTELLIGENCE_HEALTH.md"))
    assert os.path.exists(os.path.join(r_dir, "RUNTIME_INTELLIGENCE_STATISTICS.md"))
    assert os.path.exists(os.path.join(r_dir, "RUNTIME_INTELLIGENCE_DIAGNOSTICS.md"))


def test_sql_execution_interceptor(ri_setup):
    service = ri_setup["service"]
    ri_service = ri_setup["ri_service"]

    # Execute SQL statement via PersistenceService
    # (Since we are using SQLite transport in memory, execute works out of the box)
    service.execute("SELECT 1")

    # Confirm query profiling and telemetry logged automatically
    telem_data = ri_service.get_telemetry()
    assert telem_data["queries_recorded"] == 1
