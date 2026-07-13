from unittest.mock import MagicMock

import pytest
from aios.services.knowledge_hub import KnowledgeHubService
from aios.services.memory import MemoryService
from aios.services.test_coverage import CoveragePolicy
from aios.services.test_coverage_impl import (
    LocalAITestCoverageService,
    LocalCoverageAnalyzer,
    LocalRegressionAnalyzer,
)
from aios.services.test_execution import (
    ExecutionMetrics,
    ExecutionResult,
    ExecutionSummary,
    ExecutionTarget,
)


@pytest.fixture
def dummy_exec_summary():
    target = ExecutionTarget("t1", "core/tests/test_memory.py")
    res = ExecutionResult(
        target=target,
        success=True,
        exit_code=0,
        metrics=ExecutionMetrics(10, 9, 1, 0, 0.52),
        raw_output="9 passed, 1 failed"
    )
    return ExecutionSummary(
        summary_id="s1",
        workspace_id="ws_1",
        overall_success=False,
        total_duration=0.52,
        total_passed=9,
        total_failed=1,
        total_skipped=0,
        results=[res],
        timestamp=0.0
    )


def test_coverage_analyzer(dummy_exec_summary):
    analyzer = LocalCoverageAnalyzer()
    policy = CoveragePolicy("p1", 90.0, 85.0)
    
    report = analyzer.analyze_coverage(dummy_exec_summary, [], policy)
    assert report.summary.metrics.statement_coverage > 50.0
    assert report.summary.overall_coverage_pct > 50.0


def test_regression_analyzer(dummy_exec_summary):
    analyzer = LocalRegressionAnalyzer()
    dep_graph = {
        "core/src/aios/kernel.py": ["core/src/aios/services/memory.py"],
        "core/src/aios/services/memory.py": []
    }
    
    # 1. Non-critical risk
    risk_std = analyzer.analyze_regression_risks(["core/src/aios/services/memory.py"], dep_graph, dummy_exec_summary)
    assert risk_std.risk_level in ["Medium", "High", "Critical"] # because memory.py is imported by kernel.py
    
    # 2. Critical file changes risk (kernel.py)
    risk_crit = analyzer.analyze_regression_risks(["core/src/aios/kernel.py"], dep_graph, dummy_exec_summary)
    assert risk_crit.risk_level == "High"
    assert risk_crit.regression_probability >= 0.70


def test_validation_gaps_identification(dummy_exec_summary):
    mock_memory = MagicMock(spec=MemoryService)
    mock_kh = MagicMock(spec=KnowledgeHubService)
    
    service = LocalAITestCoverageService(memory_service=mock_memory, knowledge_hub=mock_kh)
    policy = CoveragePolicy("p1", 95.0, 90.0) # High policy triggers gap
    
    result = service.evaluate_validation(
        workspace_id="ws_1",
        execution_summary=dummy_exec_summary,
        affected_files=["core/src/aios/services/memory.py"],
        dependency_graph={"core/src/aios/kernel.py": ["core/src/aios/services/memory.py"]},
        policy=policy
    )
    
    assert "coverage_report" in result
    assert "regression_risk" in result
    assert len(result["validation_gaps"]) >= 1
    assert result["validation_gaps"][0].gap_type == "low_coverage"


def test_service_evaluation_flow(dummy_exec_summary):
    mock_memory = MagicMock(spec=MemoryService)
    mock_kh = MagicMock(spec=KnowledgeHubService)
    
    service = LocalAITestCoverageService(
        memory_service=mock_memory,
        knowledge_hub=mock_kh
    )
    service.initialize()
    
    policy = CoveragePolicy("p1", 80.0, 75.0)
    result = service.evaluate_validation(
        workspace_id="ws_1",
        execution_summary=dummy_exec_summary,
        affected_files=["core/src/aios/services/memory.py"],
        dependency_graph={},
        policy=policy
    )
    
    report = result["coverage_report"]
    
    # Store
    service.store_coverage_summary(report)
    mock_memory.add_memory.assert_called_once()
    
    # Publish
    service.publish_coverage_report(report)
    mock_kh.sync_document.assert_called_once()


def test_backward_compatibility():
    class CustomAnalyzer(LocalCoverageAnalyzer):
        def analyze_coverage(self, execution_summary, targets, policy):
            report = super().analyze_coverage(execution_summary, targets, policy)
            report.summary.overall_coverage_pct = 100.0
            return report
            
    analyzer = CustomAnalyzer()
    report = analyzer.analyze_coverage(MagicMock(), [], MagicMock())
    assert report.summary.overall_coverage_pct == 100.0
