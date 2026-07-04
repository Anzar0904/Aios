import pytest
from unittest.mock import MagicMock

from aios.services.workspace_intelligence import CodeStructureSummary
from aios.services.model import ModelService, LLMResponse
from aios.services.memory import MemoryService
from aios.services.knowledge_hub import KnowledgeHubService
from aios.services.test_execution import ExecutionSummary, ExecutionResult, ExecutionTarget, ExecutionMetrics
from aios.services.test_failure import FailureSeverity, FailureConfidence
from aios.services.test_failure_impl import (
    LocalFailureAnalyzer,
    LocalRootCauseAnalyzer,
    LocalFailureAnalysisService,
)


@pytest.fixture
def dummy_failed_summary():
    target1 = ExecutionTarget("t1", "core/src/aios/kernel.py")
    res1 = ExecutionResult(
        target=target1,
        success=False,
        exit_code=1,
        metrics=ExecutionMetrics(1, 0, 1, 0, 0.1),
        raw_output="AssertionError: Kernel failed to boot"
    )
    target2 = ExecutionTarget("t2", "core/src/aios/services/memory.py")
    res2 = ExecutionResult(
        target=target2,
        success=False,
        exit_code=1,
        metrics=ExecutionMetrics(1, 0, 1, 0, 0.1),
        raw_output="ImportError: No module named memory"
    )
    return ExecutionSummary(
        summary_id="s1",
        workspace_id="ws_1",
        overall_success=False,
        total_duration=0.2,
        total_passed=0,
        total_failed=2,
        total_skipped=0,
        results=[res1, res2],
        timestamp=0.0
    )


def test_failure_analyzer_classification():
    analyzer = LocalFailureAnalyzer()
    
    assert analyzer.classify_failure("AssertionError: custom msg").pattern_name == "assertion_failure"
    assert analyzer.classify_failure("ModuleNotFoundError: No module").pattern_name == "import_failure"
    assert analyzer.classify_failure("SyntaxError: invalid syntax").pattern_name == "syntax_failure"
    assert analyzer.classify_failure("TimeoutExpired").pattern_name == "timeout"
    assert analyzer.classify_failure("some runtime exception").pattern_name == "runtime_exception"


def test_failure_analyzer_clustering(dummy_failed_summary):
    analyzer = LocalFailureAnalyzer()
    
    signatures = [
        MagicMock(signature_id="s1", error_message="msg1", stack_trace="trace1", exception_class="AssertionError"),
        MagicMock(signature_id="s2", error_message="msg2", stack_trace="trace2", exception_class="AssertionError"),
        MagicMock(signature_id="s3", error_message="msg3", stack_trace="trace3", exception_class="ImportError")
    ]
    clusters = analyzer.cluster_failures(signatures)
    
    assert len(clusters) == 2
    # One cluster for AssertionError (2 sigs) and one for ImportError (1 sig)
    class_names = [c.signatures[0].exception_class for c in clusters]
    assert "AssertionError" in class_names
    assert "ImportError" in class_names


def test_root_cause_analysis(dummy_failed_summary):
    analyzer = LocalRootCauseAnalyzer()
    summary = CodeStructureSummary("s1", 0.0, {}, {}, {}, {}, [])
    
    rc = analyzer.analyze_root_cause(dummy_failed_summary, summary)
    assert len(rc["origin_components"]) == 2
    assert "core/src/aios/kernel.py" in rc["origin_components"]
    assert "core/src/aios/services/memory.py" in rc["origin_components"]


def test_failure_analysis_service_flow(dummy_failed_summary):
    mock_model = MagicMock(spec=ModelService)
    mock_memory = MagicMock(spec=MemoryService)
    mock_kh = MagicMock(spec=KnowledgeHubService)
    
    # Mock LLM Refinement Response
    mock_response = MagicMock(spec=LLMResponse)
    mock_response.content = "{\n  \"severity\": \"Critical\",\n  \"confidence\": \"Certain\",\n  \"refined_recommendation\": \"Refined manual review recommendation.\"\n}"
    mock_model.execute_request.return_value = mock_response

    service = LocalFailureAnalysisService(
        memory_service=mock_memory,
        knowledge_hub=mock_kh,
        model_service=mock_model
    )
    service.initialize()
    
    summary = CodeStructureSummary("s1", 0.0, {}, {}, {}, {}, [])
    report = service.diagnose_failures(
        workspace_id="ws_1",
        execution_summary=dummy_failed_summary,
        code_summary=summary
    )
    
    # Verify LLM refined fields merged
    assert report.severity == FailureSeverity.CRITICAL
    assert report.confidence == FailureConfidence.CERTAIN
    assert len(report.recommendations) == 3 # 2 rules + 1 LLM refinement
    
    # Store
    service.store_failure_report(report)
    mock_memory.add_memory.assert_called_once()
    
    # Publish
    service.publish_failure_report(report)
    mock_kh.sync_document.assert_called_once()


def test_backward_compatibility():
    class CustomAnalyzer(LocalFailureAnalyzer):
        def classify_failure(self, raw_output):
            pattern = super().classify_failure(raw_output)
            pattern.pattern_name = "custom_pattern"
            return pattern
            
    analyzer = CustomAnalyzer()
    assert analyzer.classify_failure("msg").pattern_name == "custom_pattern"
