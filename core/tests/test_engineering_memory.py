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
    ApprovalRepositoryImpl,
    DocumentationMetadataRepositoryImpl,
    EngineeringMemoryHealthMonitor,
    EngineeringMemoryReportGenerator,
    EngineeringMemoryServiceImpl,
    EngineeringMemoryStatistics,
    EngineeringMemoryTelemetry,
    EngineeringMemoryValidator,
    EngineeringTaskRepositoryImpl,
    PersistenceBootstrapper,
    PersistenceServiceImpl,
    PlanningRepositoryImpl,
    PostgreSQLProvider,
    ReviewRepositoryImpl,
    TestResultRepositoryImpl,
    TestSessionRepositoryImpl,
)

from tests.test_persistence import SQLiteTransportForTests


@pytest.fixture
def memory_setup():
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
    bootstrapper.start()

    # Repositories
    task_repo = EngineeringTaskRepositoryImpl(service)
    planning_repo = PlanningRepositoryImpl(service)
    approval_repo = ApprovalRepositoryImpl(service)
    review_repo = ReviewRepositoryImpl(service)
    doc_repo = DocumentationMetadataRepositoryImpl(service)
    test_session_repo = TestSessionRepositoryImpl(service)
    test_result_repo = TestResultRepositoryImpl(service)

    # Register in registry
    repos.register_repository("tasks", task_repo)
    repos.register_repository("planning", planning_repo)
    repos.register_repository("approvals", approval_repo)
    repos.register_repository("reviews", review_repo)
    repos.register_repository("documentation", doc_repo)
    repos.register_repository("test_sessions", test_session_repo)
    repos.register_repository("test_results", test_result_repo)

    # Engineering Memory coordinator & services
    validator = EngineeringMemoryValidator()
    telemetry = EngineeringMemoryTelemetry()
    stats_compiler = EngineeringMemoryStatistics(service)
    health_monitor = EngineeringMemoryHealthMonitor(service, telemetry, stats_compiler)
    report_generator = EngineeringMemoryReportGenerator(os.getcwd(), health_monitor)

    memory_service = EngineeringMemoryServiceImpl(
        service,
        task_repo,
        planning_repo,
        approval_repo,
        review_repo,
        doc_repo,
        test_session_repo,
        test_result_repo,
        validator,
        telemetry,
        stats_compiler,
        health_monitor,
        report_generator,
    )

    yield {
        "service": service,
        "memory_service": memory_service,
        "task_repo": task_repo,
        "planning_repo": planning_repo,
        "approval_repo": approval_repo,
        "review_repo": review_repo,
        "doc_repo": doc_repo,
        "test_session_repo": test_session_repo,
        "test_result_repo": test_result_repo,
        "provider": provider,
    }

    provider.disconnect()


def test_record_and_update_task(memory_setup):
    ms = memory_setup["memory_service"]
    task_id = "task_001"
    task_data = {
        "id": task_id,
        "name": "Implement DB Repositories",
        "description": "Create Sprint 4 Milestone 3 repositories",
        "priority": "High",
        "status": "in_progress",
        "creation_time": time.time(),
        "update_time": time.time(),
        "completion_time": 0.0,
        "workspace": "default_workspace",
        "current_phase": "Implementation",
        "assigned_agent": "Antigravity",
        "dependencies": ["dep_001"],
        "retry_count": 0,
        "operation_results": {}
    }

    # Record task
    res = ms.Record("tasks", task_id, task_data)
    assert res.status == PersistenceStatus.SUCCESS

    # Search task
    search_res = ms.SearchMetadata("tasks", {"id": task_id})
    assert search_res.status == PersistenceStatus.SUCCESS
    assert len(search_res.payload) == 1
    assert search_res.payload[0]["name"] == "Implement DB Repositories"

    # Update task
    task_data["status"] = "completed"
    task_data["completion_time"] = time.time()
    update_res = ms.Update("tasks", task_id, task_data)
    assert update_res.status == PersistenceStatus.SUCCESS

    # Verify update
    search_res2 = ms.SearchMetadata("tasks", {"id": task_id})
    assert search_res2.payload[0]["status"] == "completed"


def test_record_and_update_plan(memory_setup):
    ms = memory_setup["memory_service"]
    plan_id = "plan_001"
    plan_data = {
        "id": plan_id,
        "execution_plan": {"phases": ["setup", "run"]},
        "decision_tree": {"root": "choice"},
        "architecture_decisions": {"database": "SQLite"},
        "dependency_graph": {"nodes": []},
        "planning_statistics": {"time_taken": 1.2},
        "planning_version": 1,
        "timestamp": time.time()
    }

    # Record plan
    res = ms.Record("planning", plan_id, plan_data)
    assert res.status == PersistenceStatus.SUCCESS

    # Search plan
    search_res = ms.SearchMetadata("planning", {"id": plan_id})
    assert search_res.status == PersistenceStatus.SUCCESS
    assert len(search_res.payload) == 1
    assert search_res.payload[0]["planning_version"] == 1


def test_archive_and_restore(memory_setup):
    ms = memory_setup["memory_service"]
    doc_id = "doc_001"
    doc_data = {
        "id": doc_id,
        "workspace_id": "ws_001",
        "session_id": "sess_001",
        "category": "Architecture",
        "status": "registered",
        "generation_time": time.time(),
        "author": "AI Architect",
        "publication_status": "draft",
        "knowledge_references": ["ref_1"],
        "checksums": {"sha256": "abc"},
        "version": 1
    }

    # Record doc
    ms.Record("documentation", doc_id, doc_data)

    # Archive
    archive_res = ms.Archive("documentation", doc_id)
    assert archive_res.status == PersistenceStatus.SUCCESS

    # Verify archived
    search_res = ms.SearchMetadata("documentation", {"id": doc_id})
    assert search_res.payload[0]["status"] == "archived"

    # Restore
    restore_res = ms.Restore("documentation", doc_id)
    assert restore_res.status == PersistenceStatus.SUCCESS

    # Verify restored
    search_res2 = ms.SearchMetadata("documentation", {"id": doc_id})
    assert search_res2.payload[0]["status"] == "active"


def test_statistics(memory_setup):
    ms = memory_setup["memory_service"]
    
    # Empty stats initially
    stats_res = ms.Statistics()
    assert stats_res.status == PersistenceStatus.SUCCESS
    assert stats_res.payload["task_count"] == 0

    # Insert a task
    ms.Record("tasks", "task_1", {
        "id": "task_1",
        "name": "t1",
        "description": "d",
        "priority": "Low",
        "status": "completed",
        "creation_time": time.time(),
        "update_time": time.time(),
        "completion_time": time.time(),
        "workspace": "ws",
        "current_phase": "p",
        "assigned_agent": "a",
        "dependencies": [],
        "retry_count": 0,
        "operation_results": {}
    })

    # Stats compilation should update
    stats_res2 = ms.Statistics()
    assert stats_res2.payload["task_count"] == 1


def test_strict_policy_fails_on_db_issue(memory_setup):
    ms = memory_setup["memory_service"]
    provider = memory_setup["provider"]
    config = ms.service.config

    # Set policy to STRICT
    config.policy = PersistencePolicy.STRICT

    # Break connection/disconnect provider
    provider.disconnect()

    # Call should raise RuntimeError under STRICT policy
    with pytest.raises(RuntimeError):
        ms.Record("tasks", "task_error", {
            "id": "task_error",
            "name": "t_err",
            "description": "d",
            "priority": "Low",
            "status": "pending",
            "creation_time": time.time(),
            "update_time": time.time(),
            "completion_time": 0.0,
            "workspace": "ws",
            "current_phase": "p",
            "assigned_agent": "a",
            "dependencies": [],
            "retry_count": 0,
            "operation_results": {}
        })
