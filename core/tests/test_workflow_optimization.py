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
    WorkflowMonitoringService,
)
from aios.services.workflow_monitoring_impl import LocalWorkflowMonitoringService
from aios.services.workflow_optimization import (
    WorkflowOptimizationCategory,
    WorkflowOptimizationImpact,
    WorkflowOptimizationRecommendation,
    WorkflowOptimizationPlan,
    WorkflowOptimizationReport,
)
from aios.services.workflow_optimization_impl import (
    LocalWorkflowCostAnalyzer,
    LocalWorkflowLatencyAnalyzer,
    LocalWorkflowParallelizationAnalyzer,
    LocalWorkflowOptimizationValidator,
    LocalWorkflowOptimizationService,
)


@pytest.fixture
def mock_memory_service():
    service = MagicMock(spec=MemoryService)
    return service


@pytest.fixture
def mock_workspace_service():
    service = MagicMock(spec=AIWorkspaceService)
    return service


def test_cost_analyzer():
    analyzer = LocalWorkflowCostAnalyzer()
    
    # Trace with high CPU usage trigger cost cache
    r1 = WorkflowExecutionRecord(
        "ex_1", "wf_test", "ws_1", WorkflowExecutionState.SUCCESS,
        WorkflowExecutionMetrics(10.0, 1.0, 0, 70.0, 50.0), time.time()
    )

    recs = analyzer.analyze_cost(None, [r1])
    assert len(recs) == 1
    assert recs[0].category == WorkflowOptimizationCategory.CACHING
    assert "High CPU footprint" in recs[0].reasoning


def test_latency_analyzer():
    analyzer = LocalWorkflowLatencyAnalyzer()
    
    # Trace with duration > 20s
    r1 = WorkflowExecutionRecord(
        "ex_1", "wf_test", "ws_1", WorkflowExecutionState.SUCCESS,
        WorkflowExecutionMetrics(25.0, 1.0, 0, 5.0, 50.0), time.time()
    )

    recs = analyzer.analyze_latency(None, [r1])
    assert len(recs) == 1
    assert recs[0].category == WorkflowOptimizationCategory.PERFORMANCE
    assert recs[0].priority == "high"


def test_parallelization_analyzer():
    analyzer = LocalWorkflowParallelizationAnalyzer()
    recs = analyzer.analyze_parallelization(None, [])
    assert len(recs) == 1
    assert recs[0].category == WorkflowOptimizationCategory.PARALLELIZATION


def test_optimization_validator():
    validator = LocalWorkflowOptimizationValidator()

    # Valid plan
    rec = WorkflowOptimizationRecommendation(
        "rec_1", WorkflowOptimizationCategory.COST, "medium",
        WorkflowOptimizationImpact.MEDIUM, 0.8, "Reasoning", "Evidence",
        ["Node1"], "Benefit", "easy"
    )
    plan_valid = WorkflowOptimizationPlan("plan_1", "wf_test", [rec])
    assert len(validator.validate_plan(plan_valid)) == 0

    # Invalid confidence range
    rec_invalid = WorkflowOptimizationRecommendation(
        "rec_1", WorkflowOptimizationCategory.COST, "medium",
        WorkflowOptimizationImpact.MEDIUM, 1.5, "Reasoning", "Evidence",
        ["Node1"], "Benefit", "easy"
    )
    plan_invalid = WorkflowOptimizationPlan("plan_1", "wf_test", [rec_invalid])
    errors = validator.validate_plan(plan_invalid)
    assert len(errors) > 0
    assert any("confidence" in e.lower() for e in errors)


def test_optimization_service_report(tmp_path, mock_memory_service, mock_workspace_service):
    ws_id = "ws_test_opt"
    ws_root = str(tmp_path / ws_id)
    os.makedirs(ws_root, exist_ok=True)

    meta = WorkspaceMetadata(ws_id, 0.0, "/src", ws_root, "active")
    mock_workspace_service._workspaces = {ws_id: meta}

    # Setup monitoring tracker with records
    mon_service = LocalWorkflowMonitoringService(memory_service=mock_memory_service)
    mon_service.initialize()
    
    r1 = WorkflowExecutionRecord(
        "ex_1", "wf_test", ws_id, WorkflowExecutionState.SUCCESS,
        WorkflowExecutionMetrics(30.0, 1.0, 0, 80.0, 50.0), time.time()
    )
    mon_service.record_execution(r1)

    registry = MagicMock()
    registry.get.side_effect = lambda t: (
        mock_workspace_service if t == AIWorkspaceService else
        mon_service if t == WorkflowMonitoringService else None
    )

    service = LocalWorkflowOptimizationService(
        memory_service=mock_memory_service,
        registry=registry
    )
    service.initialize()

    report = service.generate_optimization_report(ws_id)
    assert report.total_time_savings_seconds > 0
    assert report.total_cost_savings_dollars > 0

    expected_file = os.path.join(ws_root, "docs", "monitors", f"OPTIMIZATION_REPORT_{ws_id}.md")
    assert os.path.exists(expected_file)
    with open(expected_file, "r") as f:
        content = f.read()
    assert "# Workflow Optimization Intelligence Report" in content


def test_memory_integration(mock_memory_service):
    service = LocalWorkflowOptimizationService(
        memory_service=mock_memory_service
    )
    service.initialize()

    p = WorkflowOptimizationPlan("plan_1", "wf_test")
    report = WorkflowOptimizationReport(
        report_id="rep_opt_123",
        workspace_id="ws_1",
        plans={"wf_test": p},
        optimization_score=95.0,
        total_time_savings_seconds=10.0,
        total_cost_savings_dollars=0.1,
        timestamp=time.time()
    )
    service._reports["ws_1"] = [report]
    service.store_optimization_summary("ws_1")

    mock_memory_service.add_memory.assert_called_once()
    args, kwargs = mock_memory_service.add_memory.call_args
    content = kwargs.get("content", args[0] if args else "")
    tags = kwargs.get("tags", [])

    assert "source code" not in content.lower()
    assert "Workflow Optimizations Audited" in content
    assert "workflow_optimization" in tags


def test_knowledge_hub_integration(mock_memory_service):
    mock_kh = MagicMock(spec=KnowledgeHubService)
    service = LocalWorkflowOptimizationService(
        memory_service=mock_memory_service,
        knowledge_hub=mock_kh
    )
    service.initialize()

    report = WorkflowOptimizationReport(
        report_id="rep_opt_123",
        workspace_id="ws_1",
        plans={},
        optimization_score=90.0,
        total_time_savings_seconds=10.0,
        total_cost_savings_dollars=0.1,
        timestamp=time.time()
    )
    service.publish_optimization_report(report)

    mock_kh.sync_document.assert_called_once()
    args, kwargs = mock_kh.sync_document.call_args
    doc = args[0]
    assert doc.title == "Workflow Optimization - rep_opt_123"
    assert "Notion Sync" in doc.content


def test_backward_compatibility():
    class CustomCostAnalyzer(LocalWorkflowCostAnalyzer):
        def analyze_cost(self, graph, telemetry):
            recs = super().analyze_cost(graph, telemetry)
            recs.append(
                WorkflowOptimizationRecommendation(
                    "rec_custom", WorkflowOptimizationCategory.COST, "low",
                    WorkflowOptimizationImpact.LOW, 0.99, "Custom reasoning", "Evidence",
                    ["CustomNode"], "Benefit", "easy"
                )
            )
            return recs

    analyzer = CustomCostAnalyzer()
    r = WorkflowExecutionRecord(
        "ex_1", "wf_test", "ws_1", WorkflowExecutionState.SUCCESS,
        WorkflowExecutionMetrics(10.0, 1.0, 0, 70.0, 50.0), time.time()
    )
    recs = analyzer.analyze_cost(None, [r])
    assert len(recs) == 2
    assert recs[1].recommendation_id == "rec_custom"
