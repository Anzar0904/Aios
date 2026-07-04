import os
import time
import pytest
from unittest.mock import MagicMock

from aios.services.memory import MemoryService, MemoryType
from aios.services.knowledge_hub import KnowledgeHubService
from aios.services.model import ModelService, LLMResponse
from aios.services.ai_workspace import AIWorkspaceService, WorkspaceMetadata
from aios.services.workflow_monitoring import (
    WorkflowExecutionState,
    WorkflowExecutionMetrics,
    WorkflowExecutionRecord,
    WorkflowTelemetry,
    WorkflowAlert,
    WorkflowHealthScore,
    WorkflowStatistics,
    WorkflowMonitoringReport,
)
from aios.services.workflow_monitoring_impl import (
    LocalWorkflowMonitoringValidator,
    LocalWorkflowPerformanceAnalyzer,
    LocalWorkflowMonitoringService,
)


@pytest.fixture
def mock_memory_service():
    service = MagicMock(spec=MemoryService)
    return service


@pytest.fixture
def mock_workspace_service():
    service = MagicMock(spec=AIWorkspaceService)
    return service


@pytest.fixture
def mock_model_service():
    service = MagicMock(spec=ModelService)
    response = MagicMock(spec=LLMResponse)
    response.content = "LLM Refined Workflow Telemetry overview."
    service.execute_request.return_value = response
    return service


def test_performance_analytics():
    analyzer = LocalWorkflowPerformanceAnalyzer()
    
    # 3 mock runs
    r1 = WorkflowExecutionRecord(
        "ex_1", "wf_test", "ws_1", WorkflowExecutionState.SUCCESS,
        WorkflowExecutionMetrics(10.0, 1.0, 0, 5.0, 50.0), time.time()
    )
    r2 = WorkflowExecutionRecord(
        "ex_2", "wf_test", "ws_1", WorkflowExecutionState.SUCCESS,
        WorkflowExecutionMetrics(20.0, 1.0, 1, 5.0, 50.0), time.time()
    )
    r3 = WorkflowExecutionRecord(
        "ex_3", "wf_test", "ws_1", WorkflowExecutionState.FAILED,
        WorkflowExecutionMetrics(30.0, 1.0, 0, 5.0, 50.0), time.time(),
        error_message="Connection timed out"
    )

    stats = analyzer.analyze_performance([r1, r2, r3])
    
    assert stats.total_runs == 3
    assert stats.success_rate == pytest.approx(2/3)
    assert stats.failure_rate == pytest.approx(1/3)
    assert stats.retry_rate == pytest.approx(1/3)
    assert stats.average_duration == pytest.approx(20.0)
    assert stats.median_duration == pytest.approx(20.0)
    assert stats.p95_duration == pytest.approx(30.0)


def test_telemetry_validation():
    validator = LocalWorkflowMonitoringValidator()

    # Valid record
    r_valid = WorkflowExecutionRecord(
        "ex_1", "wf_test", "ws_1", WorkflowExecutionState.SUCCESS,
        WorkflowExecutionMetrics(10.0, 1.0, 0, 5.0, 50.0), 100.0, 110.0
    )
    assert len(validator.validate_telemetry([r_valid])) == 0

    # Invalid record (end_time before start_time)
    r_invalid = WorkflowExecutionRecord(
        "ex_2", "wf_test", "ws_1", WorkflowExecutionState.SUCCESS,
        WorkflowExecutionMetrics(10.0, 1.0, 0, 5.0, 50.0), 120.0, 110.0
    )
    errors = validator.validate_telemetry([r_invalid])
    assert len(errors) > 0
    assert any("integrity breach" in e.lower() for e in errors)


def test_monitoring_alerts_and_health_scoring(mock_memory_service):
    service = LocalWorkflowMonitoringService(memory_service=mock_memory_service)
    service.initialize()

    # Log 2 consecutive failures
    r1 = WorkflowExecutionRecord(
        "ex_1", "wf_test", "ws_1", WorkflowExecutionState.FAILED,
        WorkflowExecutionMetrics(10.0, 1.0, 0, 5.0, 50.0), time.time(),
        error_message="Compilation Error"
    )
    r2 = WorkflowExecutionRecord(
        "ex_2", "wf_test", "ws_1", WorkflowExecutionState.FAILED,
        WorkflowExecutionMetrics(400.0, 1.0, 3, 5.0, 50.0), time.time(), # triggers high retry and long duration alert too
        error_message="Compilation Error"
    )

    service.record_execution(r1)
    service.record_execution(r2)

    report = service.get_telemetry_report("ws_1")

    # Alerts checks
    alerts = report.alerts
    assert len(alerts) >= 3
    types = [a.alert_type for a in alerts]
    assert "repeated_failure" in types
    assert "long_duration" in types
    assert "high_retry" in types

    # Health score checks
    score_obj = report.health_scores["wf_test"]
    # deductions: 2 failures * 20.0 + 1 retry * 10.0 = 50.0. Score must be 50.0.
    assert score_obj.score == 50.0
    assert score_obj.status == "degraded"


def test_workspace_integration(tmp_path, mock_memory_service, mock_workspace_service):
    ws_id = "ws_test_mon"
    ws_root = str(tmp_path / ws_id)
    os.makedirs(ws_root, exist_ok=True)

    meta = WorkspaceMetadata(ws_id, 0.0, "/src", ws_root, "active")
    mock_workspace_service._workspaces = {ws_id: meta}

    registry = MagicMock()
    registry.get.side_effect = lambda t: mock_workspace_service if t == AIWorkspaceService else None

    service = LocalWorkflowMonitoringService(
        memory_service=mock_memory_service,
        registry=registry
    )
    service.initialize()

    r = WorkflowExecutionRecord(
        "ex_1", "wf_test", ws_id, WorkflowExecutionState.SUCCESS,
        WorkflowExecutionMetrics(15.0, 1.0, 0, 5.0, 50.0), time.time()
    )
    service.record_execution(r)

    report = service.get_telemetry_report(ws_id)
    expected_file = os.path.join(ws_root, "docs", "monitors", f"TELEMETRY_REPORT_{ws_id}.md")

    assert os.path.exists(expected_file)
    with open(expected_file, "r") as f:
        content = f.read()
    assert "# Workflow Telemetry & Health Monitoring Report" in content


def test_memory_integration(mock_memory_service):
    service = LocalWorkflowMonitoringService(
        memory_service=mock_memory_service
    )
    service.initialize()

    r = WorkflowExecutionRecord(
        "ex_1", "wf_test", "ws_1", WorkflowExecutionState.SUCCESS,
        WorkflowExecutionMetrics(15.0, 1.0, 0, 5.0, 50.0), time.time()
    )
    service.record_execution(r)
    service.get_telemetry_report("ws_1")
    service.store_monitoring_summary("ws_1")

    mock_memory_service.add_memory.assert_called_once()
    args, kwargs = mock_memory_service.add_memory.call_args
    content = kwargs.get("content", args[0] if args else "")
    tags = kwargs.get("tags", [])

    assert "source code" not in content.lower()
    assert "Workflow Telemetry Logged" in content
    assert "workflow_monitoring" in tags


def test_knowledge_hub_integration(mock_memory_service):
    mock_kh = MagicMock(spec=KnowledgeHubService)
    service = LocalWorkflowMonitoringService(
        memory_service=mock_memory_service,
        knowledge_hub=mock_kh
    )
    service.initialize()

    report = WorkflowMonitoringReport(
        report_id="rep_mon_123",
        workspace_id="ws_1",
        statistics={},
        health_scores={},
        alerts=[],
        timestamp=time.time()
    )
    service.publish_monitoring_report(report)

    mock_kh.sync_document.assert_called_once()
    args, kwargs = mock_kh.sync_document.call_args
    doc = args[0]
    assert doc.title == "Workflow Monitoring - rep_mon_123"
    assert "Notion Sync" in doc.content


def test_backward_compatibility():
    class CustomPerformanceAnalyzer(LocalWorkflowPerformanceAnalyzer):
        def analyze_performance(self, records):
            stats = super().analyze_performance(records)
            stats.average_duration = 999.0
            return stats

    analyzer = CustomPerformanceAnalyzer()
    r = WorkflowExecutionRecord(
        "ex_1", "wf_test", "ws_1", WorkflowExecutionState.SUCCESS,
        WorkflowExecutionMetrics(15.0, 1.0, 0, 5.0, 50.0), time.time()
    )
    stats = analyzer.analyze_performance([r])
    assert stats.average_duration == 999.0
