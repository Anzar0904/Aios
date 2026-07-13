import os
import time

import pytest
from aios.services.persistence import (
    PersistenceConfigurationService,
    PersistencePolicy,
    PersistenceRegistry,
    PersistenceStatus,
    RepositoryRegistry,
)
from aios.services.persistence_impl import (
    AutomationPersistenceHealthMonitor,
    AutomationPersistenceReportGenerator,
    AutomationPersistenceServiceImpl,
    AutomationPersistenceStatistics,
    AutomationPersistenceTelemetry,
    AutomationPersistenceValidator,
    AutomationStatisticsRepositoryImpl,
    AutomationTelemetryRepositoryImpl,
    PersistenceBootstrapper,
    PersistenceServiceImpl,
    PostgreSQLProvider,
    WorkflowExecutionRepositoryImpl,
    WorkflowIntegrationRepositoryImpl,
    WorkflowMonitoringRepositoryImpl,
    WorkflowOptimizationRepositoryImpl,
    WorkflowRepositoryImpl,
    WorkflowTranslationRepositoryImpl,
    WorkflowVersionRepositoryImpl,
)

from tests.test_persistence import SQLiteTransportForTests


@pytest.fixture
def automation_setup():
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

    # Bootstrap schemas including Level 16-23 migrations
    bootstrapper = PersistenceBootstrapper(service)
    bootstrapper.initialize()
    bootstrapper.start()

    # Repositories
    workflow_repo = WorkflowRepositoryImpl(service)
    execution_repo = WorkflowExecutionRepositoryImpl(service)
    monitor_repo = WorkflowMonitoringRepositoryImpl(service)
    optimization_repo = WorkflowOptimizationRepositoryImpl(service)
    version_repo = WorkflowVersionRepositoryImpl(service)
    translation_repo = WorkflowTranslationRepositoryImpl(service)
    integration_repo = WorkflowIntegrationRepositoryImpl(service)
    telemetry_repo = AutomationTelemetryRepositoryImpl(service)
    stats_repo = AutomationStatisticsRepositoryImpl(service)

    # Register in RepositoryRegistry
    repos.register_repository("automation_workflows", workflow_repo)
    repos.register_repository("workflow_executions", execution_repo)
    repos.register_repository("workflow_monitoring", monitor_repo)
    repos.register_repository("workflow_optimizations", optimization_repo)
    repos.register_repository("workflow_versions", version_repo)
    repos.register_repository("workflow_translations", translation_repo)
    repos.register_repository("workflow_integrations", integration_repo)
    repos.register_repository("automation_statistics", stats_repo)

    # Instantiate auxiliary services
    validator = AutomationPersistenceValidator()
    telemetry = AutomationPersistenceTelemetry()
    stats_compiler = AutomationPersistenceStatistics(service)
    health_monitor = AutomationPersistenceHealthMonitor(service, telemetry, stats_compiler)
    report_generator = AutomationPersistenceReportGenerator(os.getcwd(), health_monitor)

    persistence_service = AutomationPersistenceServiceImpl(
        service,
        workflow_repo,
        execution_repo,
        monitor_repo,
        optimization_repo,
        version_repo,
        translation_repo,
        integration_repo,
        telemetry_repo,
        stats_repo,
        validator,
        telemetry,
        stats_compiler,
        health_monitor,
        report_generator
    )

    yield {
        "service": service,
        "workflow_repo": workflow_repo,
        "execution_repo": execution_repo,
        "monitor_repo": monitor_repo,
        "optimization_repo": optimization_repo,
        "version_repo": version_repo,
        "translation_repo": translation_repo,
        "integration_repo": integration_repo,
        "telemetry_repo": telemetry_repo,
        "stats_repo": stats_repo,
        "persistence_service": persistence_service,
        "health_monitor": health_monitor,
        "telemetry": telemetry,
        "report_generator": report_generator,
        "config": config
    }


def test_workflow_repository_crud(automation_setup):
    repo = automation_setup["workflow_repo"]
    config = automation_setup["config"]
    workflow = {
        "id": "wf_test_1",
        "name": "Integration Test Workflow",
        "description": "Validates system integration routines.",
        "metadata": {"tags": ["test"], "labels": {"env": "staging"}},
        "triggers": [{"trigger_id": "trig_1", "trigger_type": "webhook", "config": {}}],
        "actions": [{"action_id": "act_1", "action_type": "script", "config": {}}],
        "conditions": [],
        "variables": [],
        "policy": {"max_retries": 3, "retry_delay_seconds": 10, "timeout_seconds": 600, "concurrency_limit": 1}
    }

    # Create / Save
    res = repo.save(workflow)
    assert res.status == PersistenceStatus.SUCCESS

    # Get
    res_get = repo.get("wf_test_1")
    assert res_get.status == PersistenceStatus.SUCCESS
    assert res_get.payload["name"] == "Integration Test Workflow"
    assert res_get.payload["metadata"]["tags"] == ["test"]

    # Delete
    res_del = repo.delete("wf_test_1")
    assert res_del.status == PersistenceStatus.SUCCESS

    # Try Get Deleted in BEST_EFFORT mode
    config.policy = PersistencePolicy.BEST_EFFORT
    res_get_missing = repo.get("wf_test_1")
    assert res_get_missing.status == PersistenceStatus.UNKNOWN_FAILURE


def test_workflow_execution_repository_crud(automation_setup):
    repo = automation_setup["execution_repo"]
    execution = {
        "id": "exec_test_1",
        "workflow_id": "wf_test_1",
        "workspace_id": "ws_test_1",
        "status": "success",
        "success": 1,
        "error_summary": None,
        "execution_time": 4.5,
        "created_at": time.time(),
        "closed_at": time.time(),
        "metadata": {"provider": "n8n"}
    }

    res = repo.save(execution)
    assert res.status == PersistenceStatus.SUCCESS

    res_get = repo.get("exec_test_1")
    assert res_get.status == PersistenceStatus.SUCCESS
    assert res_get.payload["status"] == "success"
    assert res_get.payload["metadata"]["provider"] == "n8n"

    repo.delete("exec_test_1")


def test_automation_persistence_service_coordinator(automation_setup):
    service = automation_setup["persistence_service"]
    workflow = {
        "id": "wf_test_coordinator",
        "name": "Coordinator Workflow",
        "description": "Validates persistent coordinator workflows.",
        "metadata": {"tags": ["coord"]},
        "triggers": [],
        "actions": [],
        "conditions": [],
        "variables": [],
        "policy": {}
    }

    # Record
    res = service.Record("workflows", "wf_test_coordinator", workflow)
    assert res.status == PersistenceStatus.SUCCESS

    # SearchMetadata
    res_search = service.SearchMetadata("workflows", {"name": "Coordinator Workflow"})
    assert res_search.status == PersistenceStatus.SUCCESS
    assert len(res_search.payload) == 1
    assert res_search.payload[0]["id"] == "wf_test_coordinator"

    # Archive
    res_arch = service.Archive("workflows", "wf_test_coordinator")
    assert res_arch.status == PersistenceStatus.SUCCESS

    # Restore
    res_rest = service.Restore("workflows", "wf_test_coordinator")
    assert res_rest.status == PersistenceStatus.SUCCESS

    # History
    res_hist = service.History("workflows", "wf_test_coordinator")
    assert res_hist.status == PersistenceStatus.SUCCESS
    assert len(res_hist.payload) == 1


def test_persistence_policy_strict_mode(automation_setup):
    config = automation_setup["config"]
    repo = automation_setup["workflow_repo"]

    # Set strict mode policy
    config.policy = PersistencePolicy.STRICT

    # Attempting to retrieve a missing workflow should raise RuntimeError in STRICT mode
    with pytest.raises(RuntimeError):
        repo.get("non_existent_workflow")


def test_health_monitoring_and_telemetry(automation_setup):
    health_monitor = automation_setup["health_monitor"]
    telemetry = automation_setup["telemetry"]
    report_gen = automation_setup["report_generator"]

    # Trigger some simulated queries
    telemetry.record_query(15.4, True)
    telemetry.record_query(22.1, False)

    health = health_monitor.check_health()
    assert health["status"] in ["healthy", "degraded"]
    assert health["failures"] == 1
    assert health["db_connected"] is True

    report = report_gen.generate_health_report()
    assert "Overall Status" in report
    assert "Failures Tallied**: 1" in report
