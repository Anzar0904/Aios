import os
import time
from unittest.mock import MagicMock

import pytest
from aios.services.ai_workspace import AIWorkspaceService, WorkspaceMetadata
from aios.services.knowledge_hub import KnowledgeHubService
from aios.services.memory import MemoryService
from aios.services.workflow_monitoring import (
    WorkflowExecutionMetrics,
    WorkflowExecutionRecord,
    WorkflowExecutionState,
    WorkflowMonitoringService,
)
from aios.services.workflow_monitoring_impl import LocalWorkflowMonitoringService
from aios.services.workflow_optimization import (
    WorkflowOptimizationCategory,
    WorkflowOptimizationImpact,
    WorkflowOptimizationKnowledgeBase,
    WorkflowOptimizationPlan,
    WorkflowOptimizationPriority,
    WorkflowOptimizationRecommendation,
    WorkflowOptimizationReport,
)
from aios.services.workflow_optimization_impl import (
    LocalWorkflowComplexityAnalyzer,
    LocalWorkflowCostAnalyzer,
    LocalWorkflowLatencyAnalyzer,
    LocalWorkflowOptimizationService,
    LocalWorkflowOptimizationValidator,
    LocalWorkflowParallelizationAnalyzer,
)


@pytest.fixture
def mock_memory_service():
    service = MagicMock(spec=MemoryService)
    return service


@pytest.fixture
def mock_workspace_service():
    service = MagicMock(spec=AIWorkspaceService)
    return service


def test_knowledge_base():
    kb = WorkflowOptimizationKnowledgeBase()
    patterns = kb.get_all_patterns()
    assert len(patterns) >= 15
    p = kb.get_pattern("missing_cache")
    assert p is not None
    assert p.name == "Missing Cache"


def test_cost_analyzer():
    analyzer = LocalWorkflowCostAnalyzer()
    r1 = WorkflowExecutionRecord(
        "ex_1", "wf_test", "ws_1", WorkflowExecutionState.SUCCESS,
        WorkflowExecutionMetrics(10.0, 1.0, 0, 70.0, 50.0), time.time()
    )
    recs = analyzer.analyze_cost(None, [r1])
    assert len(recs) == 1
    assert recs[0].category == WorkflowOptimizationCategory.CACHING
    assert "High CPU footprint" in recs[0].reasoning
    assert "missing_cache" in recs[0].pattern_ids


def test_latency_analyzer():
    analyzer = LocalWorkflowLatencyAnalyzer()
    r1 = WorkflowExecutionRecord(
        "ex_1", "wf_test", "ws_1", WorkflowExecutionState.SUCCESS,
        WorkflowExecutionMetrics(25.0, 1.0, 0, 5.0, 50.0), time.time()
    )
    recs = analyzer.analyze_latency(None, [r1])
    assert len(recs) == 1
    assert recs[0].category == WorkflowOptimizationCategory.TIMEOUTS
    assert recs[0].priority == WorkflowOptimizationPriority.HIGH


def test_parallelization_analyzer():
    analyzer = LocalWorkflowParallelizationAnalyzer()
    recs = analyzer.analyze_parallelization(None, [])
    assert len(recs) == 1
    assert recs[0].category == WorkflowOptimizationCategory.PARALLELIZATION


def test_complexity_analyzer():
    analyzer = LocalWorkflowComplexityAnalyzer()
    metrics = analyzer.analyze_complexity(None)
    assert metrics["complexity_level"] == 1.0
    assert "complexity_score" in metrics


def test_optimization_validator():
    kb = WorkflowOptimizationKnowledgeBase()
    validator = LocalWorkflowOptimizationValidator(kb)

    rec = WorkflowOptimizationRecommendation(
        recommendation_id="rec_1",
        category=WorkflowOptimizationCategory.COST,
        priority=WorkflowOptimizationPriority.MEDIUM,
        expected_impact=WorkflowOptimizationImpact.MEDIUM,
        confidence=0.8,
        reasoning="Reasoning",
        supporting_evidence="Evidence",
        affected_nodes=["Node1"],
        affected_branches=["Branch1"],
        expected_time_savings_seconds=10.0,
        expected_cost_savings_dollars=0.05,
        estimated_risk=0.1,
        implementation_difficulty="easy",
        rollback_considerations="None",
        pattern_ids=["missing_cache"]
    )
    plan_valid = WorkflowOptimizationPlan("plan_1", "wf_test", [rec])
    assert len(validator.validate_plan(plan_valid)) == 0

    # Invalid confidence range
    rec_invalid = WorkflowOptimizationRecommendation(
        recommendation_id="rec_1",
        category=WorkflowOptimizationCategory.COST,
        priority=WorkflowOptimizationPriority.MEDIUM,
        expected_impact=WorkflowOptimizationImpact.MEDIUM,
        confidence=1.5,
        reasoning="Reasoning",
        supporting_evidence="Evidence",
        affected_nodes=["Node1"],
        affected_branches=["Branch1"],
        expected_time_savings_seconds=10.0,
        expected_cost_savings_dollars=0.05,
        estimated_risk=0.1,
        implementation_difficulty="easy",
        rollback_considerations="None",
        pattern_ids=["missing_cache"]
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
                    recommendation_id="rec_custom",
                    category=WorkflowOptimizationCategory.COST,
                    priority=WorkflowOptimizationPriority.LOW,
                    expected_impact=WorkflowOptimizationImpact.LOW,
                    confidence=0.99,
                    reasoning="Custom reasoning",
                    supporting_evidence="Evidence",
                    affected_nodes=["CustomNode"],
                    affected_branches=["CustomBranch"],
                    expected_time_savings_seconds=0.0,
                    expected_cost_savings_dollars=0.0,
                    estimated_risk=0.0,
                    implementation_difficulty="easy",
                    rollback_considerations="None",
                    pattern_ids=["missing_cache"]
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
