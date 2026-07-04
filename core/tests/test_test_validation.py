import pytest
from unittest.mock import MagicMock

from aios.services.memory import MemoryService
from aios.services.knowledge_hub import KnowledgeHubService
from aios.services.model import ModelService, LLMResponse
from aios.services.test_execution import ExecutionSummary, ExecutionResult, ExecutionMetrics
from aios.services.test_coverage import CoverageReport, CoverageSummary, CoverageMetrics, CoveragePolicy
from aios.services.test_failure import FailureAnalysisReport, FailureSeverity, FailureConfidence
from aios.services.test_validation import ValidationStatus, ValidationDecision
from aios.services.test_validation_impl import LocalValidationService


@pytest.fixture
def mock_exec_summary():
    summary = MagicMock(spec=ExecutionSummary)
    summary.workspace_id = "ws_1"
    summary.total_passed = 10
    summary.total_failed = 0
    summary.results = []
    return summary


@pytest.fixture
def mock_coverage_report():
    summary = MagicMock(spec=CoverageSummary)
    summary.overall_coverage_pct = 85.0
    summary.metrics = MagicMock(spec=CoverageMetrics)
    summary.metrics.statement_coverage = 85.0
    summary.metrics.branch_coverage = 80.0
    
    policy = MagicMock(spec=CoveragePolicy)
    policy.policy_id = "p1"
    policy.min_statement_coverage = 80.0
    policy.min_branch_coverage = 75.0
    
    report = MagicMock(spec=CoverageReport)
    report.workspace_id = "ws_1"
    report.summary = summary
    report.policy = policy
    report.targets = []
    return report


@pytest.fixture
def mock_failure_report():
    report = MagicMock(spec=FailureAnalysisReport)
    report.workspace_id = "ws_1"
    report.failed_suites_count = 0
    report.severity = FailureSeverity.LOW
    report.confidence = FailureConfidence.CERTAIN
    return report


def test_validation_gate_evaluators(mock_exec_summary, mock_coverage_report, mock_failure_report):
    service = LocalValidationService(memory_service=MagicMock())
    
    # 1. Success case: All gates pass
    report = service.synthesize_validation("ws_1", mock_exec_summary, mock_coverage_report, mock_failure_report)
    assert report.summary.overall_status == ValidationStatus.PASS
    assert report.summary.decision == ValidationDecision.APPROVED
    assert len(report.gates) == 3
    
    # 2. Coverage deficit: Triggers warning status
    mock_coverage_report.summary.overall_coverage_pct = 70.0 # Policy min is 80.0
    report_warn = service.synthesize_validation("ws_1", mock_exec_summary, mock_coverage_report, mock_failure_report)
    assert report_warn.summary.overall_status == ValidationStatus.WARNING
    assert report_warn.summary.decision == ValidationDecision.MANUAL_REVIEW


def test_weighted_scoring_model(mock_exec_summary, mock_coverage_report, mock_failure_report):
    service = LocalValidationService(memory_service=MagicMock())
    
    # Full pass
    report = service.synthesize_validation("ws_1", mock_exec_summary, mock_coverage_report, mock_failure_report)
    assert report.metrics.overall_score == 100.0

    # Deficit coverage & failing tests
    mock_exec_summary.total_passed = 8
    mock_exec_summary.total_failed = 2 # 20% fail
    mock_coverage_report.summary.overall_coverage_pct = 75.0 # Deficit of 5.0 (policy is 80)
    
    report_low = service.synthesize_validation("ws_1", mock_exec_summary, mock_coverage_report, mock_failure_report)
    assert report_low.metrics.overall_score < 100.0
    assert report_low.metrics.overall_score > 0.0


def test_overall_decision_states(mock_exec_summary, mock_coverage_report, mock_failure_report):
    service = LocalValidationService(memory_service=MagicMock())
    
    # Rejected if tests fail
    mock_exec_summary.total_failed = 1
    report = service.synthesize_validation("ws_1", mock_exec_summary, mock_coverage_report, mock_failure_report)
    assert report.summary.overall_status == ValidationStatus.FAIL
    assert report.summary.decision == ValidationDecision.REJECTED


def test_service_evaluation_flow(mock_exec_summary, mock_coverage_report, mock_failure_report):
    mock_model = MagicMock(spec=ModelService)
    mock_memory = MagicMock(spec=MemoryService)
    mock_kh = MagicMock(spec=KnowledgeHubService)
    
    # Mock LLM response
    mock_response = MagicMock(spec=LLMResponse)
    mock_response.content = "{\n  \"decision\": \"manual_review\",\n  \"executive_summary\": \"Refined manual review summary.\"\n}"
    mock_model.execute_request.return_value = mock_response

    service = LocalValidationService(
        memory_service=mock_memory,
        knowledge_hub=mock_kh,
        model_service=mock_model
    )
    service.initialize()
    
    report = service.synthesize_validation("ws_1", mock_exec_summary, mock_coverage_report, mock_failure_report)
    
    # Refined decision
    assert report.summary.decision == ValidationDecision.MANUAL_REVIEW
    assert report.executive_summary == "Refined manual review summary."
    
    # Store
    service.store_validation_report(report)
    mock_memory.add_memory.assert_called_once()
    
    # Publish
    service.publish_validation_report(report)
    mock_kh.sync_document.assert_called_once()


def test_backward_compatibility():
    class CustomService(LocalValidationService):
        def synthesize_validation(self, workspace_id, execution_summary, coverage_report, failure_report):
            report = super().synthesize_validation(workspace_id, execution_summary, coverage_report, failure_report)
            report.executive_summary = "Custom summary."
            return report
            
    service = CustomService(memory_service=MagicMock())
    report = service.synthesize_validation("ws_1", MagicMock(), MagicMock(), MagicMock())
    assert report.executive_summary == "Custom summary."
